# Matching Methods for Multilevel Data in Education Research

Hands-on materials for the SREE 2026 workshop (Baltimore, September 2026), taught by Jordan Rickles (UCLA) and Alberto Guzman-Alvarez (American Institutes for Research).

Rendered site: https://alberto-guzman.github.io/multilevel-matching-workshop/

Chapter 4 (setup and data) is shown from the handbook itself. Each `.qmd` here is the R code from one chapter of the handbook *Propensity Score Matching in Multilevel Educational Settings*, with the explanatory text removed so it can be run top to bottom.

| File | Handbook chapter | Design |
|---|---|---|
| `05_miad.qmd` | 5 | Multisite individual assignment design |
| `06_cad.qmd` | 6 | Cluster assignment design |

## Setup

1. Install R (4.3 or later) and RStudio or Positron.
2. Clone or download this repository.
3. Run `00_install_packages.R` once.
4. Open `05_miad.qmd` and run the chunks in order.

Rendering a document (`quarto render 05_miad.qmd`) runs every chunk. Chapter 5 fits GBM, BART, and two logistic mixed models, so expect a few minutes.

## Data

`data/timss_df.rds` is TIMSS 2015 Grade 4 mathematics (Canada), 2,478 students nested in teachers nested in schools. The treatment indicators are derived from observed covariates and are not real interventions. See `data/README.md`.

## Regenerating from the handbook

`tools/build_from_book.py` rebuilds the two `.qmd` files from the handbook source. It keeps code chunks, headers, code annotations, and the "Main takeaways" callouts, and drops everything else.

```
python3 tools/build_from_book.py /path/to/matching_toolkit
quarto render
```
