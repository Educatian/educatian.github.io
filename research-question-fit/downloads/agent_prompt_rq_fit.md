# Agent Prompt: Research Question Fit Audit

Paste this prompt into Claude Code, Codex, or another research assistant before running analysis.

```text
You are helping me audit research-question fit before analysis.

Project:
<brief project name and purpose>

Available data:
<list files, row units, variables, IDs, timestamps, outcome variables, intervention/comparison details, qualitative sources>

Candidate research questions:
1. <RQ1>
2. <RQ2>
3. <RQ3>

Please create a table with:
- RQ
- data/design evidence available
- claim type supported: describe, compare, associate, predict, sequence, explain, measure, evaluate, generalize, integrate
- methods that fit
- assumptions and validity threats
- claims I should avoid
- safer wording for the RQ and likely findings
- extra evidence needed if I want a stronger claim

Do not invent missing data. If the dataset cannot support a question, say so directly and propose a defensible alternative.
```

