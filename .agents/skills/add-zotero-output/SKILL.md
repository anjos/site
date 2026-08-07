---
name: add-zotero-output
description: Add one new research output (paper, preprint, chapter, patent, thesis, or dataset) to André's Zotero "My Publications" — the source of truth for the site and ORCID. Use when the user has a new output (a DOI and/or a PDF) to register. Optional — the user may instead add it via the Zotero desktop/web GUI.
---

# Add a research output to Zotero

Zotero **"My Publications"** is the single source of truth. Everything downstream
(the website, the ORCID report) is generated from it. This skill adds ONE work.

> This step is optional: the user can add the work in the Zotero GUI instead
> (New Item → fill fields → tick "My Publications"; drag a PDF onto it; right-click
> the attachment → set its "My Publications" file visibility). If they did that,
> skip to the workflow's next step (`pixi run outputs`).

Writing needs a read-write key in `~/.config/pyzotero.toml` (`api_key` + `user_id`).

## Steps

1. **Collect what the user has.** Ask for the **DOI** (preferred) and/or a **PDF
   path**, plus anything else they volunteer (venue, type). Most metadata comes
   from the DOI — don't over-ask.

2. **Preview the enriched entry** (dry-run — reads Crossref, writes nothing):
   ```sh
   pixi run python tools/add_zotero_output.py --doi <DOI> --dry-run
   ```
   Check the type/title/authors/venue/year look right. If Crossref is thin or the
   work has no DOI, supply the essentials explicitly:
   ```sh
   pixi run python tools/add_zotero_output.py --type conferencePaper \
     --title "…" --venue "…" --year 2026 --authors "Jane Doe;André Anjos" --dry-run
   ```
   Zotero types: `journalArticle`, `conferencePaper`, `preprint`, `bookSection`,
   `book`, `patent`, `thesis`, `report`, `newspaperArticle`, `magazineArticle`.

3. **If there's a PDF, ASK: public or private?**
   - **Public** — the file is served openly (`…/publications/items/<key>/file`),
     shown on the website. Right for open-access / author-hosted copies.
   - **Private** — stored for the record but not served (use when the DOI already
     provides access, or the PDF isn't OK to redistribute).
   Do not guess; the user decides.

4. **ASK about relationships.** Does this output relate to something already in the
   library? Common cases:
   - a **preprint ↔ its published** paper/chapter,
   - a **dataset ↔ the paper that introduced/uses** it.

   If yes, identify the related item — by its **DOI** or its Zotero **item key** (a
   dry-run of the tool prints existing entries; or the user names it). Pass one or
   more via `--related` (`;`-separated); the tool creates a **bidirectional** Zotero
   `dc:relation`. The site then shows a *Related `<type>` <doi/link>* line on both
   entries (direction/label are inferred from the item types — you don't set them).
   If there's no obvious relation, skip this.

4b. **ASK about the paper page and companion code.** Two optional links, each mapped to a
   specific Zotero field (both render beside the entry's DOI/PDF):
   - **Homepage** (`--paper-page <url>` -> a `Homepage:` line in the item's `extra`): a
     one-pager about the work, often with figures/videos (e.g. an Idiap
     `medai.pages.idiap.ch/.../paper/...` page). This is the authoritative source; the
     item's top-level `url` field is unreliable (earlier auto-enrichment) and is ignored by
     the site. Renders as **"Homepage"**.
   - **Companion code** (`--software <url>` -> a `Software:` line in `extra`): a repo
     **specifically tied to THIS paper** — validation/reproduction code (e.g.
     `uveai-validation`, `fm-overspecialization`, `euvip24-refine-cad-tb`). *Not* a reusable
     library with its own entry (that is a separate `computerProgram` — see `add-software` —
     and would be `--related` here). Renders as **"Software"**.

   Ask if either exists; attribute each to its field. Skip the one that doesn't apply.

5. **Create it** (drop `--dry-run`, add the PDF + visibility + any relations/links):
   ```sh
   pixi run python tools/add_zotero_output.py --doi <DOI> --pdf <PATH> --public \
     --paper-page "https://medai.pages.idiap.ch/.../paper/foo" \
     --related "10.48550/arXiv.1234;ABCD1234" --software "https://gitlab.../paper-code"
   ```
   To edit these on an **existing** item, use `tools/edit_zotero_item.py`
   (`--set-extra Homepage=…`, `--set-extra Software=…`, `--del-extra …`); see its `--help`.
   The tool creates the item with `inPublications: true`, attaches the PDF with the
   chosen visibility, links any related items, and prints the new item key. Unknown
   `--related` targets are reported and skipped (they must already be in the library).

6. **Refresh**: `pixi run outputs` (regenerates `data/outputs.json`, which now
   includes this work and its generated `key`), then `pixi run orcid-report`. The
   `add-output-workflow` skill runs the whole sequence.

7. **Connect it (ASK).** Does this output belong to a **project**, or come out of a
   **thesis** you supervised? If so, add its **DOI** (or, for a DOI-less work, its
   generated `key` from `data/outputs.json`) to that page's `research_outputs:` list —
   `content/projects/<id>/index.md` or `content/theses/<slug>.md` — so it shows in that
   page's "Research outputs". If no suitable project/thesis exists yet, offer to create
   one (`add-project` / `add-thesis`). Output↔output links are the `--related` step
   above. Then `pixi run validate && pixi run build`.

## Notes

- Idempotency: re-running creates a duplicate. If unsure whether the work already
  exists, check first (it's in the source of truth if `pixi run outputs` already lists
  it). To fix a mistake, delete the item in the Zotero GUI.
- arXiv (`10.48550`), SSRN (`10.2139`) and similar are "preprint" type; keep both a
  preprint and its published version as separate items, linked with `--related`.
- Relations are symmetric/untyped in Zotero; the site derives the direction and the
  "Related `<type>`" label from the two item types, so no manual labelling is needed.
- The mechanical worker is `tools/add_zotero_output.py`; shared logic lives in
  `tools/zotero_common.py`.
