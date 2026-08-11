[![build](https://github.com/anjos/site/actions/workflows/deploy.yml/badge.svg)](https://github.com/anjos/site/actions/workflows/deploy.yml)

# anjos.ai

Source for [anjos.ai](https://anjos.ai), André Anjos' professional website. Built
with [Hugo](https://gohugo.io) and a bespoke theme, rebuilt and redeployed to
GitHub Pages on every push to `main`.

**Adding or editing content?** Read [AGENTS.md](AGENTS.md) — it is the
authoritative guide, for humans and for LLM agents alike.

## Local development

Everything runs through [pixi](https://pixi.sh), which provides Hugo, Python and
the checkers:

```sh
pixi install
pixi run serve      # local preview at localhost:1313, drafts included
```

## Gates

One command has to pass before committing, and CI runs that same one:

```sh
pixi run validate   # hygiene hooks, content front-matter, covers, unit tests,
                    # the Zotero data, a strict build and a dead-link check
```

Each step is also a task of its own: `lint`, `test`, `check-content`,
`check-outputs`, `check-links`. `check-sync` (an Idiap publish dry-run) needs SSH,
so it stays out of the gate — run it by hand after `idiap-push`. Commit hooks run
the file-hygiene checks automatically; install them once with
`pixi run prek install --install-hooks`.

## What lives outside this repository

**Publications** come from the Zotero "My Publications" library, the single
source of truth. `pixi run outputs` refreshes `data/outputs.json` when a Zotero
API key is configured, and merely *verifies* that it is current when there is
none — which is how CI checks the data without any credentials. Never hand-edit
that file. `pixi run orcid-report` writes a to-do list for keeping ORCID in sync.

**Grants and research interests** come from the ORCID record — its funding
section and its Keywords. `pixi run funding` and `pixi run interests` regenerate
`data/funding.json` and `data/interests.json`; the ORCID public API needs no key,
so CI verifies both with `--check`. The interests feed the home page's hero pills
and the CV's sidebar from that one file. Never hand-edit either.

**PDFs and raw images** are served from `https://www.idiap.ch/~aanjos/` rather
than committed here — only optimised front-matter covers live in `static/`. The
local mirror is `idiap-public/` (git-ignored), synced with:

```sh
pixi run idiap-push   # publish to the server; additive, never deletes
pixi run idiap-pull   # refresh the local mirror from the server
```

See "Large assets live on Idiap" in [AGENTS.md](AGENTS.md) for the full rule.

## The CV

`/andre-anjos-cv.pdf`, the download linked in the site header, is built here from
`cv/cv.typ` with [Typst](https://typst.app) and the
[neat-cv](https://typst.app/universe/package/neat-cv/) template. `pixi run build`
compiles it first, so the site and the PDF can never disagree.

```sh
pixi run cv         # build the PDF into static/
pixi run cv-watch   # rebuild it on every save
```

It reuses the website's own data — publications, grants, supervised theses,
courses, projects — and nothing is typed twice. See "The CV" in
[AGENTS.md](AGENTS.md) for what goes where.

## Licence

See [LICENSE](LICENSE).
