# Claude Code / Codex Build Prompt

Use this when you want an AI coding agent to create a public GitHub Pages onboarding guide.

```text
You are helping me create an English GitHub Pages onboarding guide.

Topic:
<topic>

Audience:
<students, researchers, lab team, instructors>

Repository path:
<repo/path>

Requirements:
- Build a usable guide, not a marketing page.
- Start from the decision the reader must make.
- Include a compact visual explanation.
- Include a table that maps question types to data requirements, safe claims, red flags, and reviewer objections.
- Remove redundant sections, but do not remove methodological detail.
- Add 1-2 image assets only where they reduce text pressure.
- Cite primary or credible sources.
- Verify local links, anchors, rendering, and GitHub Pages readiness.

Before publishing, tell me exactly which files will be staged.
```

## Follow-up prompts

```text
Check the content itself. Use a dialectical review: thesis, likely overclaim, synthesis, missing evidence, and how a reviewer would object.
```

```text
Find the section where readers will hesitate. Strengthen that section without adding redundant explanation.
```

```text
Find 1-2 places where a visual would reduce text pressure. Generate project-bound images, insert them, compress them for the web, and verify that all local links still work.
```
