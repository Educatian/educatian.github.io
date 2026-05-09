# Learning Analytics Data Readiness Checklist

Use this checklist before treating classroom logs as research-ready learning analytics data.

## 1. Provenance

- [ ] Each source system is named.
- [ ] Export date and extraction method are documented.
- [ ] Raw files remain private and unchanged.
- [ ] A script or notebook can recreate cleaned outputs from raw inputs.

## 2. Privacy and governance

- [ ] Direct identifiers were removed from analysis copies.
- [ ] Pseudonym mapping is stored separately from public or shared data.
- [ ] Small-cell risks were checked before sharing summaries.
- [ ] Public examples are synthetic, aggregated, or approved for release.
- [ ] IRB, consent, data-use, and institutional requirements were checked.

## 3. Event grammar

- [ ] Every row has learner, time, action, object, and source fields.
- [ ] Event types use a controlled vocabulary.
- [ ] Raw platform event names are preserved separately.
- [ ] Timestamps are parseable and sorted.
- [ ] Duplicate events are detected and handled intentionally.

## 4. Analysis fit

- [ ] The dataset supports the intended research question.
- [ ] Sequence analyses preserve order.
- [ ] Knowledge tracing rows map attempts to skills or concepts.
- [ ] ONA/ENA-style analyses define meaningful codes and units.
- [ ] Predictive models use temporally honest train/test splits.

## 5. Interpretation

- [ ] Missingness and logging gaps are described.
- [ ] Platform affordances are separated from learner intent.
- [ ] Causal language is avoided unless the design supports it.
- [ ] Visualizations show sample size, uncertainty, or aggregation level where relevant.
