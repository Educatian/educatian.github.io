library(TraMineR)

dat <- read.csv("synthetic_gameplay_log.csv")

# Demo: create per-user task-success sequences such as S-F-S.
wide <- reshape(
  dat[c("user_id", "task_id", "success_flag")],
  idvar = "user_id",
  timevar = "task_id",
  direction = "wide"
)

seq_df <- as.data.frame(lapply(wide[ , grepl("^success_flag\\.", names(wide)), drop = FALSE], function(x) {
  ifelse(is.na(x), "M", ifelse(x == 1, "S", "F"))
}))

seq_obj <- seqdef(seq_df, alphabet = c("S", "F", "M"), states = c("S", "F", "M"))
print(seqstatd(seq_obj))
print(seqtab(seq_obj, idxs = 1:5))
