#!/usr/bin/env python3
"""Check the site's `featured:` works are starred as "Featured works" on ORCID.

`content/outputs/_index.md` carries a hand-picked `featured:` list rendered as a
grid above the full output list. It is meant to mirror the starred works on
https://orcid.org/0000-0001-7248-4014, and nothing used to enforce that.

The relation is one-way on purpose: **the site's list must be a subset of
ORCID's.** ORCID stars five works, the site shows four to keep the grid a clean
2x2, so a work starred on ORCID but absent here is not an error and is ignored.

ORCID's public v3.0 API does not expose starred status (`display-index` is
something else), so the list comes from the same key-less JSON endpoint the
ORCID profile page itself calls. That endpoint is undocumented: if it cannot be
fetched or parsed, this check *warns* and passes, exactly as `check-outputs`
treats an unreachable Zotero — an outage must never break a deploy. A genuine
mismatch still fails.

SPDX-FileCopyrightText: Copyright © 2026 Idiap Research Institute <contact@idiap.ch>

SPDX-License-Identifier: BSD-3-Clause
"""

from __future__ import annotations

import json
import sys

import validate_content
import zotero_common

INDEX = zotero_common.ROOT / "content" / "outputs" / "_index.md"

#: Undocumented but public and key-less — what the ORCID profile page uses to
#: render the "Featured works" panel. The v3.0 API has no equivalent.
FEATURED_URL = f"https://orcid.org/{zotero_common.ORCID_ID}/featuredWorks.json"


def _featured_refs() -> list[str]:
    """Read the `featured:` list from the outputs section front-matter.

    Returns
    -------
    list[str]
        Each entry as written: a DOI or a Zotero BetterBibTeX citation key.
    """
    return [str(r) for r in validate_content.parse_front_matter(INDEX).get("featured", [])]


def _resolve(refs: list[str]) -> tuple[dict[str, str], list[str]]:
    """Resolve `featured:` references against ``data/outputs.json``.

    A reference is either a DOI or a citation key, matching what the
    ``out-featured.html`` partial resolves at build time.

    Parameters
    ----------
    refs
        References as written in the front-matter.

    Returns
    -------
    tuple[dict[str, str], list[str]]
        A ``{normalised DOI: title}`` mapping of the resolvable references, and
        the references that resolve to nothing (or to a DOI-less work, which
        cannot be compared with ORCID).
    """
    entries = json.loads(zotero_common.OUTPUT_FILE.read_text())["entries"]
    by_ref = {}
    for e in entries:
        for field in ("doi", "key"):
            if e.get(field):
                by_ref[e[field].lower()] = e
    resolved, unresolved = {}, []
    for ref in refs:
        entry = by_ref.get(ref.lower())
        doi = zotero_common.normalize_doi(entry.get("doi")) if entry else None
        if doi is None:
            unresolved.append(ref)
        else:
            resolved[doi] = entry.get("title") or ref
    return resolved, unresolved


def _orcid_featured_dois() -> set[str]:
    """Fetch the DOIs of the works starred as "Featured works" on ORCID.

    Returns
    -------
    set[str]
        Normalised DOIs. Starred works without a DOI contribute nothing.

    Raises
    ------
    Exception
        Any network, HTTP, or JSON error from the undocumented endpoint; the
        caller downgrades it to a warning.
    """
    import requests

    r = requests.get(
        FEATURED_URL,
        headers={"Accept": "application/json", "User-Agent": zotero_common.USER_AGENT},
        timeout=30,
    )
    r.raise_for_status()
    dois = set()
    for work in r.json():
        for eid in work.get("workExternalIdentifiers") or []:
            if (eid.get("externalIdentifierType") or {}).get("value", "").lower() == "doi":
                doi = zotero_common.normalize_doi(
                    (eid.get("externalIdentifierId") or {}).get("value")
                )
                if doi:
                    dois.add(doi)
    return dois


def main() -> int:
    """Run the check and report, following ``validate_content``'s convention.

    Returns
    -------
    int
        0 if every featured work is starred on ORCID (or ORCID is unreachable),
        1 otherwise. ``WARN:``-prefixed messages are non-fatal.
    """
    errors: list[str] = []
    resolved, unresolved = _resolve(_featured_refs())
    for ref in unresolved:
        errors.append(
            f"{INDEX.relative_to(zotero_common.ROOT)}: featured ref {ref} does not "
            "resolve to a work with a DOI in data/outputs.json (fix the ref, or "
            "run `pixi run outputs`)"
        )

    try:
        starred = _orcid_featured_dois()
    except Exception as e:  # undocumented endpoint — never break the build on it
        errors.append(f"WARN: could not read ORCID featured works ({e}) — not checked.")
        starred = None

    if starred is not None:
        for doi, title in sorted(resolved.items()):
            if doi not in starred:
                errors.append(
                    f"{INDEX.relative_to(zotero_common.ROOT)}: {doi} ({title}) is "
                    "featured here but not starred on ORCID — star it at "
                    f"https://orcid.org/{zotero_common.ORCID_ID} or drop it from "
                    "`featured:`"
                )

    fatal = [e for e in errors if not e.startswith("WARN:")]
    for e in errors:
        print(("  " if e.startswith("WARN:") else "  ✗ ") + e, file=sys.stderr)
    if fatal:
        print(f"\nFeatured-works check FAILED with {len(fatal)} error(s).", file=sys.stderr)
        return 1
    if starred is not None:
        print(f"Featured works: {len(resolved)} of {len(starred)} ORCID stars, all in sync.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
