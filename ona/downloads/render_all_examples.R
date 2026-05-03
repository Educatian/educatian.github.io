# =============================================================================
# render_all_examples.R — produce 4 ONA figures (single, combined, panels,
# subtracted) from the synthetic fake_dialogue_long.csv. Outputs JSON files
# next to this script; PNGs are produced separately via render_ona_kaleido.py.
# =============================================================================
suppressPackageStartupMessages({
  library(ona); library(tma); library(plotly); library(htmlwidgets); library(magrittr)
})

ROOT <- "C:/Users/jewoo/.claude/skills/ona/example_data"
OUT  <- "C:/Users/jewoo/.claude/skills/ona/example_figures"
CSV  <- file.path(ROOT, "fake_dialogue_long.csv")
dir.create(OUT, showWarnings = FALSE, recursive = TRUE)

CODES <- c("ASK","EXPLAIN","EXAMPLE","AGREE","ELABORATE")
WIN   <- 4

# Visual knobs (match the look the user signed off on)
EM <- 0.4; ES <- c(0,1.5); EL <- 2.5
NMIN <- 12; NRANGE <- 34; DI <- 0.55; LF <- 17

# ---------------------------------------------------------------------------
# Build ONA model from fake data
# ---------------------------------------------------------------------------
long <- read.csv(CSV, stringsAsFactors = FALSE)
for (c in CODES) long[[c]] <- as.integer(long[[c]])
hoo <- tma:::rules(user_id %in% UNIT$user_id & cond %in% UNIT$cond)
ctx <- tma:::contexts(long, units = c("cond","user_id"), hoo_rules = hoo)
accum <- tma:::accumulate_contexts(ctx, codes = CODES,
  decay.function = decay(simple_window, window_size = WIN),
  time.column = "turn_idx", return.ena.set = FALSE,
  mode.column = "speaker")
set <- model(accum)

flat <- as.data.frame(set$line.weights)
edge_cols <- setdiff(colnames(flat), c("cond","user_id","ENA_UNIT","ENA_DIRECTION"))
fmat <- as.matrix(flat[, edge_cols]); storage.mode(fmat) <- "numeric"
fmat[!is.finite(fmat)] <- 0
w_T <- as.numeric(colMeans(fmat[flat$cond == "treatment", , drop = FALSE]))
w_C <- as.numeric(colMeans(fmat[flat$cond == "control",   , drop = FALSE]))
weight_max <- max(c(w_T, w_C))

nodes_dt <- data.table::copy(set$rotation$nodes)
nodes_xy <- data.frame(code = as.character(nodes_dt$code),
                       x = as.numeric(nodes_dt$SVD1),
                       y = as.numeric(nodes_dt$SVD2))

make_edges <- function(weights, color, wmax = weight_max) {
  em <- ona:::create_edge_matrix(NULL, weights = weights,
                                 nodes = nodes_dt, direction = 1)
  ona:::edge_paths(em,
    edge_color = c(color), edge_end = "outward",
    desaturate_edges_by = sqrt, lighten_edges_by = sqrt,
    edge_size_multiplier = EM, scale_edges_to = ES,
    scale_edges_from = c(0, wmax),
    edge_arrow = TRUE, edge_arrow_offset = 2, edge_arrow_width = 0.1,
    edge_arrow_saturation_multiplier = 1.6,
    fake_alpha = TRUE, edge_halo = 0.5,
    edge_arrows_to_show = "max", arrow_halo = 0,
    edge_halo_multiplier = 1.1,
    sender_direction = 1, edge_arrow_direction = 2)
}
to_shapes <- function(eps, xref="x", yref="y") {
  out <- list()
  for (s in eps) {
    p <- s$path
    if (is.null(p) || !nzchar(p) || grepl("NaN|Inf", p)) next
    out[[length(out)+1]] <- list(
      type="path", path=p,
      line=list(width=(s$line$width %||% 0.5)*EL, color=s$line$color),
      opacity=s$opacity %||% 1, fillcolor=s$fillcolor,
      xref=xref, yref=yref, layer="below")
  }; out
}

# Shared node sizes (in-strength, both groups)
in_T <- colSums(ona:::to_square(w_T))
in_C <- colSums(ona:::to_square(w_C))
node_total <- in_T + in_C; node_total[node_total == 0] <- 0.001
sizes <- NMIN + NRANGE * (node_total / max(node_total))

pts <- as.data.frame(set$points)
pT <- pts[pts$cond=="treatment",]; pC <- pts[pts$cond=="control",]
mT <- c(mean(pT$SVD1), mean(pT$SVD2)); mC <- c(mean(pC$SVD1), mean(pC$SVD2))
ciT <- c(qt(.975, nrow(pT)-1)*sd(pT$SVD1)/sqrt(nrow(pT)),
         qt(.975, nrow(pT)-1)*sd(pT$SVD2)/sqrt(nrow(pT)))
ciC <- c(qt(.975, nrow(pC)-1)*sd(pC$SVD1)/sqrt(nrow(pC)),
         qt(.975, nrow(pC)-1)*sd(pC$SVD2)/sqrt(nrow(pC)))

# Helper: donut nodes onto an existing plot
add_donuts <- function(p, sizes, xax="x", yax="y") {
  p |>
    add_trace(x=nodes_xy$x, y=nodes_xy$y, type="scatter", mode="markers",
              marker=list(color="black", size=sizes, symbol="circle",
                          line=list(color="black", width=1), sizemode="diameter"),
              xaxis=xax, yaxis=yax,
              name="Codes", hoverinfo="skip", showlegend=TRUE, cliponaxis=FALSE) |>
    add_trace(x=nodes_xy$x, y=nodes_xy$y, type="scatter", mode="markers+text",
              marker=list(color="white", size=sizes*DI, symbol="circle",
                          line=list(color="white", width=0), sizemode="diameter"),
              text=paste0("<b>", nodes_xy$code, "</b>"),
              textposition=ifelse(nodes_xy$x >= 0, "middle right", "middle left"),
              textfont=list(size=LF, color="black", family="serif"),
              xaxis=xax, yaxis=yax,
              name="Codes (label)", hoverinfo="text",
              showlegend=FALSE, cliponaxis=FALSE)
}

base_layout <- function(p, title, sub, shapes, x_axis_only = FALSE) {
  p |> layout(
    title = list(text = paste0("<b>", title, "</b>",
                               "<br><span style='font-size:11px'>", sub, "</span>"),
                 x = 0.05),
    xaxis = list(title = "ONA SVD1", zeroline=TRUE, zerolinecolor="#888",
                 range = c(-2.5, 2.5)),
    yaxis = list(title = "ONA SVD2", zeroline=TRUE, zerolinecolor="#888",
                 range = c(-2.0, 2.0), scaleanchor="x", scaleratio=1),
    shapes = shapes,
    showlegend = TRUE,
    margin = list(t=80, l=60, r=30, b=60),
    plot_bgcolor = "white", paper_bgcolor = "white"
  )
}

save_two <- function(p, base) {
  htmlwidgets::saveWidget(p, file.path(OUT, paste0(base, ".html")),
                          selfcontained = TRUE)
  write(plotly::plotly_json(p, jsonedit=FALSE, pretty=FALSE),
        file.path(OUT, paste0(base, ".json")))
  cat("[saved]", base, ".html / .json\n")
}

# ---------------------------------------------------------------------------
# 1. SINGLE network — treatment only, neutral colour
# ---------------------------------------------------------------------------
ep_single <- make_edges(w_T, "#1a1a1a", wmax = max(w_T))
shapes_single <- to_shapes(ep_single)
in_only <- colSums(ona:::to_square(w_T))
sizes_only <- NMIN + NRANGE * (in_only / max(in_only))
mU <- c(mean(pT$SVD1), mean(pT$SVD2))
ciU <- ciT
p1 <- plot_ly() |>
  add_trace(x=pT$SVD1, y=pT$SVD2, type="scatter", mode="markers",
            marker=list(color="#1a1a1a", size=6, opacity=0.4),
            name=sprintf("Units (n=%d)", nrow(pT))) |>
  add_trace(x=mU[1], y=mU[2], type="scatter", mode="markers",
            marker=list(color="#1a1a1a", symbol="square", size=14,
                        line=list(color="black", width=1.5)),
            error_x=list(array=ciU[1], color="#1a1a1a", thickness=2),
            error_y=list(array=ciU[2], color="#1a1a1a", thickness=2),
            name="Mean ± 95% CI") |>
  add_donuts(sizes_only)
p1 <- base_layout(p1, "Single-network example",
                  "Synthetic dialogue data — one condition, one network. GROUP_COL <- NULL.",
                  shapes_single)
save_two(p1, "fake_ona_SINGLE")

# ---------------------------------------------------------------------------
# 2. COMBINED — both groups overlaid
# ---------------------------------------------------------------------------
ep_T_red  <- make_edges(w_T, "red")
ep_C_blue <- make_edges(w_C, "blue")
shapes_combined <- c(to_shapes(ep_T_red), to_shapes(ep_C_blue))
p2 <- plot_ly() |>
  add_trace(x=pT$SVD1, y=pT$SVD2, type="scatter", mode="markers",
            marker=list(color="red", size=6, opacity=0.5),
            name=sprintf("Treatment units (n=%d)", nrow(pT))) |>
  add_trace(x=pC$SVD1, y=pC$SVD2, type="scatter", mode="markers",
            marker=list(color="blue", size=6, opacity=0.5),
            name=sprintf("Control units (n=%d)", nrow(pC))) |>
  add_trace(x=mT[1], y=mT[2], type="scatter", mode="markers",
            marker=list(color="red", symbol="square", size=14,
                        line=list(color="black", width=1.5)),
            error_x=list(array=ciT[1], color="red", thickness=2),
            error_y=list(array=ciT[2], color="red", thickness=2),
            name="Treatment mean ± 95% CI") |>
  add_trace(x=mC[1], y=mC[2], type="scatter", mode="markers",
            marker=list(color="blue", symbol="square", size=14,
                        line=list(color="black", width=1.5)),
            error_x=list(array=ciC[1], color="blue", thickness=2),
            error_y=list(array=ciC[2], color="blue", thickness=2),
            name="Control mean ± 95% CI") |>
  add_donuts(sizes)
p2 <- base_layout(p2, "Combined view — Treatment (red) vs Control (blue)",
                  "Synthetic dialogue data; both groups overlaid in same projection.",
                  shapes_combined)
save_two(p2, "fake_ona_COMBINED")

# ---------------------------------------------------------------------------
# 3. PANELS — side-by-side
# ---------------------------------------------------------------------------
ep_T_p <- make_edges(w_T, "red")
ep_C_p <- make_edges(w_C, "blue")
shapes_panels <- c(to_shapes(ep_T_p, "x", "y"),
                   to_shapes(ep_C_p, "x2", "y2"))
panel_traces <- function(p, ppts, mxy, ci, color, label, xax, yax) {
  p |>
    add_trace(x=ppts$SVD1, y=ppts$SVD2, type="scatter", mode="markers",
              marker=list(color=color, size=6, opacity=0.5),
              xaxis=xax, yaxis=yax,
              name=sprintf("%s units (n=%d)", label, nrow(ppts))) |>
    add_trace(x=mxy[1], y=mxy[2], type="scatter", mode="markers",
              marker=list(color=color, symbol="square", size=14,
                          line=list(color="black", width=1.5)),
              error_x=list(array=ci[1], color=color, thickness=2),
              error_y=list(array=ci[2], color=color, thickness=2),
              xaxis=xax, yaxis=yax,
              name=sprintf("%s mean ± 95%% CI", label)) |>
    add_donuts(sizes, xax=xax, yax=yax)
}
p3 <- plot_ly()
p3 <- panel_traces(p3, pT, mT, ciT, "red",  "Treatment", "x",  "y")
p3 <- panel_traces(p3, pC, mC, ciC, "blue", "Control",   "x2", "y2")
p3 <- p3 |> layout(
  title = list(text = paste0("<b>Side-by-side panels — same scales</b>",
                             "<br><span style='font-size:11px'>",
                             "Synthetic dialogue data; identical node positions, edge-width and node-size scales across panels.",
                             "</span>"), x = 0.05),
  xaxis  = list(title="ONA SVD1 — Treatment", domain=c(0.0, 0.48),
                zeroline=TRUE, zerolinecolor="#888", range=c(-2.5,2.5)),
  yaxis  = list(title="ONA SVD2", zeroline=TRUE, zerolinecolor="#888",
                range=c(-2.0,2.0), scaleanchor="x", scaleratio=1),
  xaxis2 = list(title="ONA SVD1 — Control", domain=c(0.52, 1.0),
                zeroline=TRUE, zerolinecolor="#888", range=c(-2.5,2.5),
                anchor="y2"),
  yaxis2 = list(zeroline=TRUE, zerolinecolor="#888", range=c(-2.0,2.0),
                scaleanchor="x2", scaleratio=1, anchor="x2",
                matches="y", showticklabels=FALSE),
  shapes = shapes_panels, showlegend=TRUE,
  margin = list(t=90, l=60, r=30, b=60),
  plot_bgcolor="white", paper_bgcolor="white",
  annotations = list(
    list(x=0.24, y=1.04, xref="paper", yref="paper",
         text="<b>Treatment</b>", showarrow=FALSE,
         font=list(size=16, color="red")),
    list(x=0.76, y=1.04, xref="paper", yref="paper",
         text="<b>Control</b>", showarrow=FALSE,
         font=list(size=16, color="blue"))
  )
)
save_two(p3, "fake_ona_PANELS")

# ---------------------------------------------------------------------------
# 4. SUBTRACTED — Treatment − Control
# ---------------------------------------------------------------------------
w_diff <- w_T - w_C
w_pos  <- pmax(w_diff, 0); w_neg <- pmax(-w_diff, 0)
wmaxd <- max(c(w_pos, w_neg))
ep_pos <- make_edges(w_pos, "red", wmax = wmaxd)
ep_neg <- make_edges(w_neg, "blue", wmax = wmaxd)
shapes_sub <- c(to_shapes(ep_pos), to_shapes(ep_neg))
p4 <- plot_ly() |>
  add_trace(x=pT$SVD1, y=pT$SVD2, type="scatter", mode="markers",
            marker=list(color="red", size=6, opacity=0.5),
            name=sprintf("Treatment units (n=%d)", nrow(pT))) |>
  add_trace(x=pC$SVD1, y=pC$SVD2, type="scatter", mode="markers",
            marker=list(color="blue", size=6, opacity=0.5),
            name=sprintf("Control units (n=%d)", nrow(pC))) |>
  add_trace(x=mT[1], y=mT[2], type="scatter", mode="markers",
            marker=list(color="red", symbol="square", size=14,
                        line=list(color="black", width=1.5)),
            error_x=list(array=ciT[1], color="red", thickness=2),
            error_y=list(array=ciT[2], color="red", thickness=2),
            name="Treatment mean ± 95% CI") |>
  add_trace(x=mC[1], y=mC[2], type="scatter", mode="markers",
            marker=list(color="blue", symbol="square", size=14,
                        line=list(color="black", width=1.5)),
            error_x=list(array=ciC[1], color="blue", thickness=2),
            error_y=list(array=ciC[2], color="blue", thickness=2),
            name="Control mean ± 95% CI") |>
  add_donuts(sizes)
p4 <- base_layout(p4,
  "Subtracted network — Treatment minus Control",
  "Red = stronger in Treatment; blue = stronger in Control. Edge width = |w_T - w_C|.",
  shapes_sub)
save_two(p4, "fake_ona_SUBTRACTED")

# ---------------------------------------------------------------------------
# Print metrics for the guide
# ---------------------------------------------------------------------------
sq_T <- ona:::to_square(w_T); sq_C <- ona:::to_square(w_C)
rownames(sq_T) <- colnames(sq_T) <- as.character(nodes_dt$code)
rownames(sq_C) <- colnames(sq_C) <- as.character(nodes_dt$code)

cat("\n=== NODE METRICS (synthetic) ===\n")
node_tbl <- data.frame(
  code = as.character(nodes_dt$code),
  in_T = round(colSums(sq_T), 3),  out_T = round(rowSums(sq_T), 3),
  in_C = round(colSums(sq_C), 3),  out_C = round(rowSums(sq_C), 3),
  in_diff  = round(colSums(sq_T) - colSums(sq_C), 3),
  out_diff = round(rowSums(sq_T) - rowSums(sq_C), 3))
print(node_tbl, row.names = FALSE)

cat("\n=== NETWORK METRICS (synthetic) ===\n")
mean_dist <- sqrt(sum((mT - mC)^2))
cat(sprintf("  Active edges:  T=%d  C=%d\n", sum(w_T>0), sum(w_C>0)))
cat(sprintf("  Total mass:    T=%.3f  C=%.3f\n", sum(w_T), sum(w_C)))
cat(sprintf("  Mean SVD1:     T=%.3f  C=%.3f\n", mT[1], mC[1]))
cat(sprintf("  Mean SVD2:     T=%.3f  C=%.3f\n", mT[2], mC[2]))
cat(sprintf("  Between-means dist: %.3f\n", mean_dist))

cat("\n=== GROUP COMPARISON (synthetic) ===\n")
t1 <- t.test(SVD1 ~ cond, data = pts); t2 <- t.test(SVD2 ~ cond, data = pts)
cohend <- function(x, y) {
  nx <- length(x); ny <- length(y)
  s_pool <- sqrt(((nx-1)*var(x) + (ny-1)*var(y))/(nx+ny-2))
  (mean(x) - mean(y)) / s_pool
}
cat(sprintf("  SVD1: t=%.3f, p=%.4f, d=%.3f\n",
    t1$statistic, t1$p.value, cohend(pT$SVD1, pC$SVD1)))
cat(sprintf("  SVD2: t=%.3f, p=%.4f, d=%.3f\n",
    t2$statistic, t2$p.value, cohend(pT$SVD2, pC$SVD2)))

set.seed(42); B <- 2000
perm_d <- replicate(B, {
  s <- sample(pts$cond)
  m1 <- c(mean(pts$SVD1[s=="treatment"]), mean(pts$SVD2[s=="treatment"]))
  m2 <- c(mean(pts$SVD1[s=="control"]),   mean(pts$SVD2[s=="control"]))
  sqrt(sum((m1-m2)^2))
})
cat(sprintf("  Permutation (B=%d): obs=%.3f, null mean=%.3f (%.3f, %.3f), p=%.4f\n",
    B, mean_dist, mean(perm_d),
    quantile(perm_d, .025), quantile(perm_d, .975),
    mean(perm_d >= mean_dist)))
