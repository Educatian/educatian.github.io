---
title: API to NLP Dashboard Pipeline Spec
status: draft
owner: <name>
updated: <YYYY-MM-DD>
---

# Pipeline Spec

## 1. Dashboard question

What decision should this dashboard support?

- Primary user:
- Refresh cadence:
- Unit of analysis:
- Minimum viable insight:

## 2. Source registry

| source_id | source_name | access_method | auth | refresh | owner | notes |
|---|---|---|---|---|---|---|
| src_001 | Example public API | REST JSON | none | daily | <name> | synthetic placeholder |

## 3. Data contract

| field | type | required | example | notes |
|---|---|---:|---|---|
| record_id | string | yes | ex_001 | stable unique key |
| collected_at | datetime | yes | 2026-05-07T12:00:00Z | ingestion timestamp |
| source_url | string | no | https://example.org/item/1 | public link only |
| text | string | yes | "Example text..." | raw text for NLP |

## 4. NLP outputs

| output | method | confidence | dashboard use |
|---|---|---|---|
| sentiment_label | lexicon/model/LLM | optional | trend filter |
| key_phrases | spaCy/LLM | optional | topic cards |
| entity_list | spaCy/LLM | optional | network or table |
| summary | LLM structured output | recommended | record preview |

## 5. Quality checks

- API status codes logged.
- JSON schema validation before storage.
- Duplicates removed by stable key.
- Empty or boilerplate text filtered.
- NLP model/prompt version stored with outputs.
- Dashboard never recomputes expensive NLP in the browser.

## 6. Privacy boundary

Write what must never leave local/private storage:

- No secrets in repo.
- No private user text in public static pages.
- Store only derived, review-safe fields in public dashboard exports.

