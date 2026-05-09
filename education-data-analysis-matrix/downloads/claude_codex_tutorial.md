# Claude Code / Codex Tutorial: Build an Education Data x Analysis Guide

Use this as a conversation recipe for creating a GitHub Pages guide that maps education and learning-sciences data types to analysis methods, claim limits, validity checks, and interactive visualizations.

## Topic video primers

These videos are about the guide topic itself, not about Claude Code or Codex:

- Learning analytics in a nutshell, SoLAR: https://youtu.be/XscUZ8dIa-8
- Educational Data Mining (EDM): Turning Big Data into Big Gains for Students: https://www.youtube.com/watch?v=mEWBdf1dvdw
- LASI14 panel: Learning Analytics and Learning Science, SoLAR: https://youtu.be/gR7FKMzzbOc

## 1. Start with a research brief

```text
I want to create an English GitHub Pages guide in my existing Educatian style.

Topic: all data types used in educational technology and learning sciences, and the research methods used to analyze them.

First, make a plan and research the literature before writing code. Define the audience, scope, data families, analysis families, claim verbs, reviewer risks, downloads, references, and page structure. Use checked sources and remove any citation you cannot verify.
```

Expected output:

- Guide outline
- Data families
- Analysis families
- Claim verbs
- Validity risks
- Reference plan

Quality check:

- Does the plan separate observed data from inferred constructs?
- Does it avoid treating method choice as a statistics menu?

## 2. Build the matrix logic

```text
Build the core matrix around these columns:

1. Data type
2. Raw forms available
3. Unit of analysis
4. What the data can show
5. Analysis families that fit
6. Supported claim verbs
7. Common overclaim to avoid
8. Minimum validity checks
9. Example research genre
10. Extra evidence needed for stronger claims

Make the guide warn readers when a claim or method needs extra evidence.
```

Expected output:

- Interactive selector
- Data type atlas
- Downloadable CSV matrix

Quality check:

- Unsupported causal, measurement, prediction, or generalization claims should be flagged directly.

## 3. Add interactive visualization ideas

```text
Add more playful interactive visualization ideas that help readers see data-to-method-to-claim relationships.

Include at least four patterns:

- Evidence river
- Reviewer-risk radar
- Method constellation
- Sequence storyboard

For each, explain best use, interaction, reviewer value, and risk.
```

Expected output:

- Button-driven visualization studio
- Inline conceptual SVGs
- Clear interpretation rules

Quality check:

- Each visual should teach a methods decision, not merely decorate the page.

## 4. Add the conversation tutorial

```text
Include a tutorial showing how a researcher or student can make this kind of guide through Claude Code or Codex conversation.

Use a dialogue format:

- What I ask
- What the agent should do
- Expected output
- Quality check
- Next prompt
```

Expected output:

- Tutorial section in the page
- Downloadable Markdown tutorial

Quality check:

- A student should be able to copy the prompts and reproduce the guide safely.

## 5. Verify and publish

```text
Test the page, make sure JavaScript works, inspect the rendered DOM, check downloads and links, commit the scoped files, push to GitHub Pages, and report the public URL and commit hash.
```

Expected output:

- Passing JavaScript syntax check
- Rendered DOM includes the new section
- Commit hash
- Public GitHub Pages URL

Quality check:

- Do not commit unrelated dirty files.
- Do not overwrite unresolved user changes.
- Report any test that could not be run.

## Reusable safety prompt

```text
Do not invent missing data or sources. Separate observed behavior from inferred constructs. If a claim is not supported by the available data or design, say so directly and suggest safer wording.
```
