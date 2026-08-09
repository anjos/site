---
name: add-software
description: Add an open-source software package to André's research outputs (a Zotero `computerProgram` item). Use when the user mentions a new package/library/tool to list.
---

# Add a software package

Software is a **research output**: it lives in Zotero "My Publications" as a
`computerProgram` item (source of truth), and appears under Research Outputs at
`/outputs/software/` with its license and Docs · PyPI · conda-forge · Source links.
This uses the same write path as [add-zotero-output](../add-zotero-output/SKILL.md).

## Gather the facts (do not guess)

For a package named `<name>`:

1. **PyPI** — `https://pypi.org/pypi/<name>/json`: the `License ::` classifier →
   license (e.g. GPL-3.0, BSD-3-Clause); `project_urls.repository`/`.documentation`;
   the earliest release date → **first-release year**.
   **Confirm the PyPI project is actually this software** (a namesake bit us once:
   PyPI `beat` is a "Bayesian Earthquake Analysis Tool", not Idiap's BEAT; PyPI
   `sleepless`'s first release predates the real package). If it doesn't match,
   don't use its PyPI/conda links or year.
2. **conda-forge** — verify via the API, not the web page:
   `curl -s -o /dev/null -w "%{http_code}" https://api.anaconda.org/package/conda-forge/<name>`
   (`200` = present, `404` = not).
3. **Docs** — the ReadTheDocs root (`https://<name>.readthedocs.io/`) or the
   project's docs site. **Visit it** and write a 1–2 sentence abstract of what the
   package does (→ `abstractNote`).
4. **Repo** — the GitHub/GitLab main page (→ `url`).

## Create the Zotero item

```sh
pixi run python tools/add_zotero_output.py --type computerProgram \
  --title "<name>" --year <first-release-year> \
  --abstract "<1–2 sentence description from the docs>" \
  --license "GPL-3.0" \
  --links "docs=https://<name>.readthedocs.io/;pypi=https://pypi.org/project/<name>/;conda=https://anaconda.org/conda-forge/<name>;repo=https://github.com/idiap/<name>" \
  --dry-run     # drop --dry-run to create it; add --archived for retired packages
```
The tool sets `abstractNote`, `rights` (license), `url` (repo), and the `extra`
link lines, marks it `inPublications: true`, and adds André as programmer. Include
only the `--links` that exist; add `--archived` for retired packages (Bob, BEAT).

## Finish

```sh
pixi run outputs                                  # regenerate data/outputs.json
pixi run validate                                 # tests, content, build, links
```
Its `check-links` step confirms every Docs/PyPI/conda-forge/Source link resolves. The package
now appears under Research Outputs, filterable at `/outputs/software/`.
