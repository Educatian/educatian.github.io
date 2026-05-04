library(bnlearn)

dat <- read.csv("synthetic_gameplay_log.csv")

# Minimal example: collapse episode-level evidence for a small BN prototype.
episode_dat <- unique(dat[c("user_id", "task_id", "evidence_revision", "hint_flag", "success_flag")])
names(episode_dat) <- c("user_id", "task_id", "revision", "hint", "success")
episode_dat$revision <- factor(episode_dat$revision)
episode_dat$hint <- factor(episode_dat$hint)
episode_dat$success <- factor(episode_dat$success)

dag <- model2network("[revision][hint][success|revision:hint]")
fit <- bn.fit(dag, episode_dat[c("revision", "hint", "success")], method = "bayes")
print(fit)
