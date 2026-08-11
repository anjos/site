#!/usr/bin/env python3
"""Keep data/interests.json in step with the ORCID record's Keywords.

ORCID is the source of truth for research interests, exactly as it is for
funding and as Zotero is for research outputs: they are edited on
https://orcid.org, and this tool only ever *reads* them. It has two modes:

  UPDATE (default)  Fetch the keywords and rewrite data/interests.json.
  CHECK  (--check)  Fetch them and verify the committed file is current;
                    exit 1 if it is stale.

The ORCID public API needs no key, so CI runs the very same code path with
`--check` — the same arrangement as tools/update-funding.py.

ORCID calls them Keywords; the website's hero pills and the CV's sidebar both
call them Interests, and both read this one file. Order is ORCID's own:
entries come back sorted by `display-index`, highest first, which is how ORCID
itself lists them. To reorder the pills, reorder them on ORCID.

If ORCID cannot be reached, staleness is *unknown* rather than proven: the tool
warns, checks the committed file is structurally sound, and succeeds, so an
outage never breaks a deploy.

SPDX-FileCopyrightText: Copyright © 2026 Idiap Research Institute <contact@idiap.ch>

SPDX-License-Identifier: BSD-3-Clause
"""

from __future__ import annotations

import argparse
import json
import sys
import time

import zotero_common as zc

SOURCE = f"orcid:{zc.ORCID_ID}/keywords"


def build_entries(payload: dict) -> list[str]:
    """The keyword strings from an ORCID ``/keywords`` payload, in ORCID's order.

    Parameters
    ----------
    payload
        The decoded ``/keywords`` response.

    Returns
    -------
    list of str
        Each keyword's ``content``, trimmed, blanks dropped, sorted by
        ``display-index`` descending. The sort is explicit rather than relying
        on the payload order, so `--check` never reports drift that is really
        just ORCID serialising in a different order.
    """
    keywords = payload.get("keyword") or []
    ordered = sorted(
        keywords, key=lambda k: k.get("display-index") or 0, reverse=True
    )
    return [c for c in ((k.get("content") or "").strip() for k in ordered) if c]


def sound_entries() -> list[str] | None:
    """The committed interests, or None (having said why) when the file is
    missing, unreadable, or empty."""
    rel = zc.INTERESTS_FILE.relative_to(zc.ROOT)
    if not zc.INTERESTS_FILE.exists():
        print(f"! {rel} is missing — run `pixi run interests` and commit it.",
              file=sys.stderr)
        return None
    try:
        entries = json.loads(zc.INTERESTS_FILE.read_text()).get("entries", [])
    except json.JSONDecodeError as exc:
        print(f"! {rel} is not valid JSON: {exc}", file=sys.stderr)
        return None
    if not entries:
        print(f"! {rel} has no entries.", file=sys.stderr)
        return None
    return entries


def do_check(fresh: list[str]) -> int:
    """Verify the committed file matches ORCID; report every difference."""
    rel = zc.INTERESTS_FILE.relative_to(zc.ROOT)
    entries = sound_entries()
    if entries is None:
        return 1

    if entries == fresh:
        print(f"{rel} is up to date ({len(entries)} interests).")
        return 0

    print(f"\n! {rel} is STALE ({len(entries)} committed, {len(fresh)} on ORCID):",
          file=sys.stderr)
    for k in fresh:
        if k not in entries:
            print(f"    + {k}", file=sys.stderr)
    for k in entries:
        if k not in fresh:
            print(f"    - {k}", file=sys.stderr)
    if set(entries) == set(fresh):
        print(f"    ~ order changed: {entries} -> {fresh}", file=sys.stderr)
    print("\n  Run `pixi run interests` and commit the result.", file=sys.stderr)
    return 1


def do_update(fresh: list[str]) -> int:
    """Rewrite data/interests.json from a fresh fetch."""
    rel = zc.INTERESTS_FILE.relative_to(zc.ROOT)
    if not fresh:
        print("! ORCID returned no keywords; keeping the committed file.",
              file=sys.stderr)
        return 0
    zc.DATA_DIR.mkdir(parents=True, exist_ok=True)
    zc.INTERESTS_FILE.write_text(
        json.dumps(
            {
                "generated": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                "source": SOURCE,
                "count": len(fresh),
                "entries": fresh,
            },
            indent=2,
            ensure_ascii=False,
        )
        + "\n"
    )
    print(f"Wrote {rel}: {len(fresh)} interests ({', '.join(fresh)}).")
    return 0


def offline(exc: Exception) -> int:
    """Unreachable ORCID proves nothing about freshness — validate and pass."""
    print(f"! ORCID unreachable ({exc}); cannot verify freshness.", file=sys.stderr)
    entries = sound_entries()
    if entries is None:
        return 1
    print(f"  Committed file looks sound: {len(entries)} interests. Proceeding.",
          file=sys.stderr)
    return 0


def main() -> int:
    """Parse arguments, fetch ORCID, and update or check. Returns an exit code."""
    p = argparse.ArgumentParser(
        prog="update-interests",
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    mode = p.add_mutually_exclusive_group()
    mode.add_argument("--check", action="store_true",
                      help="only verify that data/interests.json is current; never write")
    mode.add_argument("--update", action="store_true",
                      help="rewrite data/interests.json (the default)")
    args = p.parse_args()

    try:
        fresh = build_entries(zc.fetch_orcid_keywords())
    except Exception as exc:  # noqa: BLE001 — any network/HTTP failure is "unknown"
        return offline(exc)

    return do_check(fresh) if args.check else do_update(fresh)


if __name__ == "__main__":
    raise SystemExit(main())
