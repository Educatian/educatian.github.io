args <- commandArgs(trailingOnly = FALSE)
script_arg <- grep("^--file=", args, value = TRUE)
script_path <- normalizePath(sub("^--file=", "", script_arg[1]), winslash = "/")
root <- normalizePath(file.path(dirname(script_path), ".."), winslash = "/")
lib <- file.path(root, "tests", "r_lib")
outdir <- file.path(root, "tests", "results")
dir.create(outdir, recursive = TRUE, showWarnings = FALSE)
.libPaths(c(lib, .libPaths()))

suppressPackageStartupMessages({
  library(BKT)
  library(jsonlite)
})

df <- read.csv(file.path(root, "example_data", "toy_kt_long.csv"))
fit_model <- fit(bkt(seed = 42, parallel = FALSE, num_fits = 1), data = df, parallel = FALSE)
preds <- predict_bkt(fit_model, data = df)
pars <- params(fit_model)

payload <- list(
  r_version = paste(R.version$major, R.version$minor, sep = "."),
  rows = nrow(df),
  students = length(unique(df$user_id)),
  skills = sort(unique(df$skill_name)),
  prediction_head = head(preds[c("user_id", "skill_name", "correct", "correct_predictions", "state_predictions")], 8),
  param_rows = pars,
  note = "CRAN BKT ran successfully with parallel = FALSE and num_fits = 1 on toy long-format data."
)

write_json(payload, file.path(outdir, "bkt_r_result.json"), pretty = TRUE, auto_unbox = TRUE, dataframe = "rows")
