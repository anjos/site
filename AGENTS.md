# Working on anjos.ai

This repository builds [anjos.ai](https://anjos.ai), André Anjos' professional
website, with [Hugo](https://gohugo.io). It is designed to be edited by humans
and by LLM agents. This file tells an agent how the site is organised and how to
add content correctly.

## Golden rules

1. **Always work through `pixi`** — it provides Hugo, Python, and the checkers.
2. **After any content change, run the gates:**
   ```sh
   pixi run validate   # front-matter, refs, covers, static/ rule + Zotero data is current
   pixi run build      # strict Hugo build (broken internal refs fail)
   pixi run linkcheck  # no dead links in the built site
   ```
   All three must pass before committing. `pixi run gh-action` runs exactly what
   CI runs; `pixi run qa` adds the lint hooks and the Idiap sync check. See
   "Quality gates" below.
3. **Publications come from Zotero "My Publications", not hand-edited.** Never edit
   `data/outputs.json` by hand — regenerate it with `pixi run outputs`, which needs
   your API key. Without a key the tool *verifies* instead of writing, which is how
   CI checks the data without credentials (see below).
4. **Never commit a PDF or a raw image.** Only optimised front-matter covers live
   in `static/`; everything else is served from Idiap — see "Large assets" below.
5. Prefer Markdown; keep prose sober and readable for a scientific audience.

## Layout

```
content/
  _index.md            Home page intro
  about.md             Long/short/one-liner bio (via {{< bio >}} shortcode)
  projects/<id>/index.md   A research project (leaf bundle)  ← main content type
  theses/<slug>.md     A supervised thesis (links to a project)
  teaching/<slug>.md   A course
  media/<slug>.md      A talk / interview / press item
data/
  bio.yaml             Single source for bio text (long / short / one_liner)
  outputs.json    GENERATED from Zotero "My Publications" — do not edit by hand
layouts/               Bespoke theme (typography-first, light/dark)
assets/css/main.css    Theme styles (CSS custom properties for both themes)
tools/                 zotero_common.py (shared), update-site-outputs.py,
                       update-orcid-outputs.py, add_zotero_output.py,
                       edit_zotero_item.py, zotero_pdf.py (read a paper's PDF —
                       public or private — from Zotero), validate_content.py, tests
static/images/covers/  Optimised front-matter covers ONLY (served at /images/covers/...)
idiap-public/          GIT-IGNORED local mirror of ~/public on the Idiap web
                       server: every PDF and raw image (see "Large assets")
```

## Publications (Zotero is the source of truth)

The **Zotero "My Publications"** library (user `anjos`, id `5992358`) is the single
source of truth. The website and the ORCID to-do report are generated from it.

- Add one work:      the **add-zotero-output** skill (or the Zotero GUI)
- Refresh the site:  `pixi run outputs`   (Zotero public feed → `data/outputs.json`)
- ORCID to-do:       `pixi run orcid-report`  (writes `orcid-sync-report.md`; you
  apply it on ORCID by hand — ORCID writes need the paid Member API)
- Full recipe:       the **add-output-workflow** skill

### Update or check

`data/outputs.json` is generated but **committed**, and the tool has two modes,
chosen by whether a Zotero API key is configured:

| | with a key (your machine) | without a key (CI) |
|---|---|---|
| `pixi run outputs` | **UPDATE** — fetches and rewrites the file | **CHECK** — verifies and fails if stale |
| `pixi run check-outputs` | CHECK (forced) | CHECK |

Only one field needs the key: `related`, from Zotero's `dc:relation`, which the
public feed does not expose. Everything else is public — including each entry's
`key`, which is Zotero's **BibTeX citation key** (BetterBibTeX, e.g.
`anjos_mednet_2024`) — so CHECK verifies the whole file except `related`. That is
why CI needs no secrets. If Zotero is unreachable, staleness is *unknown* rather
than proven: the tool warns and succeeds, so an outage never breaks a deploy.

`python tools/update-site-outputs.py --help` documents the flags (`--check`,
`--update`, `--verbose`). Only a *public* PDF attachment in Zotero produces a PDF
link on the site. Writing to Zotero (the add skill) needs a read-write key in
`~/.config/pyzotero.toml` (`api_key` + `user_id`).

To feature an output on a project (or thesis) page, add its **DOI or citation key**
to that page's `research_outputs:` list — the template resolves it from
`data/outputs.json` (any type: papers, datasets, software). If it's not yet in the
data, add the work to Zotero and run `pixi run outputs`.

## Quality gates

Checks are layered by cost, cheapest first. Install the hooks once with
`pixi run prek install --install-hooks`.

| when | what | cost |
|---|---|---|
| **pre-commit** | whitespace/TOML/JSON/YAML hygiene, no submodules, **no file >300 KB in `static/`**, `ruff` on `tools/`, `check-content` | offline, instant |
| **pre-push** | `check-outputs` (Zotero freshness), `test` | network, seconds |
| **`pixi run gh-action`** | `validate` + `test` + `build` + `check-links` — exactly what CI runs | tens of seconds |
| **`pixi run qa`** | the above plus `lint` and `check-sync` | adds SSH |

Each check also runs alone: `check-content`, `check-outputs`, `check-links`,
`check-sync`, `lint`. `check-sync` is a `rsync --dry-run` proving everything in
`idiap-public/` is already published; it needs your SSH key, so it never runs in
CI. `pixi run serve` deliberately has **no** dependencies — preview must not wait
on a Zotero round-trip.

## Large assets live on Idiap

The repository stays small. The rule, enforced by `pixi run validate`:

> **All PDFs and raw image files are served from `https://www.idiap.ch/~aanjos/`.
> Only front-matter cover images — optimised for list rendering — live in `static/`.**

`idiap-public/` is a git-ignored local mirror of `~/public` on the Idiap web
server, and the path mapping is literal:

| file | URL |
|---|---|
| `idiap-public/pdfs/theses/foo.pdf` | `https://www.idiap.ch/~aanjos/pdfs/theses/foo.pdf` |
| `idiap-public/images/about/bar.jpg` | `https://www.idiap.ch/~aanjos/images/about/bar.jpg` |

Adding an asset:

1. **A cover** (front-matter `cover:`) → optimise it and put it in
   `static/images/covers/`, referenced as `images/covers/<file>`:
   ```sh
   magick IN -resize '1000x1000>' -strip -quality 82 -interlace Plane   static/images/covers/x.jpg
   magick IN -resize '1000x1000>' -strip -colors 256 -define png:compression-level=9 PNG8:static/images/covers/x.png
   ```
   Keep the source format (no extension changes), stay under 300 KB, leave SVGs
   alone. A full-resolution original also belongs on Idiap.
2. **Anything else** — a PDF, a photo, a gallery image, a logo → drop it under
   `idiap-public/<path>` and reference it by its **full URL**. Hugo's `relURL`
   passes absolute URLs through untouched, so this works in front-matter
   (`cover:`, `report:`), in Markdown links, in `{{< figure >}}`, and in the raw
   HTML the gallery pages use.
3. Publish it, **before** running `pixi run linkcheck` (which fetches the real
   URLs and will 404 otherwise):
   ```sh
   pixi run idiap-push   # rsync idiap-public/ -> idiap:public/
   pixi run idiap-pull   # the other direction, to refresh the local mirror
   ```
   Both are additive — no `--delete`, so neither side ever loses a file.

`pixi run validate` fails on anything in `static/` that is not a cover, on any
`static/` file over 300 KB, and (locally, where the mirror exists) on any Idiap
URL with no matching file in `idiap-public/`.

## Adding content

Each content type has a skill under `.claude/skills/` — prefer them:

- **add-project** — a new research project
- **add-thesis** — a supervised student's thesis (linked to a project)
- **add-zotero-output** — add one publication to Zotero (source of truth)
- **add-output-workflow** — full add-a-paper recipe (Zotero → site → ORCID report)
- **add-talk** — a Media entry (talk, interview, press item)
- **add-software** — an open-source package (a Zotero `computerProgram` research output)

The front-matter schemas the validator enforces are documented in each skill and
in `tools/validate_content.py`.

## Project front-matter (reference)

```yaml
---
title: "Retinal Image Analysis"
weight: 10                       # ordering on the Projects page
cover: "images/covers/foo.png"   # optional; must exist under static/
summary: "One-sentence overview."   # required
partners: ["Hôpital ophtalmique Jules-Gonin (HOJG)"]
research_outputs:                # linked outputs of any type, by DOI or citation key
  - "10.1038/s41598-022-09675-y" # a paper
  - "anjos_mednet_2024"          # software (Zotero citation key, see data/outputs.json)
  - "10.34777/..."               # a dataset (DOI)
---
Markdown body: an SNSF-style "major achievements" narrative. External datasets
*used* (not produced by you) are mentioned in prose, not in research_outputs.
```

The project's **id** is its folder name (`content/projects/<id>/`). A thesis
links to it with `projects: [<id>]`.
