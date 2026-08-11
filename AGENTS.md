# Working on anjos.ai

This repository builds [anjos.ai](https://anjos.ai), André Anjos' professional
website, with [Hugo](https://gohugo.io). It is designed to be edited by humans
and by LLM agents. This file tells an agent how the site is organised and how to
add content correctly.

## Golden rules

1. **Always work through `pixi`** — it provides Hugo, Python, and the checkers.
2. **After any change, run the gate:**
   ```sh
   pixi run validate   # hygiene + front-matter/refs/covers + unit tests + Zotero
                       # data + a strict build and a dead-link check
   ```
   It must pass before committing, and it is exactly what CI runs — there is no
   second, longer command to remember. See "Quality gates" below.
3. **Publications come from Zotero "My Publications", not hand-edited.** Never edit
   `data/outputs.json` by hand — regenerate it with `pixi run outputs`, which needs
   your API key. Without a key the tool *verifies* instead of writing, which is how
   CI checks the data without credentials (see below).
4. **Never commit a PDF or a raw image.** Only optimised front-matter covers live
   in `static/`; everything else is served from Idiap — see "Large assets" below.
   The one exception is `cv/portrait.jpg`, which Typst has to read from disk.
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
  funding.json    GENERATED from the ORCID record's funding section — likewise
  interests.json  GENERATED from the ORCID record's Keywords — likewise; feeds
                       both the hero pills and the CV
  outputtypes.json     How the donut charts group and colour outputs. Shared by
                       the CV and /outputs/ — read its own comment before editing
  cv.json              Hand-written CV material with no web page: employment,
                       education, community service, skills, bibliometrics
cv/                    The CV (Typst + neat-cv) — see "The CV" below
layouts/               Bespoke theme (typography-first, light/dark)
assets/css/main.css    Theme styles (CSS custom properties for both themes)
assets/fonts/          Self-hosted Source Serif 4 (subset woff2) — see below
tools/                 zotero_common.py (shared), update-site-outputs.py,
                       update-funding.py, update-interests.py,
                       update-orcid-outputs.py, add_zotero_output.py,
                       edit_zotero_item.py, zotero_pdf.py (read a paper's PDF —
                       public or private — from Zotero), build-cv.py,
                       validate_content.py, tests
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

## Funding (ORCID is the source of truth)

The **funding section of the ORCID record** is the single source of truth for
grants. Add or correct a grant on <https://orcid.org>, then regenerate:

```sh
pixi run funding        # ORCID public API → data/funding.json
pixi run check-funding  # verify the committed file is current (what CI runs)
```

Never edit `data/funding.json` by hand. Unlike the Zotero tooling there is no
key to switch on — the ORCID public API is open — so `check-funding` is the very
same code path with `--check`, and a stale file fails it with a per-grant diff.
An unreachable ORCID warns and passes, as everywhere else here.

`/funding/` renders the file straight, in ORCID's own words: entries are sorted
by closing date (start date when a grant has no end), the abstract folds into a
`<details>`, and nothing on the page is curated. Amounts are kept out of the
meta line and appear inside that same disclosure, so a grant with an amount but
no abstract still gets one.

Three ORCID quirks the tool absorbs:

- A grant asserted by both you and a third party (Dimensions, say) appears twice
  in one group. ORCID groups by grant identifier; the self-asserted summary wins.
- The amount, abstract and instrument are missing from the summary feed and
  there is no bulk endpoint, so each grant costs one extra request.
- Each assertion names the funder freely, so one agency arrives under several
  names. `FUNDER_NAMES` in the tool maps them to one canonical name — add a line
  there when a new agency shows up spelled two ways.

**ORCID has no public URL for a single funding entry.** `/funding/{put-code}` is
API-only, and the `orcid.org` path of it redirects to sign-in, so the per-grant
"Grant page" pill links to the grant's own page instead — ORCID's `url` when it
has one, else the grant number's resolver (this is where the `data.snf.ch` links
come from). A grant with neither shows no pill; give it a `url` on ORCID to fix
that.

## Interests (ORCID is the source of truth)

The **Keywords of the ORCID record** are the single source of truth for research
interests. They feed two places at once — the home page's hero pills and the CV's
sidebar — so there is one list, not two:

```sh
pixi run interests        # ORCID public API → data/interests.json
pixi run check-interests  # verify the committed file is current (what CI runs)
```

Same contract as funding, and the same code path with `--check`: key-less, a
per-item diff on drift, an unreachable ORCID warns and passes. Never edit
`data/interests.json` by hand; edit the Keywords on <https://orcid.org>.

**Order is ORCID's own.** Entries are sorted by ORCID's `display-index`, highest
first, which is how ORCID itself lists them, and both renderers print them in file
order. To reorder the pills, reorder the keywords on ORCID — and note that the
check fails on a pure reorder, exactly as it does on an add or a remove.

## The CV

The CV is built here, from the website's own data, with
[Typst](https://typst.app) and the
[neat-cv](https://typst.app/universe/package/neat-cv/) template. It is published
as `/andre-anjos-cv.pdf` — `cvURL` in `hugo.toml`, the "Download CV" button and
the header link.

```sh
pixi run cv         # cv-data, then typst -> static/andre-anjos-cv.pdf
pixi run cv-watch   # rebuild on every save while editing cv/cv.typ
```

`build` **depends on** `cv`, so the PDF is always as fresh as the site, and
`check-links` verifies the download link against the real file.

### Where each section comes from

**Nothing on the CV is typed twice.** Everything the website knows is pulled from
its existing source of truth; only what has no web page is written by hand.

| CV section | Source |
|---|---|
| About, contact, social links | `data/bio.yaml`, `hugo.toml` |
| Professional experience, education | `data/cv.json` |
| Research areas | `content/projects/*/index.md` |
| Grants and funding | `data/funding.json` (→ ORCID) |
| Teaching | `content/teaching/*.md` |
| Supervision | `content/theses/*.md`, plus `data/cv.json` for students who predate the website |
| Interests | `data/interests.json` (→ ORCID Keywords) |
| Skills, bibliometrics | `data/cv.json` |
| Open software, open datasets, publications | `data/outputs.json` (→ Zotero) |

So: a new paper goes into Zotero, a new grant onto ORCID, a new thesis into
`content/theses/`. The CV picks them up on the next build. **A grant missing from
ORCID is missing from the CV** — that is the intended pressure, not a bug to work
around by adding it to `data/cv.json`.

`data/cv.json` is the one hand-written file. It is a Hugo data file, reachable as
`.Site.Data.cv.*`, so any of it can grow a web page later without moving. Its
entries all share one shape, neat-cv's: `title`, `date`, `institution`,
`location`, `description` (a string, or a list rendered as bullets). It holds one
section the CV does **not** currently print — `service` (committees, reviewing,
memberships), parked pending a review; the `= Community Service` block in
`cv/cv.typ` is commented out, not deleted.

The research outputs open on a page whose 4 cm sidebar holds two donut charts —
every output by type, and the same for the last five calendar years — over a
legend counting both. `output_stats()` in `tools/build-cv.py` does the counting;
the grouping, the order and the colours all come from **`data/outputtypes.json`**,
which the website's `/outputs/` page reads too, so a slice is the same colour in
the PDF and on the page. The slices carry no rim labels: 4 cm has no room for
them, and the legend names every category anyway.

**That file caps the chart's hues, and the cap is not cosmetic.** A donut is
read by matching any slice to any legend row, so every pair of colours has to be
tellable apart — including under colour-vision deficiency, in light mode and
dark. Five hues is the most that clears that bar; everything else folds into the
neutral "Other". Two steps sit below 3:1 against their surface, which is allowed
only because the count table is always rendered — it is the required relief, not
decoration, so do not drop it. Re-run the palette validator over the set as a
whole before changing any colour; a hue that looks fine alone routinely collides
with another one.

**`cvTypes` narrows a slice to what the CV lists.** `/outputs/` lists press items
and presentations — they are in the same Zotero library — and the CV does not, so
the neutral Other wedge counts them on the website and not in the PDF. Each chart
then totals exactly what the page it sits on goes on to list: 143 on the website,
141 on the CV. That is why the two numbers differ, and neither is wrong.

That page is a second `cv-with-side`, and the bibliography after it switches to
`cv-thin-side` — it runs for pages, and 4 cm of white down each would buy nothing.
Opening a second wide sidebar is also why `cv()` is called **without**
`profile-picture:`: neat-cv draws that at the top of every `cv-with-side`
sidebar, so the portrait is placed by hand in the first one instead.

### How it fits together

Typst reads JSON, YAML and TOML itself, so `cv/cv.typ` opens `data/*.json`,
`data/bio.yaml` and `hugo.toml` directly (hence `--root .` in the build task, which
is what makes `/data/...` resolve to the repository root). `tools/build-cv.py`
exists only for the two things Typst cannot do — read the YAML front matter inside
`content/**/*.md`, and convert `data/outputs.json` into the Hayagriva form
neat-cv's `publications()` wants. Its output, `cv/generated.yaml`, is git-ignored
and rebuilt every time.

Three details worth not rediscovering:

- **The PDF is written to `static/`, not `public/`.** `hugo --cleanDestinationDir`
  wipes `public/`, so a Typst step after Hugo would race it; writing into
  `static/` before the build keeps the whole thing one linear chain. It is the
  single exception to the `static/`-holds-only-covers rule, named in
  `tools/validate_content.py` (`STATIC_BUILD_PRODUCTS`) and git-ignored.
- **`cv/portrait.jpg` is committed**, the one raw image in the repository: Typst
  cannot fetch a URL, so the header photo cannot live on Idiap like the others.
  It must be square, because it is clipped to a circle, and it should be a real
  crop that fills the frame — no letterboxing, no blurred bands. From the
  full-resolution portrait on Idiap:
  ```sh
  magick idiap-public/images/pictures/andre-anjos-portrait.jpg \
    -gravity north -crop 989x989+0+109 +repage \
    -resize 900x900 -strip -quality 88 -interlace Plane cv/portrait.jpg
  ```
  The crop is the source's full width; the `+109` offset is what places the face
  once the circle clips the corners — raising it moves the head *up* in the
  frame. Re-derive it if the source changes.
- **Fonts come from conda-forge** (`font-ttf-roboto`, `font-ttf-opensans`,
  `font-otf-fontawesome`) and land in `$CONDA_PREFIX/fonts`, which Typst does not
  scan on its own — hence `--font-path` in the task. neat-cv's default heading
  face, Fira Sans, is not packaged for conda-forge, which is why `cv.typ` asks for
  Roboto instead. The accent colour is the site's `--accent`, set in both places.

## Quality gates

**Every gate is defined exactly once, as a pixi task.** `.pre-commit-config.yaml`
holds file hygiene and nothing else; the project-specific checks are pixi tasks,
and `lint` is what runs the hygiene hooks from inside `validate`. Install the
hooks once with `pixi run prek install --install-hooks`.

| when | what | cost |
|---|---|---|
| **pre-commit** | whitespace/TOML/JSON/YAML hygiene, no submodules, `ruff` on `tools/` | offline, instant |
| **`pixi run validate`** | `lint` + `test` + `check-content` + `check-outputs` + `check-featured` + `check-funding` + `check-interests` + `check-links` (which builds first) — **exactly what CI runs** | network, ~10 s |

The order makes failures fast and legible: offline before network, the build last,
and `test` ahead of both checkers because it covers the code they run
(`test_static_rule.py` → `validate_content.py`, `test_pipeline.py` →
`zotero_common.py`, `test_cv_data.py` → `build-cv.py`). Broken tooling then fails
as a named assertion rather than as a puzzling content error or Zotero diff.

Each check also runs alone: `check-content`, `check-outputs`, `check-featured`,
`check-funding`, `check-interests`, `check-links`, `check-sync`, `lint`. `check-links` declares `depends-on = ["build"]`, so it is
correct standalone and never link-checks a stale `public/`; `build` in turn
declares `depends-on = ["cv"]`, which is the whole chain — CV data, CV PDF, site,
links — in one order that never races. `check-sync` is a
`rsync --dry-run` proving everything in `idiap-public/` is already published; it
needs SSH, so it belongs to no composite gate — run it by hand after
`idiap-push`. `pixi run serve` deliberately has **no** dependencies — preview
must not wait on a Zotero round-trip.

The `static/` rule (layout + the 300 KB cap) lives in `check-content`, not in a
prek hook: that way it is enforced in CI, covers modified files and not just
newly added ones, and gives the "re-encode it" message instead of a bare size
error.

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
3. Publish it, **before** running `pixi run validate` (whose `check-links` step
   fetches the real URLs and will 404 otherwise):
   ```sh
   pixi run idiap-push   # rsync idiap-public/ -> idiap:public/
   pixi run idiap-pull   # the other direction, to refresh the local mirror
   ```
   Both are additive — no `--delete`, so neither side ever loses a file.

`pixi run validate` fails on anything in `static/` that is not a cover, on any
`static/` file over 300 KB, and (locally, where the mirror exists) on any Idiap
URL with no matching file in `idiap-public/`. The generated CV is exempt from the
first two — it is a build product, listed in `STATIC_BUILD_PRODUCTS` and
git-ignored (see "The CV").

### Webfonts are the one exception, and they live in `assets/`

The rule above is about `static/`. **Site webfonts belong in `assets/fonts/` and
must not be moved to Idiap** — they are part of the theme, not content, and a
third-party font request is exactly what self-hosting avoids. `assets/` is
processed by Hugo Pipes and is outside `validate_content.py`'s remit, so the
`static/` cover rule does not apply to it.

`assets/fonts/` holds Source Serif 4 (SIL OFL-1.1) as two subset variable woff2
files, ~180 KB total. They are deliberately **not** fingerprinted: `main.css`
refers to them by the relative path `../fonts/<file>.woff2`, which only resolves
if the published filename stays stable. The `@font-face` block at the top of
`assets/css/main.css` documents the exact `pyftsubset` command, the unicode
range, and why `opsz` is pinned — regenerate from there if the font is ever
updated or the content gains a script the subset does not cover.

## The theme

A bespoke, typography-first theme in `layouts/` and `assets/css/main.css`. Not a
Hugo theme or module — the reasoning is in the `theme:` commits. These are the
invariants; breaking one has already caused a real bug, so they are worth
keeping rather than rediscovering.

**One width.** `--page: 52rem` is the site's only content width, matching the
header from the title across to the CV link. Sections are `<div class="wide
band">`. Do not introduce a second width: bands of differing widths were what
made the page look misaligned.

**One accent knob.** `--accent` is the single source of colour identity;
`--accent-wash/soft/line/glow` and the hero stops all derive from it with native
`color-mix()`. Changing that one value re-tints the whole site. It is internal —
nothing in the UI exposes it. Two companions:

- `--accent-2` — the teal the hero gradient ends on, also the pill tint.
- `--on-accent` — the label colour *on* an accent fill. It exists because white
  on the accent fails in dark mode.

> **Gradients must be a hue shift at constant lightness, never a ramp toward
> white.** Ramping put the CV button's label at 3.95:1 in light and 1.80:1 in
> dark, against a 4.5:1 minimum. Held at one lightness, both stops clear 6:1.
> `pixi run test` enforces this (`tools/tests/test_contrast.py`).

**One card partial.** `layouts/partials/card.html` is the single card structure
for Projects, Teaching, Theses, Media and the Gallery; pass `"variant"
"vertical"` for grid cards. It was four copies once, which meant the link
behaviour had to be kept in sync four times.

> **Exactly one link per card.** The title's `<a>` is stretched over the whole
> card by `.card__title a::after`, so the cover image is inside the same hit
> area while the accessibility tree still sees one link. Never add a second
> anchor to the same target; anything genuinely separate inside a card needs
> `position: relative; z-index: 1`.

Grid cards centre-crop their cover to **3:2** — see the cover note in the
`add-*` skills.

**Section headings** go through `layouts/partials/sec-head.html`, which pairs an
icon with the text. It branches `h1`/`h2` explicitly: Go's `html/template`
cannot parse a dynamic element name (`<{{ $level }}`) and silently escapes the
whole partial into visible markup.

**Icons** come from `layouts/partials/icon.html`, one inline `currentColor` SVG
per name. Brand marks are the official simple-icons paths, except `linkedin`,
which simple-icons dropped and which comes from Hugo Blox's `brands.json`. No
icon font and no icon set is vendored.

**The home page** is composed in `layouts/index.html`: hero, then the top four
current projects, then the four most recent research outputs. That last section
is recomputed from `data/outputs.json` on every build and needs no curation.
**`/outputs/` carries a Bibliometrics section** between "Featured works" and the
filter bar: the two headline numbers from `data/cv.json`'s `metrics` (the CV's
own, Google-Scholar-sourced and hand-maintained), then the same two donuts the CV
draws, from the same `data/outputtypes.json`. `layouts/partials/out-bibliometrics.html`
counts straight from `data/outputs.json` — nothing is generated for it. The arcs
are dashed `<circle>`s rather than `<path>` wedges because Go templates have no
trigonometry and a dashed ring needs only the circumference; each slice is
therefore a real element with its own tooltip.

**Featured works** on `/outputs/` is the opposite — a hand-written `featured:`
list in `content/outputs/_index.md` mirroring the starred works on ORCID. Nothing
*syncs* the two — you update it by hand — but `check-featured` (in `validate`)
enforces the one direction that matters: every entry here must be starred on
ORCID. ORCID may star more than the page shows; the reverse fails the build. It
reads ORCID's undocumented `featuredWorks.json` (the v3.0 API does not expose
starred status), so a fetch failure warns instead of breaking a deploy.

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
cover_position: "50% 20%"        # optional CSS object-position; re-aims the 3:2
                                 # centre-crop cards apply to the cover
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

## Coding Style & Naming Conventions

Skills to reuse:

- Use `python-design-patterns` as basis for writing or refactoring code.
- Use `repomix` when larger overviews, refactoring, or third-party remote repositories
  need to be inspected.

Particularities for this package:

- Python: 4-space indentation, `snake_case` for functions/modules, `PascalCase` for
  classes.
- Keep lines near 88 chars (Ruff config target) and let `ruff-format` normalize
  formatting.
- You should always add docstrings to public methods, variables, enumerations, etc. You
  should avoid docstrings that only contain a sentence, and really write that first
  sentence, then a more detailed explanation of the method, a description of the
  parameters, the returned objects and any exceptions each method/function may throw, if
  applicable.
- If you create or edit Python docstrings, use the numpydoc style formatting
- Use ruff and ty to check the code and try to comply as much as possible with errors,
  warnings and tips from these tools
- All files should have a valid SPDX header with the following:
  ```text
  SPDX-FileCopyrightText: Copyright © 2026 Idiap Research Institute <contact@idiap.ch>

  SPDX-License-Identifier: BSD-3-Clause
  ```
- In Python code, you should avoid imports like `from module import function`, and just
  `import module` and use the function as `module.function(...)`. You should also avoid
  the `as` particle as in `from module import function as another_name`. Just call
  things what they are, with their full (Python) path.
- While importing within the package code itself, use relative imports for own code.
- Code from tests or documentation should use full module imports (never relative).
- By default, all methods should be private and start with a single underscore
  `def _private_method(...)`, unless it must be made public.
- Type annotations should be as permissive as possible on function/method inputs, and as
  specific as possible on function/method returns.
- Regarding type annotations, do not add aliases, just name types verbosely everywhere.
  Do not come up with aliases such as `PathLike = str | pathlib.Path` to then use
  `PathLike` everywhere. Just use `str | pathlib.Path` where needed.
- You may still add specific type aliases if, and only if, actual types would be
  ridiculously long (e.g. occupying 40 or more characters), in which case you should
  also properly document such type aliases.
- I prefer functional programming to classes. If you can find elegant ways to keep a
  functional programming style, go for it unless a class/object-oriented style is more
  elegant and will translate to less code.

## Commit & Merge Request Guidelines

- Use the shell command `wt step commit` to commit.
- Always create branches for new features and fixes -- avoid committing to the `main`
  branch directly, unless the user explicitly requests to do so.
- Branch names should not contain slashes (`/`). They should be of the format
  `<verb>-<object>` like `add-new-feature` or `fix-weird-behaviour`. The actual branch
  name should be as compact as possible to save typing.
