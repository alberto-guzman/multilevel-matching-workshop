# Run this after 00_install_packages.R. It prints what is missing.
# Bring the output to the workshop if anything fails.

packages <- c("tidyverse", "MatchIt", "matchMulti", "CMatching", "optmatch",
              "gbm", "dbarts", "cobalt", "lme4", "performance",
              "marginaleffects", "sensemakr", "gt", "rmarkdown", "knitr")

installed <- sapply(packages, requireNamespace, quietly = TRUE)

cat("R version:", R.version.string, "\n")
cat("Quarto on PATH:", nzchar(Sys.which("quarto")),
    "(FALSE is fine; RStudio and Positron bundle Quarto, and it is only needed to render)\n")
cat("Packages missing:", if (all(installed)) "none" else names(installed)[!installed], "\n")
cat("A note reading \"Registered S3 method overwritten\" may appear. It is expected and harmless.\n")

timss <- readRDS("data/timss_df.rds")
cat("Data loaded:", nrow(timss), "students,", length(unique(timss$school_id)), "schools\n")

library(MatchIt)
m <- matchit(multisite_treatment ~ student_sex + student_age + dad_edu,
             data = timss, method = "nearest")
cat("MatchIt test run: matched", sum(m$weights > 0), "students\n")
