# Matching Methods for Multilevel Data in Education Research

This repository holds the hands-on materials for the SREE 2026 workshop in Baltimore, which meets on Wednesday, September 23, 2026 in Laurel AB at 9:30 a.m. It is taught by Jordan Rickles (UCLA) and Alberto Guzman-Alvarez (American Institutes for Research).

The rendered site is at https://alberto-guzman.github.io/multilevel-matching-workshop/.

## What is in the repository

The three chapter files contain the R code from Chapters 5, 6, and 7 of the handbook *Propensity Score Matching in Multilevel Educational Settings*, which is still a draft. The explanatory text has been removed so that the code can be run from top to bottom. Chapter 4, which covers the data and the package setup, is shown from the handbook during the workshop rather than from this repository.

| File | Handbook chapter | Contents |
|---|---|---|
| `05_miad.qmd` | 5 | The multisite individual assignment design (MIAD). We run this file in the room. Exercises and a template for your own data are at the end. |
| `06_cad.qmd` | 6 | The cluster assignment design (CAD). We run this file in the room as well, after Chapter 5. |
| `07_mcad.qmd` | 7 | The multisite cluster assignment design (MCAD). This file is a reference and is not covered in the workshop. |
| `flowcharts.qmd` | 3 | The decision flowcharts for the MIAD and the CAD, for use with your own study. |
| `before_you_come.qmd` | | The full list of what to bring and what to install. |
| `index.qmd` | | The home page of the rendered site. |
| `00_install_packages.R` | | Installs the fifteen packages the documents need. Run once. |
| `00_check_setup.R` | | Confirms the installation worked. Run after the install script. |
| `data/` | | The analytic dataset and a description of its variables and caveats. |
| `checkpoints/` | | One `.RData` file per stage of Chapter 5, holding every object as it stands at the end of that stage. If a chunk fails for you during the session, load the previous stage's file and continue. |
| `slides.qmd`, `slides/` | | The Slides page, with the lecture slides for the first hour as a PDF and the short deck for the hands-on part. |
| `tools/` | | The script that rebuilds the chapter files from the handbook source. |

## What to bring and what to install

Please do the installation at home, because the wifi in the room may be slow. The [Before you come](https://alberto-guzman.github.io/multilevel-matching-workshop/before_you_come.html) page has the details.

1. **A laptop** on which you can install software. Bring your own dataset if you have one, with one row per individual, a 0/1 treatment indicator, a site identifier, covariates, and an outcome.
2. **R 4.3 or later**, and either RStudio or Positron.
3. **This repository.** Download it as a zip file or clone it. Open `multilevel-matching-workshop.Rproj` in RStudio, or open the folder in Positron.
4. **The packages.** Run `00_install_packages.R` once. It installs 15 packages from CRAN.
5. **The setup check.** Run `00_check_setup.R`. The last line should read `MatchIt test run: matched 710 students`. If it does not, bring the output with you.

You should be comfortable with basic R, including scripts, data frames, and the pipe. The first hour of the workshop covers the ideas the code relies on, which are potential outcomes, propensity scores, and standardized mean differences.

If the installation fails, you can still follow along. Every output is on the rendered site.

## What we run in the room

We work through two files after the break.

- **`05_miad.qmd`**, one chunk at a time, with a stop for questions at the end of every stage. Stage 2 estimates eight propensity scores across seven chunks, and we split them. You run the four fast ones, which are the single-level, the fixed effects (intercepts only), the partially-pooled, and the random intercepts chunks. We run the three slow ones on the projector, which are the fully interacted fixed effects, the random intercepts and slopes, and the machine learning chunk.
- **`06_cad.qmd`**, as a tour on the projector. Alberto runs the main chunks and explains what changes when whole schools are assigned. Run the page at home. It takes about fifteen seconds over thirty chunks, and it loads its own packages and data, so it does not depend on the Chapter 5 session.

If a chunk fails for you, do not stop. Every stage of `05_miad.qmd` from Stage 2 on opens with a line that loads `checkpoints/stage_N.RData`, which restores every object from the end of the previous stage.

`07_mcad.qmd` and `flowcharts.qmd` are yours to read afterwards, along with the exercises and the own-data template at the end of `05_miad.qmd`.

## Feedback and testers

Please fill out the workshop feedback form at https://forms.cloud.microsoft/r/XZpKK1aEmY. The form also asks whether you would like to be an end-user tester for the handbook.

## Data

`data/timss_df.rds` contains the TIMSS 2015 Grade 4 mathematics data for Canada, with 2,478 students nested in teachers, who are nested in schools. The treatment indicators were derived from observed covariates and do not represent real interventions. See `data/README.md` for details.

## Regenerating the chapter files from the handbook

`tools/build_from_book.py` rebuilds `05_miad.qmd`, `06_cad.qmd`, and `07_mcad.qmd` from the handbook source. It keeps the code chunks, the headers, the code annotations, and the "Main takeaways" callouts, and it drops everything else. It also appends the "Try it" and "Your own data" blocks to the end of `05_miad.qmd`.

```
python3 tools/build_from_book.py /path/to/matching_toolkit
quarto render
```
