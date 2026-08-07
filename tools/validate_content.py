#!/usr/bin/env python
"""Validate site content before build (run in CI and by authoring skills).

Checks:
  * every project references DOIs that resolve in data/outputs.json;
  * software/dataset entries are well-formed;
  * every thesis links to existing project ids and has required fields;
  * cover images referenced in front-matter exist under static/;
  * static/ holds nothing but optimised covers (everything else lives on Idiap).

Exits non-zero (listing every problem) if anything is wrong.
"""

from __future__ import annotations

import json
import pathlib
import re
import sys

import yaml

ROOT = pathlib.Path(__file__).resolve().parent.parent
CONTENT = ROOT / "content"
STATIC = ROOT / "static"
PUB_FILE = ROOT / "data" / "outputs.json"

# Large assets (PDFs, raw images) are served from the Idiap web server instead of
# being committed here. IDIAP_LOCAL is the local mirror of ~/public, git-ignored
# and synced with `pixi run idiap-push` / `idiap-pull`; it is absent in CI.
IDIAP_URL = "https://www.idiap.ch/~aanjos/"
IDIAP_LOCAL = ROOT / "idiap-public"

# What may live in static/: optimised front-matter covers, plus site chrome.
STATIC_ALLOWED_DIRS = ("images/covers",)
STATIC_ALLOWED_FILES = (
    # Site icons, generated from the Medical AI group logo (latex/tikz/medai.svg).
    "images/favicon.svg",
    "images/favicon.ico",
    "images/apple-touch-icon.png",
    "images/profile_128.png",
)
STATIC_MAX_BYTES = 300 * 1024


def parse_front_matter(path: pathlib.Path) -> dict:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---"):
        return {}
    _, _, rest = text.partition("---\n")
    fm, _, _ = rest.partition("\n---")
    return yaml.safe_load(fm) or {}


def cover_ok(cover: str) -> bool:
    return (STATIC / cover.lstrip("/")).exists()


def check_static(errors: list[str]) -> None:
    """static/ may only hold optimised covers and site chrome, all under the size
    cap. Anything else belongs on Idiap (see AGENTS.md, "Large assets")."""
    for path in sorted(p for p in STATIC.rglob("*") if p.is_file()):
        rel = path.relative_to(STATIC).as_posix()
        if rel.startswith(".") or path.name == ".DS_Store":
            continue
        if not (
            rel.startswith(STATIC_ALLOWED_DIRS) or rel in STATIC_ALLOWED_FILES
        ):
            errors.append(
                f"static/{rel}: only optimised covers belong in static/ — move this "
                f"to idiap-public/{rel} and reference it as {IDIAP_URL}{rel}"
            )
        elif path.stat().st_size > STATIC_MAX_BYTES:
            errors.append(
                f"static/{rel}: {path.stat().st_size // 1024} KB exceeds the "
                f"{STATIC_MAX_BYTES // 1024} KB cap — re-encode it "
                "(long edge 1000 px, keep the format)"
            )


def check_idiap_refs(errors: list[str]) -> None:
    """Every Idiap URL used in content must exist in the local mirror, so typos
    surface before `pixi run idiap-push`. Skipped where the mirror is absent
    (CI), which is fine: check-links catches genuinely dead URLs there."""
    if not IDIAP_LOCAL.is_dir():
        return
    pattern = re.compile(re.escape(IDIAP_URL) + r'[^"\')<>\s]+')
    for md in sorted(CONTENT.rglob("*.md")):
        for url in set(pattern.findall(md.read_text(encoding="utf-8"))):
            asset = url[len(IDIAP_URL):]
            if not (IDIAP_LOCAL / asset).exists():
                errors.append(
                    f"{md.relative_to(ROOT)}: {url} has no counterpart at "
                    f"idiap-public/{asset}"
                )


def load_ref_set(errors: list[str]) -> set[str] | None:
    """Resolvable output references: DOIs *and* generated keys (for software,
    datasets, and DOI-less works), all lower-cased."""
    if not PUB_FILE.exists():
        errors.append(
            f"WARN: {PUB_FILE.relative_to(ROOT)} missing — run `pixi run outputs` "
            "(output references not checked)."
        )
        return None
    data = json.loads(PUB_FILE.read_text())
    refs = set()
    for e in data.get("entries", []):
        if e.get("doi"):
            refs.add(e["doi"].lower())
        if e.get("key"):
            refs.add(e["key"].lower())
    return refs


def main() -> int:
    errors: list[str] = []
    ref_set = load_ref_set(errors)

    project_dir = CONTENT / "projects"
    project_ids = {
        p.parent.name
        for p in project_dir.glob("*/index.md")
    }

    # ---- Projects -------------------------------------------------------- #
    for idx in sorted(project_dir.glob("*/index.md")):
        rel = idx.relative_to(ROOT)
        fm = parse_front_matter(idx)
        if not fm.get("title"):
            errors.append(f"{rel}: missing `title`")
        if not fm.get("summary"):
            errors.append(f"{rel}: missing `summary`")
        for ref in fm.get("research_outputs", []) or []:
            if ref_set is not None and str(ref).lower() not in ref_set:
                errors.append(
                    f"{rel}: output ref {ref} not found in outputs.json "
                    "(add the work to Zotero and run `pixi run outputs`, or fix the ref)"
                )
        for sw in fm.get("software", []) or []:
            if not (sw.get("name") and sw.get("url")):
                errors.append(f"{rel}: software entry needs both `name` and `url`: {sw}")
        for ds in fm.get("datasets", []) or []:
            if not ds.get("name"):
                errors.append(f"{rel}: dataset entry needs a `name`: {ds}")
        cover = fm.get("cover")
        if cover and not cover_ok(cover):
            errors.append(f"{rel}: cover image not found: {cover}")

    # ---- Theses ---------------------------------------------------------- #
    for th in sorted((CONTENT / "theses").glob("*.md")):
        if th.name == "_index.md":
            continue
        rel = th.relative_to(ROOT)
        fm = parse_front_matter(th)
        if not fm.get("title"):
            errors.append(f"{rel}: missing `title`")
        if not fm.get("author"):
            errors.append(f"{rel}: missing `author`")
        for pid in fm.get("projects", []) or []:
            if pid not in project_ids:
                errors.append(
                    f"{rel}: links to unknown project id `{pid}` "
                    f"(known: {', '.join(sorted(project_ids)) or 'none'})"
                )
        cover = fm.get("cover")
        if cover and not cover_ok(cover):
            errors.append(f"{rel}: cover image not found: {cover}")

    # ---- Assets ---------------------------------------------------------- #
    check_static(errors)
    check_idiap_refs(errors)

    # ---- Report ---------------------------------------------------------- #
    fatal = [e for e in errors if not e.startswith("WARN:")]
    for e in errors:
        print(("  " if e.startswith("WARN:") else "  ✗ ") + e, file=sys.stderr)
    if fatal:
        print(f"\nContent validation FAILED with {len(fatal)} error(s).", file=sys.stderr)
        return 1
    print("Content validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
