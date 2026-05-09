# Agent Conversation Script

Use this script with Claude Code or Codex when creating a public GitHub Pages guide in the same style as the Educatian open guides.

## 1. Orient to the Existing Site

```text
Inspect my GitHub Pages repository and summarize the existing guide style. Do not edit yet.

Focus on:
- page structure
- typography and color system
- card, table, and diagram patterns
- thumbnail conventions
- homepage linking pattern
- files that are likely safe to touch
```

## 2. Plan the Guide

```text
Create an English content plan for:

Title: From Classroom Logs to Research-Ready Learning Analytics Data
Audience: education researchers, learning analytics students, and collaborators preparing classroom platform data for analysis.

The guide should cover:
- event grammar: actor, time, action, object, context
- one general event table, then method-specific derived tables
- sequence mining, process mining, knowledge tracing, ONA/ENA, SNA, dashboards, NLP coding, prediction, causal/quasi-experimental designs, multilevel models, and cross-method comparison
- visualization guidance for each data structure
- public-safe downloads
- references to primary or official sources

Return the section map before editing.
```

## 3. Build the Page

```text
Build the guide as a self-contained GitHub Pages topic page that matches my existing guide style.

Requirements:
- create or update <topic-slug>/index.html
- include practical tables and matrices
- include visual explanations where text would be hard to scan
- use synthetic examples only
- do not include private student records, grades, emails, course rosters, or identifiable classroom artifacts
- add public-safe starter downloads
- add a thumbnail or Open Graph image
- add the homepage card if the site needs one
```

## 4. Improve Visuals

```text
Add diagrams and chart examples that show how classroom event logs become:

- sequence timelines
- Sankey or alluvial flows
- transition matrices
- ONA/ENA networks
- social networks
- knowledge tracing curves
- dashboards
- cross-method comparison views

Keep all text readable on desktop and mobile. If an inline diagram breaks, replace it with a stable image asset.
```

## 5. Fact-check

```text
Fact-check standards, method labels, privacy language, and organization names using primary or official sources where possible.

If a claim is too broad, soften it. If a reference is not authoritative enough for a public guide, replace it.
```

## 6. Verify Locally

```text
Run the page locally and verify:

- the topic URL opens
- every href resolves
- every image src resolves
- desktop layout is readable
- mobile layout is readable
- tables do not overflow badly
- diagram text does not break
- no private data appears in the page or downloads
```

## 7. Publish Narrowly

```text
Stage only the intended GitHub Pages files:

- the topic folder
- the thumbnail or assets for the topic
- starter downloads
- homepage link or card, if changed

Do not stage unrelated dirty files.
Commit with a specific message, push to the GitHub Pages branch, and confirm the public URL.
```

