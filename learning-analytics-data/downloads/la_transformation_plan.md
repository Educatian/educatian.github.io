# Learning Analytics Transformation Plan

## Project

- Project name:
- Course / platform:
- Data owner:
- Intended audience:
- Public release level: private / internal / de-identified / synthetic

## Research purpose

Write the research question in one sentence.

> Example: How do learners' help-seeking sequences differ before successful and unsuccessful practice attempts?

## Source files

| Source | File or export | Unit of raw row | Key risks |
|---|---|---|---|
| LMS clickstream |  | event | Identifiers, noisy navigation |
| Assessment export |  | attempt | Skill mapping, retries |
| Discussion export |  | post | Raw text, names |

## Target event grammar

Each analysis-ready event should answer:

1. Who acted?
2. When did it happen?
3. What action occurred?
4. What object was acted on?
5. What learning context makes the event interpretable?

## Transformation steps

1. Preserve raw files.
2. Remove direct identifiers from working copy.
3. Parse timestamps and normalize timezone.
4. Map platform-specific actions to controlled event types.
5. Attach object metadata and activity context.
6. Remove duplicates or document why they remain.
7. Create analysis-specific tables for sequence mining, ONA/ENA, KT, or prediction.
8. Save a metadata file describing every derived field.

## Reviewer-risk notes

- What logging gaps could affect interpretation?
- What behavior might the platform record poorly?
- Which features are proxy measures rather than direct constructs?
- Which claims are descriptive, predictive, or causal?
