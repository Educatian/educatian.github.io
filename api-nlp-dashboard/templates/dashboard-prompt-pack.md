# Claude Code / Codex Prompt Pack

Use these prompts in order. Replace bracketed placeholders with your own API, source, or dashboard question.

## 1. Define the dashboard question

```text
You are helping me build an API-to-NLP dashboard.

Dashboard question:
[Write the decision the dashboard should support.]

Turn this into:
1. primary user
2. dashboard decision
3. required source fields
4. required NLP outputs
5. dashboard panels
6. review states
7. risks and assumptions

Do not write code yet. Produce a concise implementation brief.
```

## 2. Inspect an API response

```text
Here is a sample API response:
```json
[Paste sample JSON here]
```

Infer a dashboard-ready data contract.
Return:
1. normalized fields
2. field types
3. missing-value rules
4. stable record_id strategy
5. pagination notes
6. deduplication logic
7. JSON Schema for dashboard_records.jsonl

Keep raw fields separate from normalized fields.
```

## 3. Build source registry

```text
Create a source_registry.csv row for this source.

Include:
- source_id
- source_name
- base_url
- access_method
- auth_type
- rate_limit
- refresh_cadence
- unit_of_analysis
- public_safe
- owner
- known risks
```

## 4. Create collector and normalizer

```text
Write a Python collector and normalizer for this source.

Requirements:
- save raw responses under raw/YYYY-MM-DD/
- normalize to dashboard_records_raw.jsonl
- handle pagination
- log HTTP status and failures
- deduplicate with stable record_id
- do not put secrets in the script
- include a dry-run mode limited to 20 records
```

## 5. Design NLP schema

```text
Design the NLP output schema for this dashboard.

The dashboard needs:
- topic filtering
- entity exploration
- summary preview
- priority review queue
- explanation of why an item was flagged

Return a JSON schema with:
summary, topic_labels, entities, sentiment_or_stance,
priority, review_reason, confidence, model_version.

Also give 5 validation checks for bad NLP outputs.
```

## 6. Generate dashboard records

```text
Using the normalized records and NLP schema, generate 3 synthetic dashboard_records.jsonl examples.

Each record should include:
- record_id
- source_id
- source_url
- title
- text_excerpt
- collected_at
- nlp.summary
- nlp.topic_labels
- nlp.entities
- nlp.priority
- nlp.review_reason
- nlp.confidence
- review_state

Do not use private or real sensitive data.
```

## 7. Build dashboard UI

```text
Using dashboard_records.jsonl, implement a Streamlit dashboard with:
1. Overview
2. Records
3. Review Queue
4. Source Health

For each page include:
- fields used
- filters
- charts/tables
- empty state
- error state
- user actions

The dashboard must not call APIs or run expensive NLP live.
It should only read prepared JSONL/CSV outputs.
```

## 8. QA and iteration

```text
Review the dashboard implementation.

Check:
- no horizontal overflow on mobile
- all files load if dashboard_records.jsonl is missing or empty
- filters do not crash on missing fields
- low-confidence NLP outputs are visible
- source freshness is visible
- review queue sorts correctly
- no secrets or private text are committed

Return findings first, then fixes.
```

