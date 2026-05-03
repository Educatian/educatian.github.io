# =============================================================================
# ona_template.R — chapter-style ONA figure via ona internals + plotly shapes.
#
# This template is the ONLY working path under the current ona × tma × rENA
# combo on Windows (ona's exported plot wrapper silent-fails).
#
# Copy this file into your project, edit the PARAMS block, then run:
#   & "C:\Program Files\R\R-4.5.2\bin\Rscript.exe" path\to\this_file.R
#   python path\to\render_ona_kaleido.py <basename>.json <basename>.png
# =============================================================================

suppressPackageStartupMessages({
  library(ona); library(tma); library(plotly); library(htmlwidgets); library(magrittr)
})

# ---------------------------------------------------------------------------
# PARAMS — edit these
# ---------------------------------------------------------------------------
ROOT          <- "C:/path/to/project"           # absolute project root
CSV           <- file.path(ROOT, "turns_long.csv")
FIG_DIR       <- file.path(ROOT, "figures")
OUT_BASENAME  <- "ona_figure"                    # output: <FIG_DIR>/<OUT_BASENAME>.{html,json}

CODES         <- c("CODE_A","CODE_B","CODE_C")   # integer 0/1 columns in CSV
UNIT_COLS     <- c("group","user_id")            # row identity for ENA units
MODE_COL      <- "speaker"                        # speaker/agent identity
TIME_COL      <- "turn_idx"                       # numeric turn index
WINDOW_SIZE   <- 4                                # decay window

# Optional group split — set GROUP_COL <- NULL for a single mean network
GROUP_COL     <- "group"
G1            <- "A"        # first group label (red)
G2            <- "B"        # second group label (blue)
EDGE_COLOR_1  <- "red"
EDGE_COLOR_2  <- "blue"
EDGE_COLOR_SINGLE <- "black"  # used only when GROUP_COL is NULL

TITLE_HTML    <- paste0("<b>Ordered Network Analysis</b>")
SUBTITLE_HTML <- "Codes positioned by ONA SVD1/SVD2; curved arrows = directional ground&rarr;response"

# Visual knobs (defaults match the look user signed off on 2026-05-02) -------
EDGE_SIZE_MULT    <- 0.4
EDGE_SCALE_TO     <- c(0, 1.5)
EDGE_LINE_MULT    <- 2.5      # multiplied into shape line width
NODE_SIZE_MIN     <- 12
NODE_SIZE_RANGE   <- 34       # max = MIN + RANGE
DONUT_INNER_RATIO <- 0.55     # inner white circle radius / outer
LABEL_FONT_PX     <- 17

dir.create(FIG_DIR, showWarnings = FALSE, recursive = TRUE)

# ---------------------------------------------------------------------------
# 1. Build ONA model
# ---------------------------------------------------------------------------
long <- read.csv(CSV, stringsAsFactors = FALSE)
for (c in CODES) long[[c]] <- as.integer(long[[c]])

# Single-rule HOO. The two-rule (ground, response) chapter pattern crashes
# on most real datasets — keep this single rule.
hoo <- tma:::rules(user_id %in% UNIT$user_id & cond %in% UNIT$cond)

ctx <- tma:::contexts(long, units = UNIT_COLS, hoo_rules = hoo)
accum <- tma:::accumulate_contexts(
  ctx, codes = CODES,
  decay.function = decay(simple_window, window_size = WINDOW_SIZE),
  time.column = TIME_COL, return.ena.set = FALSE,
  mode.column = MODE_COL
)
set <- model(accum)

# ---------------------------------------------------------------------------
# 2. Per-condition (or pooled) mean weights
# ---------------------------------------------------------------------------
flat <- as.data.frame(set$line.weights)
edge_cols <- setdiff(colnames(flat),
                     c(UNIT_COLS, "ENA_UNIT", "ENA_DIRECTION"))
fmat <- as.matrix(flat[, edge_cols])
storage.mode(fmat) <- "numeric"
fmat[!is.finite(fmat)] <- 0

if (!is.null(GROUP_COL)) {
  w1 <- as.numeric(colMeans(fmat[flat[[GROUP_COL]] == G1, , drop = FALSE]))
  w2 <- as.numeric(colMeans(fmat[flat[[GROUP_COL]] == G2, , drop = FALSE]))
  weight_max <- max(c(w1, w2))
} else {
  w1 <- as.numeric(colMeans(fmat))
  w2 <- NULL
  weight_max <- max(w1)
}

nodes_dt <- data.table::copy(set$rotation$nodes)
nodes_xy <- data.frame(
  code = as.character(nodes_dt$code),
  x    = as.numeric(nodes_dt$SVD1),
  y    = as.numeric(nodes_dt$SVD2)
)

# ---------------------------------------------------------------------------
# 3. ona internals: edge geometry (Bezier paths)
# ---------------------------------------------------------------------------
make_edges <- function(weights, color) {
  em <- ona:::create_edge_matrix(NULL, weights = weights,
                                 nodes = nodes_dt, direction = 1)
  ona:::edge_paths(
    em,
    edge_color = c(color), edge_end = "outward",
    desaturate_edges_by = sqrt, lighten_edges_by = sqrt,
    edge_size_multiplier = EDGE_SIZE_MULT,
    scale_edges_to       = EDGE_SCALE_TO,
    scale_edges_from     = c(0, weight_max),
    edge_arrow = TRUE, edge_arrow_offset = 2, edge_arrow_width = 0.1,
    edge_arrow_saturation_multiplier = 1.6,
    fake_alpha = TRUE, edge_halo = 0.5,
    edge_arrows_to_show = "max", arrow_halo = 0,
    edge_halo_multiplier = 1.1,
    sender_direction = 1, edge_arrow_direction = 2
  )
}

ep1 <- make_edges(w1, if (is.null(GROUP_COL)) EDGE_COLOR_SINGLE else EDGE_COLOR_1)
ep2 <- if (!is.null(GROUP_COL)) make_edges(w2, EDGE_COLOR_2) else list()

cat("Edge paths:", length(ep1), "+", length(ep2), "\n")

# ---------------------------------------------------------------------------
# 4. Node sizes via in-strength (ona:::to_square colSums)
# ---------------------------------------------------------------------------
sq1 <- ona:::to_square(w1)
in1 <- colSums(sq1)
if (!is.null(GROUP_COL)) {
  sq2 <- ona:::to_square(w2); in2 <- colSums(sq2)
  node_total <- in1 + in2
} else {
  node_total <- in1
}
node_total[node_total == 0] <- 0.001
marker_sizes <- NODE_SIZE_MIN + NODE_SIZE_RANGE * (node_total / max(node_total))
cat("Node sizes:", paste(round(marker_sizes, 1), collapse = ", "), "\n")

# ---------------------------------------------------------------------------
# 5. Convert ona edge_paths output to layout shape specs (layer = below)
# ---------------------------------------------------------------------------
to_layout_shapes <- function(eps) {
  lapply(eps, function(s) {
    list(
      type      = "path",
      path      = s$path,
      line      = list(width = (s$line$width %||% 0.5) * EDGE_LINE_MULT,
                       color = s$line$color),
      opacity   = s$opacity %||% 1,
      fillcolor = s$fillcolor,
      xref = "x", yref = "y",
      layer = "below"
    )
  })
}
shapes_combined <- c(to_layout_shapes(ep1), to_layout_shapes(ep2))

# ---------------------------------------------------------------------------
# 6. Per-unit points + group means (only when grouped)
# ---------------------------------------------------------------------------
pts_df <- as.data.frame(set$points)

p <- plot_ly()

if (!is.null(GROUP_COL)) {
  pts1 <- pts_df[pts_df[[GROUP_COL]] == G1, ]
  pts2 <- pts_df[pts_df[[GROUP_COL]] == G2, ]
  m1 <- c(mean(pts1$SVD1), mean(pts1$SVD2))
  m2 <- c(mean(pts2$SVD1), mean(pts2$SVD2))
  ci1 <- c(qt(.975, nrow(pts1) - 1) * sd(pts1$SVD1) / sqrt(nrow(pts1)),
           qt(.975, nrow(pts1) - 1) * sd(pts1$SVD2) / sqrt(nrow(pts1)))
  ci2 <- c(qt(.975, nrow(pts2) - 1) * sd(pts2$SVD1) / sqrt(nrow(pts2)),
           qt(.975, nrow(pts2) - 1) * sd(pts2$SVD2) / sqrt(nrow(pts2)))

  p <- p |>
    add_trace(x = pts1$SVD1, y = pts1$SVD2,
              type = "scatter", mode = "markers",
              marker = list(color = EDGE_COLOR_1, size = 6, opacity = 0.5),
              name = sprintf("%s units (n=%d)", G1, nrow(pts1))) |>
    add_trace(x = pts2$SVD1, y = pts2$SVD2,
              type = "scatter", mode = "markers",
              marker = list(color = EDGE_COLOR_2, size = 6, opacity = 0.5),
              name = sprintf("%s units (n=%d)", G2, nrow(pts2))) |>
    add_trace(x = m1[1], y = m1[2],
              type = "scatter", mode = "markers",
              marker = list(color = EDGE_COLOR_1, symbol = "square", size = 14,
                            line = list(color = "black", width = 1.5)),
              error_x = list(array = ci1[1], color = EDGE_COLOR_1, thickness = 2),
              error_y = list(array = ci1[2], color = EDGE_COLOR_1, thickness = 2),
              name = sprintf("%s mean ± 95%% CI", G1)) |>
    add_trace(x = m2[1], y = m2[2],
              type = "scatter", mode = "markers",
              marker = list(color = EDGE_COLOR_2, symbol = "square", size = 14,
                            line = list(color = "black", width = 1.5)),
              error_x = list(array = ci2[1], color = EDGE_COLOR_2, thickness = 2),
              error_y = list(array = ci2[2], color = EDGE_COLOR_2, thickness = 2),
              name = sprintf("%s mean ± 95%% CI", G2))
}

# ---------------------------------------------------------------------------
# 7. Donut nodes (black ring + white inner with label)
# ---------------------------------------------------------------------------
p <- p |>
  add_trace(x = nodes_xy$x, y = nodes_xy$y,
            type = "scatter", mode = "markers",
            marker = list(color = "black", size = marker_sizes, symbol = "circle",
                          line = list(color = "black", width = 1),
                          sizemode = "diameter"),
            name = "Codes",
            hoverinfo = "skip", showlegend = TRUE, cliponaxis = FALSE) |>
  add_trace(x = nodes_xy$x, y = nodes_xy$y,
            type = "scatter", mode = "markers+text",
            marker = list(color = "white",
                          size = marker_sizes * DONUT_INNER_RATIO,
                          symbol = "circle",
                          line = list(color = "white", width = 0),
                          sizemode = "diameter"),
            text = paste0("<b>", nodes_xy$code, "</b>"),
            textposition = ifelse(nodes_xy$x >= 0, "middle right", "middle left"),
            textfont = list(size = LABEL_FONT_PX, color = "black", family = "serif"),
            name = "Codes (label)",
            hoverinfo = "text", showlegend = FALSE, cliponaxis = FALSE) |>
  layout(
    title = list(text = paste0(TITLE_HTML,
                               "<br><span style='font-size:11px'>",
                               SUBTITLE_HTML, "</span>"),
                 x = 0.05),
    xaxis = list(title = "ONA SVD1", zeroline = TRUE, zerolinecolor = "#888",
                 range = c(-2.2, 2.2)),
    yaxis = list(title = "ONA SVD2", zeroline = TRUE, zerolinecolor = "#888",
                 range = c(-1.9, 1.9), scaleanchor = "x", scaleratio = 1),
    shapes = shapes_combined,
    showlegend = TRUE,
    margin = list(t = 80, l = 60, r = 30, b = 60),
    plot_bgcolor = "white", paper_bgcolor = "white"
  )

cat("Built figure: shapes =", length(shapes_combined), "\n")

# ---------------------------------------------------------------------------
# 8. Save HTML + JSON (PNG via render_ona_kaleido.py)
# ---------------------------------------------------------------------------
htmlwidgets::saveWidget(p, file.path(FIG_DIR, paste0(OUT_BASENAME, ".html")),
                        selfcontained = TRUE)
cat("[saved]", paste0(OUT_BASENAME, ".html"), "\n")

write(plotly::plotly_json(p, jsonedit = FALSE, pretty = FALSE),
      file.path(FIG_DIR, paste0(OUT_BASENAME, ".json")))
cat("[saved]", paste0(OUT_BASENAME, ".json"), "\n")
