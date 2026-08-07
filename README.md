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

All three must pass before committing; CI runs the same ones:

```sh
pixi run validate   # content front-matter + covers + the Zotero data is current
pixi run build      # strict Hugo build (broken internal refs fail)
pixi run linkcheck  # no dead links in the built site
```

`pixi run gh-action` runs the full sequence exactly as CI does, unit tests
included; `pixi run qa` adds the lint hooks and an Idiap sync check. Each step is
also a task of its own: `check-content`, `check-outputs`, `check-links`,
`check-sync`, `lint`. Commit and push hooks run the cheap ones automatically —
install them once with `pixi run prek install --install-hooks`.

## What lives outside this repository

**Publications** come from the Zotero "My Publications" library, the single
source of truth. `pixi run outputs` refreshes `data/outputs.json` when a Zotero
API key is configured, and merely *verifies* that it is current when there is
none — which is how CI checks the data without any credentials. Never hand-edit
that file. `pixi run orcid-report` writes a to-do list for keeping ORCID in sync.

**PDFs and raw images** are served from `https://www.idiap.ch/~aanjos/` rather
than committed here — only optimised front-matter covers live in `static/`. The
local mirror is `idiap-public/` (git-ignored), synced with:

```sh
pixi run idiap-push   # publish to the server; additive, never deletes
pixi run idiap-pull   # refresh the local mirror from the server
```

See "Large assets live on Idiap" in [AGENTS.md](AGENTS.md) for the full rule.

**The CV** linked in the site header (`cvURL` in `hugo.toml`) is built from a
[separate repository](https://github.com/anjos/cv).

## Licence

See [LICENSE](LICENSE).
