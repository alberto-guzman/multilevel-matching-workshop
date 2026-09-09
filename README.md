# Matching Methods for Multilevel Data in Education Research

Hands-on materials for the SREE 2026 workshop (Baltimore, September 2026), taught by Jordan Rickles (UCLA) and Alberto Guzman-Alvarez (American Institutes for Research).

Rendered site: https://alberto-guzman.github.io/multilevel-matching-workshop/

Chapter 4 (setup and data) is shown from the handbook itself. Each `.qmd` here is the R code from one chapter of the handbook *Propensity Score Matching in Multilevel Educational Settings*, with the explanatory text removed so it can be run top to bottom.

| File | Handbook chapter | Design |
|---|---|---|
| `follow_along.qmd` | 5 (core path) | What we run together in the room; ends with exercises and an own-data template |
| `05_miad.qmd` | 5 | Multisite individual assignment design |
| `06_cad.qmd` | 6 | Cluster assignment design |
| `07_mcad.qmd` | 7 | Multisite cluster assignment design (reference only, not walked through) |
| `flowcharts.qmd` | 3 | Decision flowcharts for the MIAD and CAD |

## What to bring and have installed

- A laptop you can install software on. Optional: your own dataset (one row per individual, 0/1 treatment, site id, covariates, outcome).
- R 4.3 or later, and RStudio or Positron.
- This repository, cloned or downloaded as a zip and opened as a project.
- The packages: run `00_install_packages.R` once (15 CRAN packages).
- The check: run `00_check_setup.R`. It should end with `MatchIt test run: matched ... students`. If not, bring the output to the workshop.
- Basic R (scripts, data frames, the pipe) and the ideas from the first hour: potential outcomes, propensity scores, standardized mean differences.

Do the install at home. Room wifi may be slow. If the install fails, every output is on the rendered site and you can follow on screen.

Rendering a document (`quarto render 05_miad.qmd`) runs every chunk. Chapter 5 fits GBM, BART, and two logistic mixed models, so expect a few minutes. The follow-along document runs in under a minute.

## Data

`data/timss_df.rds` is TIMSS 2015 Grade 4 mathematics (Canada), 2,478 students nested in teachers nested in schools. The treatment indicators are derived from observed covariates and are not real interventions. See `data/README.md`.

## Regenerating from the handbook

`tools/build_from_book.py` rebuilds `05_miad.qmd`, `06_cad.qmd`, and `07_mcad.qmd` from the handbook source. It keeps code chunks, headers, code annotations, and the "Main takeaways" callouts, and drops everything else. `follow_along.qmd` is maintained by hand.

```
python3 tools/build_from_book.py /path/to/matching_toolkit
quarto render
```
