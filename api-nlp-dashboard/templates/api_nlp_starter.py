"""
Synthetic starter pipeline: REST/HTML collection -> normalized records -> NLP-ready JSONL.
Replace example URLs and extraction rules with your own public-safe sources.
"""

from __future__ import annotations

import datetime as dt
import hashlib
import json
from pathlib import Path
from typing import Iterable

import pandas as pd
import requests
from bs4 import BeautifulSoup


OUT = Path("data")
OUT.mkdir(exist_ok=True)


def stable_id(*parts: str) -> str:
    raw = "|".join(parts).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()[:16]


def fetch_json_api(url: str) -> list[dict]:
    response = requests.get(url, timeout=30)
    response.raise_for_status()
    payload = response.json()
    if isinstance(payload, dict) and "items" in payload:
        return payload["items"]
    if isinstance(payload, list):
        return payload
    return [payload]


def fetch_html_text(url: str) -> dict:
    response = requests.get(url, timeout=30)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")
    for tag in soup(["script", "style", "noscript"]):
        tag.decompose()
    title = soup.title.get_text(" ", strip=True) if soup.title else url
    text = " ".join(soup.get_text(" ").split())
    return {"title": title, "text": text[:12000], "source_url": url}


def normalize(records: Iterable[dict], source_id: str) -> pd.DataFrame:
    df = pd.json_normalize(list(records), sep=".")
    now = dt.datetime.now(dt.UTC).isoformat()
    if "text" not in df.columns:
        text_cols = [c for c in df.columns if c.lower() in {"body", "abstract", "description", "content"}]
        df["text"] = df[text_cols[0]] if text_cols else ""
    if "title" not in df.columns:
        df["title"] = ""
    if "source_url" not in df.columns:
        df["source_url"] = ""
    df["source_id"] = source_id
    df["collected_at"] = now
    df["record_id"] = [
        stable_id(source_id, str(row.get("source_url", "")), str(row.get("title", "")), str(i))
        for i, row in df.iterrows()
    ]
    keep = ["record_id", "collected_at", "source_id", "source_url", "title", "text"]
    return df[keep].drop_duplicates("record_id")


def simple_nlp(text: str) -> dict:
    words = [w.strip(".,:;!?()[]{}\"'").lower() for w in text.split()]
    words = [w for w in words if len(w) > 5]
    key_phrases = sorted(set(words), key=words.count, reverse=True)[:8]
    return {
        "summary": text[:240] + ("..." if len(text) > 240 else ""),
        "key_phrases": key_phrases,
        "entities": [],
        "sentiment": "unknown",
        "model_version": "simple_nlp_v0"
    }


def main() -> None:
    # Replace this with your API endpoint or HTML targets.
    html_records = [fetch_html_text("https://example.org")]
    df = normalize(html_records, "src_002")
    df["nlp"] = df["text"].map(simple_nlp)
    df.to_json(OUT / "dashboard_records.jsonl", orient="records", lines=True, force_ascii=False)
    df.drop(columns=["text"]).to_csv(OUT / "dashboard_records_preview.csv", index=False)
    print(f"Wrote {len(df)} records to {OUT}")


if __name__ == "__main__":
    main()

