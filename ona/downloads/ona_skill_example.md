---
name: ona
description: Use when the user asks for an Ordered Network Analysis figure / ONA 시각화 / chapter Fig 4 양식 / directional ground→response curved arrows. Bypasses ona's broken plot wrapper by calling ona's internal helpers (create_edge_matrix, edge_paths, to_square) directly and rendering through plotly layout$shapes + kaleido. Mirrors `~/.claude/skills/ona/SKILL.md` and `~/.claude/commands/ona.md`.
---

# ona — chapter-style Ordered Network Analysis figure (trouble-free)

**Trigger phrases (Korean + English):**
- ONA 시각화 · ONA 그림 · ONA figure · ordered network analysis · chapter Fig 4
- 도넛 노드 ONA · directional curved arrows · ground→response 곡선 화살표
- "ona 패키지로 figure 만들어" · "ONA 챕터 양식 그대로"

**Mirrors:** `C:\Users\jewoo\.claude\skills\ona\SKILL.md`, `C:\Users\jewoo\.claude\commands\ona.md`

---

## Why this skill exists

The `ona` R package's exported `nodes()` / `edges()` plot wrappers **silent-fail** under the current `ona` × `tma` × `rENA` combo on Windows: they return a plotly object with `attr(p, "edge_weights") = TRUE` but never inject any visible shape. RTools45 source compile, version pinning, and LAK24 data.table passing did not fix the wrappers. **The internals work** — call `ona:::create_edge_matrix`, `ona:::edge_paths`, and `ona:::to_square` directly, pack into `plotly::layout(shapes = ...)`, render to PNG via kaleido 1.x.

Use this skill any time the user wants an ONA mean-network visualization. Do not reinvent the wrapper.

---

## Workflow

### 1. Confirm inputs
- long-format CSV: one row per turn, integer code columns, unit column(s), speaker/mode column, numeric `turn_idx` time column
- destination dir for `<basename>.{html,json,png}`

### 2. Copy + adapt template
Copy `templates/ona_template.R` into the project. Edit only the PARAMS block:
- `ROOT`, `CSV`, `FIG_DIR`, `OUT_BASENAME`
- `CODES`, `UNIT_COLS`, `MODE_COL`, `TIME_COL`, `WINDOW_SIZE`
- `GROUP_COL` + `G1`/`G2` for two-color split, or `NULL` for single-network

Defaults (do not change unless asked):
- HOO: `tma:::rules(user_id %in% UNIT$user_id & cond %in% UNIT$cond)` (single rule)
- `direction = 1`, `sender_direction = 1`, `edge_arrow_direction = 2`
- `edge_size_multiplier = 0.4`, `scale_edges_to = c(0, 1.5)`, line width × 2.5
- node sizes: `12 + 34 * (in_strength / max_in_strength)` from `colSums(ona:::to_square(weights))`
- donut nodes: black outer + white inner with label, `sizemode = "diameter"`
- shapes: `layer = "below"`

### 3. Run R + render
```pwsh
pwsh templates/run_ona.ps1 -RScript path\to\ona_run.R `
    -OutDir path\to\figures -OutBaseName <basename>
```

The driver auto-detects Rscript, ensures kaleido+plotly, runs R, renders PNG.

Rscript path must be absolute (`C:\Program Files\R\R-4.5.2\bin\Rscript.exe`). Use kaleido 1.x (`kaleido.write_fig_sync`); never downgrade to 0.2.1.

### 4. Inspect + iterate
Open the PNG. Common knobs: `edge_size_multiplier`, `scale_edges_to[2]`, `EDGE_LINE_MULT`, `LABEL_FONT_PX`, `DONUT_INNER_RATIO`, axis range.

---

## Files in this skill

| File | Purpose |
|---|---|
| `SKILL.md` | this dispatch doc |
| `GUIDE.html` | beginner-friendly setup walkthrough (open-design blueprint aesthetic, English) |
| `templates/ona_template.R` | combined-network ONA pipeline |
| `templates/ona_panels_template.R` | side-by-side per-group panels with shared scales |
| `templates/render_ona_kaleido.py` | kaleido 1.x PNG renderer |
| `templates/run_ona.ps1` | one-shot driver (env detect + R + kaleido) |

### Picking layout
- **Combined** — overlay both groups' edges on one plot.
- **Panels** — two plots side-by-side; same node positions, same `scale_edges_from = c(0, max(c(w1,w2)))`, same `in_strength_total` for node sizes. Use when user asks "각 그룹별로 / side-by-side / 패널 / 두개의 그래프."

---

## Pitfalls

1. data.frame `[df$col=="X",]` strips `ena.line.weights` class. Template extracts numeric matrix via `as.matrix` + `colMeans`. Do not "simplify".
2. `ona::nodes()` / `ona::edges()` are silent NO-OPs. Template never calls them.
3. Two-rule (ground, response) HOO crashes most real datasets. Use the single-rule pattern.
4. kaleido 0.2.1 hangs on Windows. Always 1.x.
5. Missing edges = `layer = "below"` was dropped or `sizemode != "diameter"`.
6. No edges at all = HOO rule excluded all turns. Print `nrow(flat)` + `range(weights)` first.
