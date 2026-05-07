"""
Generate a synthetic API -> NLP dashboard case study.

Outputs:
  simulations/dashboard_records_simulated.jsonl
  simulations/source_health.csv
  simulations/validation_report.json
  simulations/validation_report.md
  simulations/case-study-summary.md

Run from the api-nlp-dashboard folder:
  python templates/simulate_dashboard_case.py
"""

from __future__ import annotations

import csv
import json
import random
from collections import Counter, defaultdict
from datetime import datetime, timedelta, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "simulations"
SEED = 20260507
N_RECORDS = 120

SOURCES = [
    {
        "source_id": "grant_feed",
        "name": "Grant announcement feed",
        "base_priority": 0.34,
        "freshness_hours": 5,
        "error_count": 0,
    },
    {
        "source_id": "paper_search",
        "name": "Research paper search",
        "base_priority": 0.18,
        "freshness_hours": 11,
        "error_count": 1,
    },
    {
        "source_id": "policy_monitor",
        "name": "Public policy monitor",
        "base_priority": 0.46,
        "freshness_hours": 3,
        "error_count": 2,
    },
    {
        "source_id": "feedback_pulse",
        "name": "Open-ended feedback pulse",
        "base_priority": 0.25,
        "freshness_hours": 19,
        "error_count": 0,
    },
]

TOPICS = [
    ("governance", ["privacy", "retention", "human review", "source permission"]),
    ("funding", ["deadline", "eligibility", "planning grant", "budget"]),
    ("student feedback", ["course feedback", "urgency", "triage", "theme"]),
    ("learning analytics", ["advising", "dashboard", "intervention", "retention"]),
    ("NLP", ["summary", "classification", "entity extraction", "confidence"]),
]

REVIEW_REASONS = {
    "high": [
        "Deadline or policy impact requires human review.",
        "High relevance and strong source match.",
        "Potential operational action item.",
    ],
    "medium": [
        "Useful benchmark, but not urgent.",
        "Relevant signal with moderate confidence.",
        "Worth grouping into topic trend review.",
    ],
    "low": [
        "Background item with low immediate action value.",
        "Useful for archive, not review queue.",
        "Weak match to current dashboard question.",
    ],
}


def choose_priority(rng: random.Random, source: dict[str, object], confidence: float) -> str:
    p = float(source["base_priority"])
    if confidence < 0.62:
        p += 0.18
    roll = rng.random()
    if roll < p:
        return "high"
    if roll < p + 0.34:
        return "medium"
    return "low"


def make_record(rng: random.Random, idx: int, now: datetime) -> dict[str, object]:
    source = rng.choice(SOURCES)
    topic, phrases = rng.choice(TOPICS)
    phrase_sample = rng.sample(phrases, k=2)
    days_ago = rng.randint(0, 29)
    collected_at = now - timedelta(days=days_ago, hours=rng.randint(0, 23))
    confidence = round(rng.uniform(0.52, 0.97), 2)
    priority = choose_priority(rng, source, confidence)
    review_state = "needs_review" if priority == "high" or confidence < 0.64 else rng.choice(["new", "reviewed"])
    title = f"{topic.title()} update #{idx:03d}"
    text = (
        f"Synthetic public record about {topic}. It mentions {phrase_sample[0]} and "
        f"{phrase_sample[1]} as signals for an API-to-NLP dashboard workflow."
    )
    return {
        "record_id": f"{source['source_id']}-{idx:03d}",
        "collected_at": collected_at.replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "source_id": source["source_id"],
        "source_url": f"https://example.org/{source['source_id']}/{idx:03d}",
        "title": title,
        "text": text,
        "review_state": review_state,
        "nlp": {
            "summary": f"{topic.title()} item related to {phrase_sample[0]} and {phrase_sample[1]}.",
            "topic_labels": [topic],
            "key_phrases": phrase_sample,
            "entities": [
                {"text": phrase_sample[0], "label": "CONCEPT"},
                {"text": source["name"], "label": "SOURCE"},
            ],
            "sentiment": rng.choice(["neutral", "mixed", "positive"]),
            "priority": priority,
            "confidence": confidence,
            "review_reason": rng.choice(REVIEW_REASONS[priority]),
            "model_version": "simulation-nlp-v1",
        },
    }


def validate(records: list[dict[str, object]]) -> dict[str, object]:
    required = {"record_id", "collected_at", "source_id", "source_url", "title", "text", "review_state", "nlp"}
    nlp_required = {"summary", "topic_labels", "key_phrases", "entities", "priority", "confidence", "review_reason", "model_version"}
    ids = [str(r.get("record_id")) for r in records]
    errors: list[str] = []
    for i, record in enumerate(records):
        missing = sorted(required - set(record))
        if missing:
            errors.append(f"record {i} missing fields: {missing}")
        nlp = record.get("nlp", {})
        if not isinstance(nlp, dict):
            errors.append(f"record {i} nlp is not an object")
            continue
        nlp_missing = sorted(nlp_required - set(nlp))
        if nlp_missing:
            errors.append(f"record {i} missing nlp fields: {nlp_missing}")
        confidence = nlp.get("confidence")
        if not isinstance(confidence, (int, float)) or confidence < 0 or confidence > 1:
            errors.append(f"record {i} confidence out of range")
    duplicate_count = len(ids) - len(set(ids))
    if duplicate_count:
        errors.append(f"duplicate record_id count: {duplicate_count}")

    priority = Counter(str(r["nlp"]["priority"]) for r in records)
    review = Counter(str(r["review_state"]) for r in records)
    sources = Counter(str(r["source_id"]) for r in records)
    topics = Counter(str(r["nlp"]["topic_labels"][0]) for r in records)
    confidence_values = [float(r["nlp"]["confidence"]) for r in records]
    low_confidence = sum(1 for value in confidence_values if value < 0.65)
    high_priority_review = sum(
        1 for r in records if r["nlp"]["priority"] == "high" and r["review_state"] == "needs_review"
    )
    return {
        "record_count": len(records),
        "schema_error_count": len(errors),
        "schema_errors": errors[:20],
        "duplicate_count": duplicate_count,
        "priority_counts": dict(priority),
        "review_state_counts": dict(review),
        "source_counts": dict(sources),
        "topic_counts": dict(topics),
        "low_confidence_count": low_confidence,
        "avg_confidence": round(sum(confidence_values) / len(confidence_values), 3),
        "high_priority_review_count": high_priority_review,
    }


def write_outputs(records: list[dict[str, object]], report: dict[str, object], now: datetime) -> None:
    OUT_DIR.mkdir(exist_ok=True)
    records_path = OUT_DIR / "dashboard_records_simulated.jsonl"
    records_path.write_text(
        "\n".join(json.dumps(r, ensure_ascii=False) for r in records) + "\n",
        encoding="utf-8",
    )

    with (OUT_DIR / "source_health.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["source_id", "source_name", "records", "last_success_at", "error_count", "avg_confidence"],
        )
        writer.writeheader()
        by_source: dict[str, list[dict[str, object]]] = defaultdict(list)
        for record in records:
            by_source[str(record["source_id"])].append(record)
        source_meta = {str(s["source_id"]): s for s in SOURCES}
        for source_id, items in sorted(by_source.items()):
            meta = source_meta[source_id]
            avg_conf = sum(float(r["nlp"]["confidence"]) for r in items) / len(items)
            last_success = now - timedelta(hours=int(meta["freshness_hours"]))
            writer.writerow(
                {
                    "source_id": source_id,
                    "source_name": meta["name"],
                    "records": len(items),
                    "last_success_at": last_success.replace(microsecond=0).isoformat().replace("+00:00", "Z"),
                    "error_count": meta["error_count"],
                    "avg_confidence": f"{avg_conf:.3f}",
                }
            )

    (OUT_DIR / "validation_report.json").write_text(
        json.dumps(report, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    report_md = f"""# Simulation Validation Report

Generated: {now.isoformat().replace("+00:00", "Z")}

## Dataset

- Records: {report["record_count"]}
- Schema errors: {report["schema_error_count"]}
- Duplicate IDs: {report["duplicate_count"]}
- Average NLP confidence: {report["avg_confidence"]}
- Low-confidence records: {report["low_confidence_count"]}
- High-priority records already routed to review: {report["high_priority_review_count"]}

## Priority Mix

{json.dumps(report["priority_counts"], indent=2, ensure_ascii=False)}

## Review State Mix

{json.dumps(report["review_state_counts"], indent=2, ensure_ascii=False)}

## Source Counts

{json.dumps(report["source_counts"], indent=2, ensure_ascii=False)}

## Topic Counts

{json.dumps(report["topic_counts"], indent=2, ensure_ascii=False)}

## Interpretation

The simulated dashboard is ready for a first case-study pass if schema errors and duplicate IDs are both zero.
The main review queue should focus on high-priority records and low-confidence records because those are the
items most likely to affect user decisions or require human judgment.
"""
    (OUT_DIR / "validation_report.md").write_text(report_md, encoding="utf-8")

    summary_md = f"""# Case Study Summary

Scenario: a public policy, grant, paper, and feedback monitor that turns web/API records into an NLP review dashboard.

The simulated run produced {report["record_count"]} dashboard records across {len(report["source_counts"])} sources.
The quality gate found {report["schema_error_count"]} schema errors and {report["duplicate_count"]} duplicate IDs.
The dashboard should open with {report["high_priority_review_count"]} high-priority review items and
{report["low_confidence_count"]} low-confidence records visible for human checking.

Recommended dashboard story:
1. Start at source health to confirm the feed is fresh.
2. Open overview to inspect record volume, priority mix, and confidence distribution.
3. Use the review queue to process high-priority and low-confidence records first.
4. Use topic filters to compare governance, funding, feedback, learning analytics, and NLP themes.
5. Export reviewed records only after review_state has been updated.
"""
    (OUT_DIR / "case-study-summary.md").write_text(summary_md, encoding="utf-8")


def main() -> None:
    rng = random.Random(SEED)
    now = datetime(2026, 5, 7, 14, 0, tzinfo=timezone.utc)
    records = [make_record(rng, i + 1, now) for i in range(N_RECORDS)]
    report = validate(records)
    write_outputs(records, report, now)
    print(json.dumps(report, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
