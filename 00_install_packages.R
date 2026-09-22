# Run once. Installs every package used in the workshop documents, then checks
# that each one loads and that the data file is where the documents expect it.
# The last line should read "Setup complete". If it does not, bring the output
# to the workshop.

packages <- c(
  "tidyverse",
  "MatchIt",
  "matchMulti",
  "CMatching",
  "optmatch",
  "gbm",
  "dbarts",
  "cobalt",
  "lme4",
  "performance",
  "marginaleffects",
  "sensemakr",
  "gt",
  "rmarkdown",
  "knitr"
)

install.packages(packages)

# Check: every package loads, and the data file is found from the project folder
invisible(lapply(packages, library, character.only = TRUE))
timss <- readRDS("data/timss_df.rds")
cat("Setup complete:", length(packages), "packages loaded,", nrow(timss), "students in the data.\n")
