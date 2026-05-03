# =============================================================================
# ona_panels_template.R — chapter-style ONA figure rendered as TWO side-by-side
# panels (one per group). Same node positions, same edge-width scale, same
# node-size scale across panels — so visual comparison is fair.
#
# Run after editing PARAMS:
#   & "C:\Program Files\R\R-4.5.2\bin\Rscript.exe" path\to\ona_panels_run.R
#   python path\to\render_ona_kaleido.py <basename>.json <basename>.png 1800 750
# =============================================================================

suppressPackageStartupMessages({
  library(ona); library(tma); library(plotly); library(htmlwidgets); library(magrittr)
})

# ---------------------------------------------------------------------------
# PARAMS
# ---------------------------------------------------------------------------
ROOT          <- "C:/path/to/project"
CSV           <- file.path(ROOT, "turns_long.csv")
FIG_DIR       <- file.path(ROOT, "figures")
OUT_BASENAME  <- "ona_panels"

CODES         <- c("CODE_A","CODE_B","CODE_C")
UNIT_COLS     <- c("group","user_id")
MODE_COL      <- "speaker"
TIME_COL      <- "turn_idx"
WINDOW_SIZE   <- 4

GROUP_COL     <- "group"
G1            <- "A"
G2            <- "B"
EDGE_COLOR_1  <- "red"
EDGE_COLOR_2  <- "blue"

TITLE_HTML    <- "<b>ONA — group panels</b>"
SUBTITLE_HTML <- "Same node positions, same edge-width scale, same node-size scale"

# Visual knobs (match the look the user signed off on 2026-05-02)
EDGE_SIZE_MULT    <- 0.4
EDGE_SCALE_TO     <- c(0, 1.5)
EDGE_LINE_MULT    <- 2.5
NODE_SIZE_MIN     <- 12
NODE_SIZE_RANGE   <- 34
DONUT_INNER_RATIO <- 0.55
LABEL_FONT_PX     <- 17

dir.create(FIG_DIR, showWarnings = FALSE, recursive = TRUE)

# ---------------------------------------------------------------------------
# 1. Build ONA model
# ---------------------------------------------------------------------------
long <- read.csv(CSV, stringsAsFactors = FALSE)
for (c in CODES) long[[c]] <- as.integer(long[[c]])

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
# 2. Per-group mean weights (shared scale)
# ---------------------------------------------------------------------------
flat <- as.data.frame(set$line.weights)
edge_cols <- setdiff(colnames(flat), c(UNIT_COLS, "ENA_UNIT", "ENA_DIRECTION"))
fmat <- as.matrix(flat[, edge_cols]); storage.mode(fmat) <- "numeric"
fmat[!is.finite(fmat)] <- 0

w1 <- as.numeric(colMeans(fmat[flat[[GROUP_COL]] == G1, , drop = FALSE]))
w2 <- as.numeric(colMeans(fmat[flat[[GROUP_COL]] == G2, , drop = FALSE]))
weight_max <- max(c(w1, w2))                # shared edge-width scale

nodes_dt <- data.table::copy(set$rotation$nodes)
nodes_xy <- data.frame(
  code = as.character(nodes_dt$code),
  x    = as.numeric(nodes_dt$SVD1),
  y    = as.numeric(nodes_dt$SVD2)
)

# ---------------------------------------------------------------------------
# 3. Edge geometry — ona internals; same scale_edges_from for both groups
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
ep1 <- make_edges(w1, EDGE_COLOR_1)
ep2 <- make_edges(w2, EDGE_COLOR_2)
cat("Edge paths: G1=", length(ep1), " G2=", length(ep2), "\n")

# ---------------------------------------------------------------------------
# 4. Node sizes — shared in-strength scale across panels
# ---------------------------------------------------------------------------
in1 <- colSums(ona:::to_square(w1))
in2 <- colSums(ona:::to_square(w2))
node_total <- in1 + in2
node_total[node_total == 0] <- 0.001
marker_sizes <- NODE_SIZE_MIN + NODE_SIZE_RANGE *
                  (node_total / max(node_total))
cat("Node sizes (shared):", paste(round(marker_sizes, 1), collapse=", "), "\n")

# ---------------------------------------------------------------------------
# 5. Convert edge_paths to layout shapes — assign to the correct subplot axes
# ---------------------------------------------------------------------------
to_layout_shapes <- function(eps, x_axis, y_axis) {
  lapply(eps, function(s) {
    list(
      type      = "path",
      path      = s$path,
      line      = list(width = (s$line$width %||% 0.5) * EDGE_LINE_MULT,
                       color = s$line$color),
      opacity   = s$opacity %||% 1,
      fillcolor = s$fillcolor,
      xref = x_axis, yref = y_axis,
      layer = "below"
    )
  })
}
shapes_panel1 <- to_layout_shapes(ep1, "x",  "y")
shapes_panel2 <- to_layout_shapes(ep2, "x2", "y2")
shapes_combined <- c(shapes_panel1, shapes_panel2)

# ---------------------------------------------------------------------------
# 6. Per-unit points + group means
# ---------------------------------------------------------------------------
pts_df <- as.data.frame(set$points)
pts1 <- pts_df[pts_df[[GROUP_COL]] == G1, ]
pts2 <- pts_df[pts_df[[GROUP_COL]] == G2, ]
m1 <- c(mean(pts1$SVD1), mean(pts1$SVD2))
m2 <- c(mean(pts2$SVD1), mean(pts2$SVD2))
ci1 <- c(qt(.975, nrow(pts1)-1) * sd(pts1$SVD1)/sqrt(nrow(pts1)),
         qt(.975, nrow(pts1)-1) * sd(pts1$SVD2)/sqrt(nrow(pts1)))
ci2 <- c(qt(.975, nrow(pts2)-1) * sd(pts2$SVD1)/sqrt(nrow(pts2)),
         qt(.975, nrow(pts2)-1) * sd(pts2$SVD2)/sqrt(nrow(pts2)))

# Helper to build one panel's traces
panel_traces <- function(p, pts, mean_xy, ci_xy, color, label, xaxis, yaxis,
                          show_legend) {
  p |>
    add_trace(x = pts$SVD1, y = pts$SVD2,
              type = "scatter", mode = "markers",
              marker = list(color = color, size = 6, opacity = 0.5),
              xaxis = xaxis, yaxis = yaxis,
              name = sprintf("%s units (n=%d)", label, nrow(pts)),
              showlegend = show_legend) |>
    add_trace(x = mean_xy[1], y = mean_xy[2],
              type = "scatter", mode = "markers",
              marker = list(color = color, symbol = "square", size = 14,
                            line = list(color = "black", width = 1.5)),
              error_x = list(array = ci_xy[1], color = color, thickness = 2),
              error_y = list(array = ci_xy[2], color = color, thickness = 2),
              xaxis = xaxis, yaxis = yaxis,
              name = sprintf("%s mean ± 95%% CI", label),
              showlegend = show_legend) |>
    # Donut nodes (black ring)
    add_trace(x = nodes_xy$x, y = nodes_xy$y,
              type = "scatter", mode = "markers",
              marker = list(color = "black", size = marker_sizes,
                            symbol = "circle",
                            line = list(color = "black", width = 1),
                            sizemode = "diameter"),
              xaxis = xaxis, yaxis = yaxis,
              name = "Codes", hoverinfo = "skip",
              showlegend = FALSE, cliponaxis = FALSE) |>
    # White inner with label
    add_trace(x = nodes_xy$x, y = nodes_xy$y,
              type = "scatter", mode = "markers+text",
              marker = list(color = "white",
                            size = marker_sizes * DONUT_INNER_RATIO,
                            symbol = "circle",
                            line = list(color = "white", width = 0),
                            sizemode = "diameter"),
              text = paste0("<b>", nodes_xy$code, "</b>"),
              textposition = ifelse(nodes_xy$x >= 0, "middle right",
                                                       "middle left"),
              textfont = list(size = LABEL_FONT_PX, color = "black",
                              family = "serif"),
              xaxis = xaxis, yaxis = yaxis,
              name = "Codes (label)", hoverinfo = "text",
              showlegend = FALSE, cliponaxis = FALSE)
}

# ---------------------------------------------------------------------------
# 7. Build subplot
# ---------------------------------------------------------------------------
p <- plot_ly()
p <- panel_traces(p, pts1, m1, ci1, EDGE_COLOR_1, G1, "x",  "y",  TRUE)
p <- panel_traces(p, pts2, m2, ci2, EDGE_COLOR_2, G2, "x2", "y2", TRUE)

p <- p |>
  layout(
    title = list(text = paste0(TITLE_HTML,
                               "<br><span style='font-size:11px'>",
                               SUBTITLE_HTML, "</span>"),
                 x = 0.05),
    xaxis  = list(title = paste0("ONA SVD1 — ", G1),
                  domain = c(0.0, 0.48),
                  zeroline = TRUE, zerolinecolor = "#888",
                  range = c(-2.2, 2.2)),
    yaxis  = list(title = "ONA SVD2",
                  zeroline = TRUE, zerolinecolor = "#888",
                  range = c(-1.9, 1.9), scaleanchor = "x", scaleratio = 1),
    xaxis2 = list(title = paste0("ONA SVD1 — ", G2),
                  domain = c(0.52, 1.0),
                  zeroline = TRUE, zerolinecolor = "#888",
                  range = c(-2.2, 2.2),
                  anchor = "y2"),
    yaxis2 = list(zeroline = TRUE, zerolinecolor = "#888",
                  range = c(-1.9, 1.9),
                  scaleanchor = "x2", scaleratio = 1,
                  anchor = "x2", overlaying = NULL,
                  matches = "y", showticklabels = FALSE),
    shapes = shapes_combined,
    showlegend = TRUE,
    margin = list(t = 80, l = 60, r = 30, b = 60),
    plot_bgcolor = "white", paper_bgcolor = "white",
    annotations = list(
      list(x = 0.24, y = 1.04, xref = "paper", yref = "paper",
           text = paste0("<b>", G1, "</b>"), showarrow = FALSE,
           font = list(size = 16)),
      list(x = 0.76, y = 1.04, xref = "paper", yref = "paper",
           text = paste0("<b>", G2, "</b>"), showarrow = FALSE,
           font = list(size = 16))
    )
  )

cat("Built figure: shapes =", length(shapes_combined), "\n")

# ---------------------------------------------------------------------------
# 8. Save
# ---------------------------------------------------------------------------
htmlwidgets::saveWidget(p, file.path(FIG_DIR, paste0(OUT_BASENAME, ".html")),
                        selfcontained = TRUE)
cat("[saved]", paste0(OUT_BASENAME, ".html"), "\n")

write(plotly::plotly_json(p, jsonedit = FALSE, pretty = FALSE),
      file.path(FIG_DIR, paste0(OUT_BASENAME, ".json")))
cat("[saved]", paste0(OUT_BASENAME, ".json"), "\n")
