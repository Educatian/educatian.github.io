# Case Study Summary

Scenario: a public policy, grant, paper, and feedback monitor that turns web/API records into an NLP review dashboard.

The simulated run produced 120 dashboard records across 4 sources.
The quality gate found 0 schema errors and 0 duplicate IDs.
The dashboard should open with 36 high-priority review items and
30 low-confidence records visible for human checking.

Recommended dashboard story:
1. Start at source health to confirm the feed is fresh.
2. Open overview to inspect record volume, priority mix, and confidence distribution.
3. Use the review queue to process high-priority and low-confidence records first.
4. Use topic filters to compare governance, funding, feedback, learning analytics, and NLP themes.
5. Export reviewed records only after review_state has been updated.
