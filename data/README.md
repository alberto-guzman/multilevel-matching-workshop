# Analytic data

`timss_df.rds` is the analytic dataset used by all workshop documents: TIMSS 2015 Canada Grade 4 math assessment, 2,478 students × 29 variables, no missing values. Variable definitions are in `04_setup_data.qmd`.

## Structure (three levels)

Students within teachers/classrooms within schools: `student_id` ⊂ `teacher_id` ⊂ `school_id`.

The analytic `school_id` is a *synthetic* school: a set of about three real TIMSS schools combined so each analytic school has more teachers and students. School-level covariates are aggregated to one value per synthetic school (mean for continuous scales and bands, majority vote for categorical and binary measures), and teacher-level covariates are constant within a teacher.

## Treatment indicators are derived, not real interventions

All three are constructed from observed covariates to illustrate the three designs. They are not real treatments, and the worked-example estimates are pedagogical, not substantive findings.

| Indicator | Level | = 1 when | Design |
|---|---|---|---|
| `multisite_treatment` | student | the student receives extra lessons in math | MIAD (`05_miad.qmd`) |
| `cluster_treatment` | school | the school's average score on the TIMSS resource-shortage scale (ACBGMRS) is in the top third, that is, the schools least affected by shortages | CAD (`06_cad.qmd`) |
| `multisite_cluster_treatment` | teacher | the student's teacher majored in math | MCAD (handbook Chapter 7) |

## Caveats

- `math_score` is the first plausible value (`asmmat01`) only. The five TIMSS plausible values are not combined.
- No sampling weights are applied and the file is complete-case, so it is not population-representative. Use it to learn the matching workflow, not for inference about TIMSS.
- `school_pop` is the population of the school's community or area (banded midpoints), not student enrollment.
- `school_shortage` is the TIMSS ACBGMRS scale, on which higher scores mean instruction is *less* affected by resource shortages. `cluster_treatment` therefore flags the least-affected (well-resourced) schools.
