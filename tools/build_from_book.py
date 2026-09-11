#!/usr/bin/env python3
"""Regenerate the workshop .qmd files from the handbook chapters.

Usage:  python3 tools/build_from_book.py [path/to/matching_toolkit]

Keeps: YAML, headers, code chunks (with options), the numbered annotation
lists that follow a chunk, and the "Main takeaways" callouts.
Drops: all other prose, other callouts, markdown tables, images in prose.
"""
import re, sys, shutil, pathlib

BOOK = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else "~/matching_toolkit").expanduser()
OUT  = pathlib.Path(__file__).resolve().parent.parent

CHAPTERS = {
    "chapter_5_multisite.qmd":   ("05_miad.qmd",       "Multisite individual assignment design, MIAD (Chapter 5)"),
    "chapter_6_cluster.qmd":     ("06_cad.qmd",        "Cluster assignment design, CAD (Chapter 6)"),
    "chapter_7_multisite_cluster.qmd": ("07_mcad.qmd", "Multisite cluster assignment design, MCAD (Chapter 7)"),
}

# Chunks whose code stays hidden (long reference tables)
KEEP_HIDDEN = {"tbl-var-defs", "tbl-trt-defs"}

# Lines appended inside formerly hidden chunks so their results print
PRINT_AFTER = {
    "n_pref_within   <- n_pref_treated - n_pref_fallback":
        "\nc(within_site = n_pref_within, cross_site_fallback = n_pref_fallback,\n  treated_matched = n_pref_treated)",
    "  lmer(student_math_conf ~ 1 + (1 | school_id), data = timss))$ICC_adjusted":
        "\n\nc(icc_outcome = icc_outcome, icc_math_conf = icc_conf)",
    "sigma_firc  <- sigma(firc_model)":
        "\n\nc(site_average = delta_firc, between_school_sd = tau_firc, residual_sd = sigma_firc)",
    "  mutate(n_kept = coalesce(n_kept, 0L), pct = 100 * n_kept / n_total)":
        "\n\nsummary(nf_school_ret$pct)",
    "  map_dbl(\\(b) max(abs(b$Balance$Diff.Adj), na.rm = TRUE))":
        "\n\nmax_smd",
    '  treat.name   = "cluster_treatment"\n)':
        "\n\n# ci1/ci2 are not ordered for a negative effect, so take the range\nc(estimate = multi_outcome$p.est,\n  ci_low = min(multi_outcome$ci1, multi_outcome$ci2),\n  ci_high = max(multi_outcome$ci1, multi_outcome$ci2),\n  p_value = multi_outcome$pval.c)",
}

# Chunks that end in an assignment show nothing when run. In the handbook the value
# reached the reader through inline prose, which this version drops, so we append a
# short print line. Keys are matched against the chunk body and must identify one chunk.
PRINT_TAIL = {
    "05_miad.qmd": {
        "m_single <- matchit(":   "summary(timss$pscore_single)",
        "m_fe <- matchit(":       "summary(timss$pscore_fe)",
        "m_fe_int <- matchit(":   "summary(timss$pscore_fe_int)",
        "ps_ri_model <- glmer(":  "summary(timss$pscore_ri)",
        "ps_ris_model <- glmer(": "summary(timss$pscore_ris)",
        "m_partial_ps <- matchit(": "summary(timss$pscore_partial)",
        "m_bart <- matchit(":     "summary(timss$pscore_gbm)\nsummary(timss$pscore_bart)",
        "m_global <- matchit(":   "m_global",
        "m_within <- matchit(":   "m_within",
        "m_partial <- matchit(":  "m_partial",
    },
    "06_cad.qmd": {
        "cluster_df <- timss |>":   "cluster_df",
        "m_ps_cluster <- matchit(": "summary(cluster_df$pscore)",
        "m_cluster_nn <- matchit(": "m_cluster_nn",
        "m_cluster_opt <- matchit(": "m_cluster_opt",
        "dat_sequential <- timss |>": "count(dat_sequential, cluster_treatment)",
        "m_multi <- matchMulti(":   "c(schools = n_distinct(m_multi$matched$school_id),\n  students = nrow(m_multi$matched))",
    },
    "07_mcad.qmd": {
        "overlap_schools <- site_diagnostics |>":
            "c(schools_all = n_distinct(timss$school_id),\n  schools_with_overlap = length(overlap_schools))",
        "m_ps_single <- matchit(":
            "summary(teacher_df_overlap$pscore_single)\nsummary(teacher_df_overlap$pscore_ri)",
        "m_across <- matchit(":   "m_across",
        "m_within_it <- matchit(": "m_within_it",
        "m_grouped <- matchit(":  "m_grouped",
    },
}

# Annotation text that pointed at prose the workshop version drops
REPLACE = {
    "(see the caliper callout above)": "(see the caliper note in Stage 3 of the handbook chapter)",
    ", the exception described above.": ", the one exception to matching without replacement in this document.",
    "The prose reports how many school-covariate points lie beyond.": "`sum(abs(within_smds$smd) > 3)` counts the points beyond the display limit.",
    "# Helper values used in the prose below": "# Helper values reused in the caterpillar plot below",
    "follows the chapter convention stated above.": "follows the chapter's convention of standardizing by the treated-group SD.",
}

# Appended to Chapter 5 only: exercise block + own-data template for the workshop
TAIL = {"05_miad.qmd": """
## Try it

Each exercise changes one argument in the Stage 3 matching call. Make the change, then rerun the retention table and the love plot and compare the result with what we saw in the session.

```{r}
#| eval: false

# A. Tighten the caliper to 0.10. How many treated students does within-site matching lose?
m_within_tight <- matchit(ps_formula, data = timss, method = "nearest",
                          distance = timss$pscore_fe, exact = ~school_id,
                          replace = FALSE, caliper = 0.10, estimand = "ATT")
sum(m_within_tight$weights[timss$multisite_treatment == 1] > 0)

# B. Run global matching on the single-level score instead of the fixed-effects score.
m_global_single <- matchit(ps_formula, data = timss, method = "nearest",
                           distance = timss$pscore_single, replace = FALSE,
                           caliper = 0.25, estimand = "ATT")
love.plot(m_global_single, binary = "std", stats = "mean.diffs", thresholds = c(m = .25),
          var.names = var_labels, colors = c(air_navy, air_blue))

# C. Run global matching with replacement. The weights are no longer 0 or 1.
m_global_rep <- matchit(ps_formula, data = timss, method = "nearest",
                        distance = timss$pscore_fe, replace = TRUE,
                        caliper = 0.25, estimand = "ATT")
table(match.data(m_global_rep)$weights)
```

## Your own data

Five objects set the whole workflow. Fill them in, and the chunks above will run on your study.

```{r}
#| eval: false

timss      <- readRDS("path/to/your_data.rds")   # one row per individual
                                                 # columns: treatment (0/1), site id, covariates, outcome

ps_formula <- your_treatment ~ covariate_1 + covariate_2 + site_covariate_1

# site id column: replace school_id in exact = ~school_id, cluster = "school_id",
#                 factor(school_id), and vcov = ~subclass + school_id

outcome_formula <- your_outcome ~ your_treatment + covariate_1 + covariate_2

# estimand: choose the individual-average effect (att_within) or the site-average effect (att_site_avg)
```
"""}

HOWTO = """::: {.callout-tip title="How to use this document"}
This page contains the code from the handbook chapter with the explanatory text removed. Run the chunks in order from the top, because later chunks depend on objects created earlier. The numbered notes under a chunk explain the marked lines. The full discussion of each stage is in the handbook chapter.
:::
"""

# One sentence inserted after a header, so the estimand is stated on the page
AFTER_HEADER = {
    "05_miad.qmd": {"## Stage 1: Define estimand and understand data {#sec-stage1}":
        "The estimand in this example is the effect on the treated. Stage 5 estimates both the individual-average and the site-average version of it."},
    "06_cad.qmd": {"## Stage 1: Define estimand and understand data {#sec-cad-stage1}":
        "The estimand in this example is the effect on the treated schools. Stage 5 estimates the individual-average, the cluster-average, and a precision-weighted version of it."},
}

NOTE = {"05_miad.qmd": """::: {.callout-important title="In the workshop"}
Stage 2 fits seven propensity score models and we split them. You run the single-level, the fixed effects (intercepts only), the partially-pooled, and the random intercepts chunks, which take a few seconds between them. We run the fully interacted fixed effects, the random intercepts and slopes, and the machine learning chunks on the projector, because those are slow enough that a room full of laptops would be waiting on them. If you use RStudio, do not use "Run All Chunks Above", because it runs all seven. Every other chunk on the page runs in seconds.
:::
""",
        "06_cad.qmd": """::: {.callout-important title="In the workshop"}
We run this page after the Chapter 5 page. Every chunk here runs in a few seconds, so run the page from top to bottom without skipping anything. The page loads its own packages and data and does not depend on Chapter 5, so you can run it in a fresh session.
:::
"""}


def strip(lines):
    out=[]; i=0; n=len(lines)
    if lines[0]=='---':
        j=lines.index('---',1); i=j+1
    in_chunk=False; skip=0; after_chunk=False
    while i<n:
        L=lines[i]
        if in_chunk:
            out.append(L)
            if L.strip()=='```': in_chunk=False; after_chunk=True; out.append('')
            i+=1; continue
        if L.startswith('```{r'):
            in_chunk=True; out.append(L); i+=1; continue
        if L.startswith(':::'):
            if skip:
                skip += -1 if L.strip()==':::' else 1
                i+=1; continue
            if 'callout' in L and 'Main takeaways' not in L:
                skip=1; i+=1; continue
            if 'callout' in L:
                out.append(L); i+=1
                while lines[i].strip()!=':::': out.append(lines[i]); i+=1
                out += [':::','']; i+=1; continue
            out += [L,'']; i+=1; continue
        if skip: i+=1; continue
        if re.match(r'^#{1,4} ',L):
            out += [L,'']; after_chunk=False; i+=1; continue
        if after_chunk and re.match(r'^\d+\.\s',L):
            while i<n and lines[i].strip()!='': out.append(lines[i]); i+=1
            out.append(''); after_chunk=False; continue
        if L.strip()!='': after_chunk=False
        i+=1
    return out

def process_chunks(lines, dst):
    """Unhide chunks, drop include:false chunks, drop design-figure chunks if the png is missing."""
    out=[]; i=0
    while i<len(lines):
        if lines[i].startswith('```{r'):
            j=i
            while lines[j].strip()!='```': j+=1
            chunk=lines[i:j+1]
            opts=[l for l in chunk if l.startswith('#| ')]
            label=next((l.split(':',1)[1].strip() for l in opts if l.startswith('#| label:')),'')
            if any(l.startswith('#| include: false') for l in opts):
                i=j+1
                if i<len(lines) and lines[i]=='': i+=1
                continue
            if 'knitr::include_graphics' in '\n'.join(chunk):
                png=re.search(r'include_graphics\("([^"]+)"\)','\n'.join(chunk)).group(1)
                if not (BOOK/'part2_handbook'/png).exists():
                    i=j+1; continue
            if label not in KEEP_HIDDEN:
                chunk=[l for l in chunk if not l.startswith('#| echo: false')]
            for key, tail in PRINT_TAIL.get(dst, {}).items():
                if key in '\n'.join(chunk):
                    assert chunk[-1].strip()=='```', key
                    chunk = chunk[:-1] + ['', tail, '```']
                    break
            out += chunk; i=j+1; continue
        out.append(lines[i]); i+=1
    return out

def drop_empty_headers(lines):
    """Drop headers with no content under them. Code chunks are skipped, because an R
    comment line looks exactly like a Markdown header to the regex below."""
    changed=True
    while changed:
        changed=False; out=[]; i=0; in_chunk=False
        while i<len(lines):
            if in_chunk:
                out.append(lines[i])
                if lines[i].strip()=='```': in_chunk=False
                i+=1; continue
            if lines[i].startswith('```{r'):
                in_chunk=True; out.append(lines[i]); i+=1; continue
            m=re.match(r'^(#{1,4}) ',lines[i])
            if m:
                lvl=len(m.group(1)); k=i+1
                while k<len(lines) and lines[k]=='': k+=1
                nxt=lines[k] if k<len(lines) else None
                m2=re.match(r'^(#{1,4}) ',nxt) if nxt else None
                if nxt is None or (m2 and len(m2.group(1))<=lvl):
                    changed=True; i=k; continue
            out.append(lines[i]); i+=1
        lines=out
    return lines

def collapse_blanks(lines):
    res=[]
    for L in lines:
        if L=='' and res and res[-1]=='': continue
        res.append(L)
    while res and res[-1]=='': res.pop()
    return res

for src,(dst,title) in CHAPTERS.items():
    text=(BOOK/'part2_handbook'/src).read_text()
    text=text.replace('"../data/timss_df.rds"','"data/timss_df.rds"')
    for k,v in PRINT_AFTER.items():
        if k in text:
            assert text.count(k)==1, k
            text=text.replace(k,k+v)
    for k,v in REPLACE.items(): text=text.replace(k,v)
    lines=collapse_blanks(drop_empty_headers(process_chunks(strip(text.split('\n')), dst)))
    for hdr,sent in AFTER_HEADER.get(dst,{}).items():
        assert lines.count(hdr)==1, hdr
        k=lines.index(hdr); lines[k+1:k+1]=['',sent]
    yaml=f'---\ntitle: "{title}"\n---\n\n'
    (OUT/dst).write_text(yaml+HOWTO+NOTE.get(dst,'')+'\n'+'\n'.join(lines)+'\n'+TAIL.get(dst,''))
    print(f'{src} -> {dst}: {len(lines)} lines')

for png in ('miad_design.png','cad_design.png','mcad_design.png'):
    p=BOOK/'part2_handbook'/'figures'/png
    if p.exists(): shutil.copy(p, OUT/'figures'/png)
for png in ('MMT_Chapter3_Figure3_2.png','MMT_Chapter3_Figure3_3.png'):
    shutil.copy(BOOK/'part1_primer'/'figures'/png, OUT/'figures'/png)
shutil.copy(BOOK/'data'/'timss_df.rds', OUT/'data'/'timss_df.rds')
print('copied figures + data')
