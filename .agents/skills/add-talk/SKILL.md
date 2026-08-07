---
name: add-talk
description: Add a talk, interview, or press item to the Media section of anjos.ai. Use when the user mentions a talk, media appearance, or press coverage.
---

# Add a talk / media item

## Steps

1. Pick a **slug** (e.g. `swissinfo-safe-ai-2024`).
2. Create `content/media/<slug>.md`:

   ```yaml
   ---
   title: "Headline of the talk or coverage"
   date: 2024-05-20
   slug: "<slug>"
   cover: "images/covers/<file>"    # optional; must exist under static/images/covers/
   summary: "One sentence: venue/outlet and what it was about."
   ---

   Body: context, plus a link to the recording/article/outlet.
   ```
3. Add the cover image under `static/images/covers/`, **optimised** (long edge
   1000 px, same format, under 300 KB) — see "Large assets live on Idiap" in
   `AGENTS.md`. Slides, a press PDF, or any other image go to `idiap-public/`
   and are referenced by their full `https://www.idiap.ch/~aanjos/...` URL,
   never committed.
4. Run the gate (`idiap-push` first if you added anything to `idiap-public/`,
   otherwise the link check 404s on the new URLs):
   ```sh
   pixi run idiap-push   # only if idiap-public/ changed
   pixi run validate     # the whole gate: tests, content, build, links
   ```
   Its `check-links` step will flag a dead external link — fix or replace it.
