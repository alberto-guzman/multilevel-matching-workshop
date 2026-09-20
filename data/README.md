# Analytic data

`timss_df.rds` is the analytic dataset used by every workshop document. It holds the TIMSS 2015 Grade 4 mathematics assessment for Canada, with 2,478 students and 29 variables and no missing values. Chapter 4 of the handbook defines every variable. The treatment indicators are described below.

## Structure

The data have three levels. Students are nested within teachers, and teachers are nested within schools. The identifiers are `student_id`, `teacher_id`, and `school_id`.

The analytic `school_id` is a *synthetic* school, made by combining about three real TIMSS schools so that each analytic school has more teachers and students. School-level covariates are aggregated to one value per synthetic school, using the mean for continuous scales and bands and the majority vote for categorical and binary measures. Teacher-level covariates are constant within a teacher.

## Treatment indicators

All three indicators are constructed from observed covariates to illustrate the three designs. They are not real interventions, and the estimates in the workshop documents illustrate the workflow rather than report findings.

| Indicator | Level | Equals 1 when | Design |
|---|---|---|---|
| `multisite_treatment` | student | the student receives extra lessons in mathematics | MIAD (`05_miad.qmd`) |
| `cluster_treatment` | school | the school's average score on the TIMSS resource-shortage scale (ACBGMRS) is in the top third, that is, the school is among those least affected by shortages | CAD (`06_cad.qmd`) |
| `multisite_cluster_treatment` | teacher | the student's teacher majored in mathematics | MCAD (`07_mcad.qmd`) |

## Caveats

- `math_score` is the first plausible value (`asmmat01`) only. The five TIMSS plausible values are not combined.
- No sampling weights are applied, and the file is complete-case, so it is not population-representative. Use it to learn the matching workflow, not for inference about TIMSS.
- `school_pop` is the population of the school's community or area, in banded midpoints. It is not student enrollment.
- `school_shortage` is the TIMSS ACBGMRS scale, on which higher scores mean instruction is *less* affected by resource shortages. `cluster_treatment` therefore flags the least-affected, best-resourced schools.
