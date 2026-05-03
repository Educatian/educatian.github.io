args <- commandArgs(trailingOnly = FALSE)
script_arg <- grep("^--file=", args, value = TRUE)
script_path <- normalizePath(sub("^--file=", "", script_arg[1]), winslash = "/")
root <- normalizePath(file.path(dirname(script_path), ".."), winslash = "/")
lib <- file.path(root, "tests", "r_lib")
outdir <- file.path(root, "tests", "results")
dir.create(outdir, recursive = TRUE, showWarnings = FALSE)
.libPaths(c(lib, .libPaths()))

suppressPackageStartupMessages({
  library(LKT)
  library(jsonlite)
})

sample_payload <- NULL
data(samplelkt)
lkt_model <- LKT(
  data = samplelkt,
  interc = FALSE,
  components = c("Anon.Student.Id", "KC..Default.", "KC..Default."),
  features = c("intercept", "intercept", "lineafm")
)
sample_payload <- list(
  rows = nrow(samplelkt),
  columns = names(samplelkt),
  output_names = names(lkt_model),
  loglike = if (!is.null(lkt_model$loglike)) unname(lkt_model$loglike) else NA
)

toy_df <- read.csv(file.path(root, "example_data", "toy_lkt_minimal.csv"))
build_error <- NULL
tryCatch(
  {
    buildLKTModel(
      data = toy_df,
      allcomponents = c("Anon.Student.Id", "KC..Default.", "KC..Default."),
      allfeatures = c("intercept", "intercept", "lineafm"),
      forv = FALSE,
      bacv = FALSE,
      interc = FALSE
    )
  },
  error = function(e) {
    build_error <<- conditionMessage(e)
  }
)

payload <- list(
  lkt_sample_run = sample_payload,
  minimal_data_columns = names(toy_df),
  buildLKTModel_error = build_error,
  note = "On this machine, the safest smoke-test path is LKT() on samplelkt/vignette-style data. buildLKTModel() is easier to mis-specify on a minimal toy frame and should be treated as an advanced entry point."
)

write_json(payload, file.path(outdir, "lkt_r_result.json"), pretty = TRUE, auto_unbox = TRUE)
