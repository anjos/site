---
name: add-project
description: Add a new research project to the anjos.ai website. Use when the user wants to create/add a project, research area, or "major achievements" page.
---

# Add a project

A project is an SNSF-style "major achievements" page aggregating a research
area's narrative, its linked **research outputs** (papers, datasets, software —
all from Zotero), and supervised theses.

## Steps

1. Choose a short kebab-case **id** (e.g. `retinal-image-analysis`). This becomes
   the folder name and the URL `/projects/<id>/`.
2. Create `content/projects/<id>/index.md` with this front-matter (only `title`
   and `summary` are required):

   ```yaml
   ---
   title: "Human-readable title"
   weight: 40                       # controls order on /projects/ (lower = earlier)
   cover: "images/covers/<file>"    # optional; must exist under static/images/covers/
   summary: "One-sentence overview."
   partners: ["Partner A", "Partner B"]
   research_outputs:                # a SELECTION of key publications, by DOI or by an
     - "10.xxxx/xxxx"               # entry's Zotero citation `key` (DOI-less works).
     - "anjos_mednet_2024"          # Resolved from data/outputs.json and rendered as
     - "10.34777/..."               # "Key publications", ordered newest first.
   ---
   ```
   `research_outputs:` is one flat list, but the template **splits it by type** into up
   to three page sections, each newest-first (file order does not matter):
   - **Key publications** — papers/preprints/chapters. Keep to a **curated few** that best
     represent the project, not every paper.
   - **Software** — standalone reusable libraries that are their own Zotero
     `computerProgram` entries (e.g. `anjos_mednet_2024`, `anjos_bob_2015`), by `key`.
   - **Datasets** — datasets you produced, by DOI/key.

   Only list a software/dataset here when it **stands on its own** in Zotero. Code that is
   specific to one paper (its validation/repro repo) is **not** a standalone entry — it
   rides on that paper as a "Software" link (attached in Zotero; see `add-zotero-output`),
   so don't also list it here. *Datasets used but not produced by you* (public benchmarks
   like DRIVE, Sleep-EDF) are not outputs — mention them in the prose instead.

   `partners:` are the collaborating institutions — read them from the linked outputs'
   **author affiliations** (the PDF front matter / DOI page): co-authors' universities,
   hospitals, and companies. Use recognisable short names; skip André's own Idiap.
3. Write the body: a short intro narrative, then a `## Major achievements` section of
   **two paragraphs** (prose, not a bullet list) giving the concrete results obtained and
   the conclusions reached on the project's scientific questions and hypotheses. Sober and
   specific. The page then renders, in order: **Major achievements** (your body) →
   **Key publications** → **Supervised theses** → **Software** → **Datasets** (the last two
   only when such standalone entries are linked).

   **Ground it in the outputs' full text — do not invent.** Base the narrative on what the
   linked outputs actually report: read each one's **full text**, not just its title, and
   pull real figures (metrics like AUC/AUROC, cohort/dataset sizes, before/after gains) and
   the authors' own conclusions. Get the PDF in this order of preference:
   - **From Zotero first** — `pixi run python tools/zotero_pdf.py --doi <DOI> -o /tmp/x.pdf`
     (or `--key`). Most of André's outputs have their PDF attached in "My Publications", and
     this reads it through the authenticated API, so it works even when the PDF was kept
     **private** (i.e. not public, not in `data/outputs.json`'s `pdf` field). Then read it
     (`pdftotext` for text, or open the pages). Prefer this over the web for *every* output.
   - **Web only as a last resort** — if Zotero has no attachment, follow the DOI or find an
     open version (arXiv/medRxiv/SSRN preprint, a PMC record, or an institutional repository
     such as Idiap Publications).
   - If no full text is reachable at all, work from the abstract and say what is grounded vs.
     summarised — never fabricate numbers.

   Verify a claimed result against the paper before writing it; a project page must not
   overstate or mis-attribute. Note that an output's scope may differ from the project's
   framing (a paper linked to a TB project may itself be about hospital infections) — read
   it to be sure, and let the prose federate the outputs honestly.
4. For each ref in `research_outputs:`, confirm it exists in `data/outputs.json`
   (match a `doi` or `key`). If missing, add the work to Zotero "My Publications"
   (see the `add-zotero-output` skill) and run `pixi run outputs`.
5. **Connections (ASK).** Offer to wire this project to the rest:
   - **Key publications** → the `research_outputs:` list (step 2), curated to a few
     highlights. To add a *new* one, use `add-zotero-output`, then link it here.
   - **Theses** → a supervised thesis attaches automatically when its front-matter's
     `projects:` list contains this project id. If an existing thesis belongs here, add
     `<id>` to its `projects:` in `content/theses/<slug>.md` (or create it with
     `add-thesis`).
6. If a cover is referenced, put it in `static/images/covers/` **optimised**
   (long edge 1000 px, same format, under 300 KB) — see "Large assets live on
   Idiap" in `AGENTS.md`. Listing pages render the cover in a card grid that centre-crops it to **3:2**, so prefer a landscape source and keep the subject away from the top and bottom edges. If the crop cuts something important, set `cover_position:` in the front matter to any CSS `object-position` value (e.g. `"50% 20%"`) to re-aim it. Any other image, figure, or PDF the page links to goes
   to `idiap-public/` and is referenced by its full
   `https://www.idiap.ch/~aanjos/...` URL, never committed.
7. Run the gate and fix anything it reports (`idiap-push` first if you added
   anything to `idiap-public/`, otherwise the link check 404s on the new URLs):
   ```sh
   pixi run idiap-push   # only if idiap-public/ changed
   pixi run validate     # the whole gate: tests, content, build, links
   ```
