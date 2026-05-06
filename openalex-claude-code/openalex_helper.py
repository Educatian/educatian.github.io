"""
openalex_helper.py
==================
OpenAlex API helper for Claude Code workflows.
Pattern B from the OpenAlex × Claude Code guidebook (2026-05-05).

No API token needed. Email goes in `mailto` for the polite pool.

Usage from Claude Code prompts:
    python openalex_helper.py search "AI literacy K-12" --year-min 2023 --min-citations 50
    python openalex_helper.py paginate works "primary_location.source.id:S206377884" --out data/jls.jsonl
    python openalex_helper.py cited-by 10.1080/10508406.2020.1782269
"""

from __future__ import annotations
import argparse
import json
import sys
import time
from pathlib import Path
from typing import Iterator
import urllib.parse
import urllib.request

BASE = "https://api.openalex.org"
EMAIL = "jewoong.moon@gmail.com"          # polite pool — change to your email
DEFAULT_PER_PAGE = 200                    # OpenAlex max
SLEEP_BETWEEN_CALLS = 0.1                 # 10 req/sec safe margin


def _get(endpoint: str, params: dict) -> dict:
    """GET wrapper with polite-pool email + light error handling."""
    params = {**params, "mailto": EMAIL}
    qs = urllib.parse.urlencode(params, safe=":,>")
    url = f"{BASE}/{endpoint}?{qs}"
    req = urllib.request.Request(url, headers={"User-Agent": f"openalex-helper/0.1 ({EMAIL})"})
    for attempt in range(4):
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                return json.loads(r.read())
        except urllib.error.HTTPError as e:
            if e.code == 429 and attempt < 3:
                wait = 2 ** attempt
                print(f"[rate-limited] retry in {wait}s", file=sys.stderr)
                time.sleep(wait)
                continue
            raise


def search_works(query: str, year_min: int | None = None,
                 min_citations: int | None = None,
                 per_page: int = 25) -> dict:
    """Full-text search for works, ranked by citation count."""
    filters = []
    if year_min:
        filters.append(f"publication_year:>{year_min - 1}")
    if min_citations:
        filters.append(f"cited_by_count:>{min_citations - 1}")
    params = {"search": query, "per-page": per_page,
              "sort": "cited_by_count:desc"}
    if filters:
        params["filter"] = ",".join(filters)
    return _get("works", params)


def paginate(endpoint: str, filter_str: str,
             max_results: int = 100_000,
             select: str | None = None) -> Iterator[dict]:
    """Cursor-based pagination — safe for >10K results.

    Yields work dicts one at a time so the caller can stream-write.
    """
    cursor = "*"
    pulled = 0
    while cursor and pulled < max_results:
        params = {"filter": filter_str, "per-page": DEFAULT_PER_PAGE, "cursor": cursor}
        if select:
            params["select"] = select
        r = _get(endpoint, params)
        for item in r["results"]:
            yield item
            pulled += 1
            if pulled >= max_results:
                return
        cursor = r["meta"].get("next_cursor")
        time.sleep(SLEEP_BETWEEN_CALLS)


def get_work(work_id_or_doi: str) -> dict:
    """Single work by OpenAlex ID (W...) or DOI (doi:10.x/...)."""
    if work_id_or_doi.startswith("10."):
        work_id_or_doi = f"doi:{work_id_or_doi}"
    return _get(f"works/{work_id_or_doi}", {})


def cited_by(work_id_or_doi: str, max_results: int = 1000) -> list[dict]:
    """Papers that cite this work (uses cited_by_api_url internally)."""
    work = get_work(work_id_or_doi)
    target_id = work["id"].split("/")[-1]   # e.g., W2741809807
    return list(paginate("works", f"cites:{target_id}", max_results=max_results))


def references_of(work_id_or_doi: str) -> list[str]:
    """Papers that this work cites (just the OpenAlex IDs)."""
    work = get_work(work_id_or_doi)
    return work.get("referenced_works", [])


def get_author(orcid_or_id: str) -> dict:
    """Author lookup by ORCID (0000-...) or OpenAlex ID (A...)."""
    if "-" in orcid_or_id and len(orcid_or_id) == 19:
        orcid_or_id = f"orcid:{orcid_or_id}"
    return _get(f"authors/{orcid_or_id}", {})


def author_works(author_id: str, year_min: int | None = None,
                 max_results: int = 10_000) -> list[dict]:
    """All works by an author."""
    aid = author_id.split("/")[-1] if "/" in author_id else author_id
    f = f"author.id:{aid}"
    if year_min:
        f += f",publication_year:>{year_min - 1}"
    return list(paginate("works", f, max_results=max_results,
                         select="id,doi,title,publication_year,cited_by_count,topics,primary_location"))


def find_source_by_issn(issn: str) -> dict | None:
    """Source (journal) lookup by ISSN."""
    r = _get("sources", {"filter": f"issn:{issn}"})
    if r.get("results"):
        return r["results"][0]
    return None


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def _cmd_search(args):
    r = search_works(args.query, args.year_min, args.min_citations, args.per_page)
    for w in r.get("results", []):
        print(json.dumps({
            "id": w["id"].split("/")[-1],
            "doi": w.get("doi"),
            "title": w["title"],
            "year": w.get("publication_year"),
            "citations": w.get("cited_by_count"),
        }, ensure_ascii=False))


def _cmd_paginate(args):
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    n = 0
    with out.open("w", encoding="utf-8") as f:
        for w in paginate(args.endpoint, args.filter, max_results=args.max,
                          select=args.select):
            f.write(json.dumps(w, ensure_ascii=False) + "\n")
            n += 1
            if n % 500 == 0:
                print(f"  ...{n} written", file=sys.stderr)
    print(f"[done] {n} records → {out}", file=sys.stderr)


def _cmd_cited_by(args):
    for w in cited_by(args.work, max_results=args.max):
        print(json.dumps({
            "id": w["id"].split("/")[-1],
            "doi": w.get("doi"),
            "title": w["title"],
            "year": w.get("publication_year"),
            "citations": w.get("cited_by_count"),
        }, ensure_ascii=False))


def _cmd_author_works(args):
    for w in author_works(args.author, args.year_min, args.max):
        print(json.dumps({
            "id": w["id"].split("/")[-1],
            "title": w["title"],
            "year": w.get("publication_year"),
            "citations": w.get("cited_by_count"),
        }, ensure_ascii=False))


def main():
    p = argparse.ArgumentParser(description="OpenAlex helper for Claude Code")
    sub = p.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("search", help="Full-text search works")
    s.add_argument("query")
    s.add_argument("--year-min", type=int)
    s.add_argument("--min-citations", type=int)
    s.add_argument("--per-page", type=int, default=25)
    s.set_defaults(func=_cmd_search)

    pg = sub.add_parser("paginate", help="Cursor-paginate filtered endpoint")
    pg.add_argument("endpoint", choices=["works", "authors", "sources",
                                         "institutions", "topics", "funders", "publishers"])
    pg.add_argument("filter", help="OpenAlex filter string, e.g., 'publication_year:2024'")
    pg.add_argument("--out", required=True, help="Output JSONL path")
    pg.add_argument("--max", type=int, default=100_000)
    pg.add_argument("--select", help="Comma-separated fields to keep")
    pg.set_defaults(func=_cmd_paginate)

    cb = sub.add_parser("cited-by", help="Papers citing the given work")
    cb.add_argument("work", help="OpenAlex Work ID or DOI")
    cb.add_argument("--max", type=int, default=1000)
    cb.set_defaults(func=_cmd_cited_by)

    aw = sub.add_parser("author-works", help="All works by author")
    aw.add_argument("author", help="ORCID or OpenAlex Author ID")
    aw.add_argument("--year-min", type=int)
    aw.add_argument("--max", type=int, default=10_000)
    aw.set_defaults(func=_cmd_author_works)

    args = p.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
