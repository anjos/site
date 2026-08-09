---
name: add-output-workflow
description: End-to-end workflow to add a new research output to André's system — into Zotero (source of truth), then reflected to the website and reported for ORCID. Use when the user wants to fully add/publish a new output across all channels.
---

# Add-a-publication workflow

Zotero **"My Publications"** is the single source of truth; the website and the
ORCID to-do report are generated from it. Run these steps in order.

## 1. Add the work to Zotero  (source of truth)

Use the **`add-zotero-output`** skill (enrich from DOI, attach PDF, choose
public/private).

*Or* the user adds it themselves in the Zotero GUI (New Item → tick "My
Publications"; attach a PDF and set its file visibility). If so, just confirm it's
in "My Publications" and continue.

## 2. Refresh the website  (Zotero → data/outputs.json)

```sh
pixi run outputs                       # regenerate data/outputs.json from Zotero
pixi run validate                      # the whole gate: tests, content, build, links
```
`pubs` reads the public Zotero feed. The publications page lists everything by
year with Type/Year filters; André is highlighted; public PDFs and DOIs are
linked. Project/thesis pages that cite a DOI keep resolving via `out-cite.html`.

**Connect it (optional).** If the new output belongs to a **project** or a supervised
**thesis**, add its DOI (or generated `key`) to that page's `research_outputs:` list
(`content/projects/<id>/index.md` or `content/theses/<slug>.md`) and re-run the gates —
it then shows in that page's "Research outputs". See `add-project` / `add-thesis`.

## 3. Reflect to ORCID  (report only — you apply it by hand)

```sh
pixi run orcid-report               # writes orcid-sync-report.md
```
Open `orcid-sync-report.md` and, on your ORCID record:
- **§1 Missing on ORCID** — add these works (ORCID: Add works → Add manually, or
  Search & link by DOI).
- **§2 Outdated / incomplete** — fix the listed fields (add DOI, add the public-PDF
  URL, correct the work-type, etc.).
- **§3 On ORCID, not in Zotero** — review only; the tooling never deletes these.
  Add them to Zotero if they belong.

ORCID writes need the paid Member API, so this step is intentionally manual.

## 4. Commit

```sh
git add data/outputs.json && git commit -m "publications: add <short title>"
```
CI regenerates `data/outputs.json` from Zotero on build too (with the
committed file as fallback if Zotero is unreachable), so committing keeps the repo
in sync and provides that fallback.

## Notes

- The whole system is Zotero-first: never hand-edit `data/outputs.json`.
- Tools: `tools/add_zotero_output.py`, `tools/update-site-outputs.py`
  (`pubs`), `tools/update-orcid-outputs.py` (`orcid-report`), shared logic in
  `tools/zotero_common.py`.
