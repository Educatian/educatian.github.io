library(mirt)

dat <- read.csv("synthetic_gameplay_log.csv")

# Build a tiny task-response table for demonstration.
wide <- reshape(
  dat[c("user_id", "task_id", "success_flag")],
  idvar = "user_id",
  timevar = "task_id",
  direction = "wide"
)
resp <- wide[ , grepl("^success_flag\\.", names(wide)), drop = FALSE]
resp[is.na(resp)] <- 0

mod <- mirt(resp, 1, itemtype = "2PL", verbose = FALSE)
print(summary(mod))
print(head(fscores(mod)))
