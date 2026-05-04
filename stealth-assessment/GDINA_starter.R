library(GDINA)

dat <- read.csv("synthetic_gameplay_log.csv")
qmat <- read.csv("q_matrix_starter.csv")

# Demo response matrix: one row per learner, one column per task.
wide <- reshape(
  dat[c("user_id", "task_id", "success_flag")],
  idvar = "user_id",
  timevar = "task_id",
  direction = "wide"
)
resp <- wide[ , grepl("^success_flag\\.", names(wide)), drop = FALSE]
resp[is.na(resp)] <- 0

Q <- as.matrix(qmat[ , -c(1, 2)])
fit <- GDINA(dat = resp, Q = Q, verbose = 0)
print(fit)
