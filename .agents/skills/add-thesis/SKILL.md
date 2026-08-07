---
name: add-thesis
description: Add a supervised student's thesis to the anjos.ai website, linked to a project. Use when the user mentions a new master/PhD thesis they supervised.
---

# Add a thesis

A thesis page has a fixed shape: a **lead image**, a **details "report card"**, then
**four short scientific paragraphs**. It also appears under the project(s) it
contributed to (via `projects:`).

## Before writing: get the source

You need the thesis **PDF** to write accurate paragraphs (literature, hypotheses,
and performance figures) and to read the title page (author, level, university,
partners). If the user has not provided it, **ask for it** (a file, or a folder
such as `~/work/medai/theses/<student>/`). Also ask for, or pick, a
**representative figure** for the lead image.

**Ground every paragraph in the full text — do not invent.** Read the actual
manuscript, not just its title or abstract: take the performance figures in
paragraph 3 (AUC, accuracy, cohort size, before/after gains) straight from the
thesis, and verify each number against the page before writing it — never round-trip
from memory or fabricate. If the user cannot share the file, look for it in the
university's thesis library or an institutional repository (e.g. a
`webthesis`/library URL) and read that; point `report:` at that external copy. If no
full text is reachable, work from the abstract and say what is grounded vs. summarised.
The title page is likewise the source of truth for author, level, university, and
partner affiliations — read them off it rather than guessing. For any **linked research
output** (a paper from the thesis), read its PDF from Zotero first —
`pixi run python tools/zotero_pdf.py --doi <DOI> -o /tmp/x.pdf` — which fetches even
privately-kept PDFs; use the web only as a last resort.

## Front-matter schema

```yaml
---
title: "Thesis title"
author: "Student Name"           # given + family name only; drop middle names
level: "Master"                  # "Master" or "PhD"  → shows as the Degree in the report card
role: "De facto co-supervisor"   # RARE; omit for Master theses (André supervised all of them,
                                 # so a "Role" row is redundant). Set it only for the exceptional
                                 # case where his role was informal/unofficial (e.g. a PhD he
                                 # de facto co-supervised). Shows as a "Role" row when present.
university: "EPFL, School of Life Sciences"   # the theses list shows only the text before the
                                 # first comma (e.g. "EPFL", "UniDistance"), so put the short
                                 # recognisable name first
date: 2023-01-27                 # manuscript delivery date (marks the end of the thesis);
                                 # shown as "<Month Year>" on the page byline and the theses list
slug: "student-name"
cover: "images/covers/<file>"    # the representative lead image; must exist under
                                 # static/images/covers/, optimised (see below)
summary: >-                      # PLAIN-LANGUAGE synopsis for the list-page card only
  Two or three sentences a general reader understands. NOT shown on the page body.
projects: ["<project-id>"]       # one or more existing project ids (folder names)
report: "https://external/pointer.pdf"   # external link preferred (see below)
research_outputs:                # research outputs from the thesis (any type), each by
  - "10.xxxx/xxxx"               # DOI or by its Zotero citation `key` (DOI-less works,
  - "anjos_mednet_2024"          # software, datasets — find keys in data/outputs.json).
                                 # Includes the student's software packages. Only what's
                                 # listed here shows; not auto-filled from co-authorship.
datasets:                        # datasets *used* (usually external/private benchmarks,
  - name: "Dataset (note if private)"   # NOT your outputs); shown as "Datasets used".
    doi: "10.34777/..."          # optional; your own datasets go in research_outputs instead
partners:
  - name: "Hôpital ophtalmique Jules-Gonin (HOJG), Lausanne"
    country: "Switzerland"       # country is required on each partner (flag is shown)
---
```

- `title`, `author`, and a valid `projects:` list are required (the validator fails otherwise).
- **PDFs are never committed.** Prefer an external URL (Idiap Infoscience, the
  university library, etc.). With no external link, put the manuscript in
  `idiap-public/pdfs/theses/<slug>.pdf`, set `report:` to
  `https://www.idiap.ch/~aanjos/pdfs/theses/<slug>.pdf`, and `pixi run idiap-push`
  before `linkcheck`. See "Large assets live on Idiap" in `AGENTS.md`.
- **The cover is the one image that lives in the repo**, optimised: long edge
  1000 px, same format, under 300 KB (`pixi run validate` enforces this). Any
  other figure from the thesis goes to `idiap-public/` and is referenced by its
  full `https://www.idiap.ch/~aanjos/...` URL.
- Partners render with an emoji type icon (🏥 hospital, 🎓 university, 🏭 industry,
  🔬 research institute) inferred from the name, plus the country flag.

## Connections (ASK)

A thesis is defined by its links — wire them explicitly:
- **Project** (`projects:`) — one or more existing project ids (folder names under
  `content/projects/`). The thesis then appears under each project's "Supervised
  theses". If none fits, create one first with `add-project`.
- **Research outputs** (`research_outputs:`) — papers, datasets, and **software** that
  came out of the thesis, by DOI or `key`. To add a *new* output, use
  `add-zotero-output` (which can also link it back here), then `pixi run outputs`.
- **Datasets used** (`datasets:`) — external/private benchmarks the thesis used; these
  are *not* research outputs.

## Body: four impersonal paragraphs

Write exactly four short paragraphs, in an **impersonal voice** (no "I", "we", or
the student's name as subject; use passive / "the thesis"), and **no em dashes**:

1. **Introduction → question.** The clinical/scientific context, leading to the
   specific question the thesis explored.
2. **Literature + hypotheses.** What prior work had and had not done, and the
   hypothesis the thesis set out to test.
3. **Methods, data, and key result.** What was built and on what data, with
   **indicative performance figures** when the thesis reports them (accuracy, AUC,
   a before/after improvement, cohort size).
4. **Conclusions and take-aways.** What it established and its limits, and how it
   fed later work.

Keep it scientific but readable for a non-specialist who is looking André up.

## Finish

```sh
pixi run idiap-push   # only if idiap-public/ changed; must precede linkcheck
pixi run validate && pixi run build && pixi run linkcheck
```
Confirm the thesis appears at `/theses/` and under `/projects/<project-id>/`.
