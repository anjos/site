#!/usr/bin/env python3
"""Keep data/outputs.json in step with the Zotero "My Publications" library.

Zotero is the source of truth. This tool has two modes, chosen by whether a
Zotero API key is configured (~/.config/pyzotero.toml or $ZOTERO_API_KEY):

  UPDATE (key present)  Fetch the library and rewrite data/outputs.json.
  CHECK  (no key)       Fetch the public feed and verify the committed
                        data/outputs.json is current; exit 1 if it is stale.

Only one field needs the key: `related`, built from Zotero's `dc:relation`,
which the public feed does not expose. Everything else — including the
BetterBibTeX `citationKey` used as each entry's `key` — is public, so CHECK
verifies the whole file except `related`. That is what lets CI validate the data
without credentials, and why the generated file is committed rather than rebuilt
during the site build.

If Zotero cannot be reached, staleness is *unknown* rather than proven: the tool
warns, verifies the committed file is structurally sound, and succeeds, so a
Zotero outage never breaks a deploy.
"""

from __future__ import annotations

import argparse
import json
import sys
import time

import zotero_common as zc

IGNORED_IN_CHECK = ("related",)  # the only field the public feed cannot supply


def log(verbose: bool, msg: str) -> None:
    if verbose:
        print(msg, file=sys.stderr)


def narrate(entries: list[dict], verbose: bool) -> None:
    if not verbose:
        return
    for i, e in enumerate(entries, 1):
        pdf = " PDF" if e.get("pdf") else ""
        doi = f" doi:{e['doi']}" if e.get("doi") else ""
        print(f"  [{i:3d}/{len(entries)}] {e.get('year') or '????'} "
              f"{e.get('type', ''):16s} {e['key']:34s} {e['title'][:52]}{doi}{pdf}",
              file=sys.stderr)


def load_committed() -> dict | None:
    if not zc.OUTPUT_FILE.exists():
        return None
    try:
        return json.loads(zc.OUTPUT_FILE.read_text())
    except json.JSONDecodeError as exc:
        sys.exit(f"! {zc.OUTPUT_FILE.relative_to(zc.ROOT)} is not valid JSON: {exc}")


def compare(committed: list[dict], fresh: list[dict]) -> tuple[list, list, list]:
    """(added, removed, changed) between the committed entries and a fresh build.
    A renamed key surfaces as an add plus a remove, so key drift is caught too."""
    cm = {e["key"]: e for e in committed}
    fm = {e["key"]: e for e in fresh}
    changed = []
    for key in sorted(cm.keys() & fm.keys()):
        a, b = cm[key], fm[key]
        fields = sorted(
            f for f in set(a) | set(b)
            if f not in IGNORED_IN_CHECK and a.get(f) != b.get(f)
        )
        if fields:
            changed.append((key, fields, a, b))
    return sorted(fm.keys() - cm.keys()), sorted(cm.keys() - fm.keys()), changed


def do_check(fresh: list[dict], verbose: bool) -> int:
    committed = load_committed()
    if committed is None:
        print(f"! {zc.OUTPUT_FILE.relative_to(zc.ROOT)} is missing — run "
              "`pixi run outputs` with a Zotero API key and commit it.", file=sys.stderr)
        return 1

    entries = committed.get("entries", [])
    try:
        zc.assert_unique_keys(entries)
    except ValueError as exc:
        print(f"! committed file has {exc}", file=sys.stderr)
        return 1

    added, removed, changed = compare(entries, fresh)
    if not (added or removed or changed):
        print(f"data/outputs.json is up to date ({len(entries)} entries).")
        return 0

    print(f"\n! data/outputs.json is STALE ({len(entries)} committed, "
          f"{len(fresh)} in Zotero):", file=sys.stderr)
    by_key = {e["key"]: e for e in fresh}
    for k in added:
        print(f"    + {k}  {by_key[k]['title'][:62]}", file=sys.stderr)
    for k in removed:
        print(f"    - {k}", file=sys.stderr)
    for k, fields, a, b in changed:
        print(f"    ~ {k}  ({', '.join(fields)})", file=sys.stderr)
        if verbose:
            for f in fields:
                print(f"        {f}: {a.get(f)!r} -> {b.get(f)!r}", file=sys.stderr)
    print("\n  Run `pixi run outputs` with a Zotero API key and commit the result."
          "\n  (Re-run with --verbose to see the changed values.)", file=sys.stderr)
    return 1


def do_update(fresh: list[dict], user_id: str) -> int:
    if not fresh:
        print("! Zotero returned no publications; keeping the committed file.",
              file=sys.stderr)
        return 0
    zc.DATA_DIR.mkdir(parents=True, exist_ok=True)
    zc.OUTPUT_FILE.write_text(
        json.dumps(
            {
                "generated": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                "source": f"zotero:users/{user_id}/publications",
                "count": len(fresh),
                "entries": fresh,
            },
            indent=2,
            ensure_ascii=False,
        )
        + "\n"
    )
    with_pdf = sum(1 for e in fresh if e.get("pdf"))
    with_doi = sum(1 for e in fresh if e.get("doi"))
    with_rel = sum(1 for e in fresh if e.get("related"))
    print(f"Wrote {zc.OUTPUT_FILE.relative_to(zc.ROOT)}: {len(fresh)} entries "
          f"({with_doi} with DOI, {with_pdf} with public PDF, {with_rel} with relations).")
    return 0


def offline(exc: Exception) -> int:
    """Unreachable Zotero proves nothing about freshness. Validate what we can
    and succeed, so an upstream outage never breaks the build."""
    print(f"! Zotero unreachable ({exc}); cannot verify freshness.", file=sys.stderr)
    committed = load_committed()
    if committed is None:
        print(f"! and {zc.OUTPUT_FILE.relative_to(zc.ROOT)} is missing.", file=sys.stderr)
        return 1
    entries = committed.get("entries", [])
    if not entries:
        print("! committed file has no entries.", file=sys.stderr)
        return 1
    try:
        zc.assert_unique_keys(entries)
    except ValueError as exc2:
        print(f"! committed file has {exc2}", file=sys.stderr)
        return 1
    print(f"  Committed file looks sound: {len(entries)} entries, unique keys. "
          "Proceeding.", file=sys.stderr)
    return 0


def main() -> int:
    p = argparse.ArgumentParser(
        prog="update-site-outputs",
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    mode = p.add_mutually_exclusive_group()
    mode.add_argument("--check", action="store_true",
                      help="only verify that data/outputs.json is current; never write "
                           "(forced default when no API key is configured)")
    mode.add_argument("--update", action="store_true",
                      help="rewrite data/outputs.json; requires an API key")
    p.add_argument("-v", "--verbose", action="store_true",
                   help="narrate every entry as it is retrieved and built")
    args = p.parse_args()

    user_id = zc.read_user_id()
    api_key = zc._config("api_key", "ZOTERO_API_KEY")
    if args.update and not api_key:
        print("! --update needs a Zotero API key: put `api_key = \"…\"` in "
              f"{zc.CONFIG_FILE} (chmod 600) or set $ZOTERO_API_KEY.", file=sys.stderr)
        return 2
    checking = args.check or not api_key

    where = "$ZOTERO_API_KEY" if not zc.CONFIG_FILE.exists() else str(zc.CONFIG_FILE)
    print(f"Zotero API key: {'found (' + where + ')' if api_key else 'absent'}"
          f" -> {'CHECK' if checking else 'UPDATE'} mode"
          f"{' (relations not verifiable)' if checking else ''}", file=sys.stderr)

    log(args.verbose, f"Fetching public feed for user {user_id} ...")
    try:
        items = zc.fetch_public_items(user_id)
    except Exception as exc:  # noqa: BLE001 — any network/HTTP failure is "unknown"
        return offline(exc)
    log(args.verbose, f"  {len(items)} items (entries + public attachments).")

    # Relations need the key, and are deliberately not fetched in check mode: they
    # are the one thing CHECK cannot verify, so it must not depend on them either.
    relmap = None
    if not checking:
        log(args.verbose, "Fetching dc:relation links (authenticated) ...")
        relmap = zc.fetch_relations(user_id)

    try:
        fresh = zc.build_entries(items, user_id, relmap)
    except ValueError as exc:
        print(f"! Zotero data has {exc}", file=sys.stderr)
        return 1
    narrate(fresh, args.verbose)

    return do_check(fresh, args.verbose) if checking else do_update(fresh, user_id)


if __name__ == "__main__":
    raise SystemExit(main())
