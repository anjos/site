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
`outputs` reads the public Zotero feed. The publications page lists everything by
year with Type/Year filters; André is highlighted; public PDFs and DOIs are
linked. Project/thesis pages that cite a DOI keep resolving via `out-cite.html`.

**The CV needs no separate step.** `validate` → `check-links` → `build` → `cv` →
`cv-data`, so `static/andre-anjos-cv.pdf` is rebuilt inside the gate above and
already lists the new work. It is a git-ignored build product — never commit it,
and never run `pixi run cv` as an extra step. Confirm with
`pdftotext static/andre-anjos-cv.pdf - | grep "<title fragment>"`.

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

Branch first (`<verb>-<object>`, no slashes), then `wt step commit` — never
hand-write the message (AGENTS.md). Commit `data/outputs.json` plus any
project/thesis page touched in step 2; nothing else changes.

CI regenerates `data/outputs.json` from Zotero on build too (with the
committed file as fallback if Zotero is unreachable), so committing keeps the repo
in sync and provides that fallback.

## Accepted but not yet published (no DOI)

Common for conference and workshop papers: accepted, proceedings months away.
Register it now, correct it later — do **not** wait for the DOI.

- Type is `conferencePaper`, not `preprint`, if the proceedings are coming.
- Metadata source is the Idiap record (`publications.idiap.ch/publications/show/<id>`)
  and its `/export/publication/<id>/bibtex`, since Crossref has nothing.
- **Venue**: name the workshop, then the parent conference, as
  `<Workshop name> (<ACRONYM>), <CONF> <YEAR> Workshops` — the form
  `queiroz_does_2024` already uses. Idiap records usually drop the workshop.
- **Date**: pass `--year 2026-09`, not a bare year — `--year` goes straight to
  Zotero's `date`, and a bare year leaves `month: 0` in `data/outputs.json`.
- **PDF**: the site only links a *public Zotero attachment*; there is no way to
  point it at the Idiap URL. To surface the Idiap copy, download it and attach it
  with `--public` (`--pdf` takes a path, not a URL).
- **`--paper-page`** the Idiap record: it is the only public landing page a
  DOI-less work has, and it renders as the *Homepage* pill. On the **CV** the
  public PDF outranks it — `hayagriva()` in `tools/build-cv.py` prefers DOI, then
  `pdf`, then `url`, because a CV reader wants the file, not a landing page.
- **Reference it by citation key**, not DOI, in any `research_outputs:` list.
- When the proceedings appear:
  ```sh
  pixi run python tools/edit_zotero_item.py --key <ITEM_KEY> \
    --set DOI=10.1007/... --set proceedingsTitle="<final volume title>" --dry-run
  ```
  then `pixi run outputs && pixi run validate`. The citation key does not change,
  so every page referencing it keeps resolving.

## Notes

- The whole system is Zotero-first: never hand-edit `data/outputs.json`.
- **Wait for the citation key before `pixi run outputs`.** BetterBibTeX assigns it
  in the running Zotero desktop client and syncs it up, so it appears roughly a
  minute after the item is created — not instantly. `outputs` **fails** until then
  (`no BetterBibTeX citation key on item …`); that is the tool working, not a
  broken item. Poll instead of guessing:
  ```sh
  curl -s "https://api.zotero.org/users/5992358/publications/items/<KEY>?format=json" \
    | python3 -c "import json,sys; print(json.load(sys.stdin)['data'].get('citationKey'))"
  ```
  If it never arrives, Zotero desktop is closed — open it and let it sync.
- **Never guess the citation key; read it from `data/outputs.json`.** BBT drops
  leading stopwords and strips punctuation, so *Beyond the Last Frame …* became
  `vanrijn_last_2026` and *Loss-Conditioned …* became `ozbulak_lossconditioned_2026`.
- `add_zotero_output.py` is **not idempotent** — a re-run creates a duplicate that
  must be deleted in the Zotero GUI. Check `data/outputs.json` for the title first.
- Tools: `tools/add_zotero_output.py`, `tools/update-site-outputs.py`
  (`outputs`), `tools/edit_zotero_item.py` (fix an existing item),
  `tools/update-orcid-outputs.py` (`orcid-report`), shared logic in
  `tools/zotero_common.py`.
