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

# Annotation text that pointed at prose the workshop version drops
REPLACE = {
    "(see the caliper callout above)": "(see the caliper note in Stage 3 of the handbook chapter)",
    ", the exception described above.": ", the one exception to matching without replacement in this document.",
    "The prose reports how many school-covariate points lie beyond.": "`sum(abs(within_smds$smd) > 3)` counts the points beyond the display limit.",
    "# Helper values used in the prose below": "# Helper values reused in the caterpillar plot below",
    "follows the chapter convention stated above.": "follows the chapter's convention of standardizing by the treated-group SD.",
}

HOWTO = """::: {.callout-tip title="How to use this document"}
This is the code from the handbook chapter with the explanatory text removed. Run the chunks in order from the top; later chunks depend on objects created earlier. The numbered notes under a chunk explain the marked lines. The full discussion of each stage is in the handbook chapter.
:::
"""

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

def process_chunks(lines):
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
            out += chunk; i=j+1; continue
        out.append(lines[i]); i+=1
    return out

def drop_empty_headers(lines):
    changed=True
    while changed:
        changed=False; out=[]; i=0
        while i<len(lines):
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
    lines=collapse_blanks(drop_empty_headers(process_chunks(strip(text.split('\n')))))
    yaml=f'---\ntitle: "{title}"\n---\n\n'
    (OUT/dst).write_text(yaml+HOWTO+'\n'+'\n'.join(lines)+'\n')
    print(f'{src} -> {dst}: {len(lines)} lines')

for png in ('miad_design.png','cad_design.png','mcad_design.png'):
    p=BOOK/'part2_handbook'/'figures'/png
    if p.exists(): shutil.copy(p, OUT/'figures'/png)
for png in ('MMT_Chapter3_Figure3_2.png','MMT_Chapter3_Figure3_3.png'):
    shutil.copy(BOOK/'part1_primer'/'figures'/png, OUT/'figures'/png)
shutil.copy(BOOK/'data'/'timss_df.rds', OUT/'data'/'timss_df.rds')
print('copied figures + data')
