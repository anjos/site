#!/usr/bin/env python3
"""Edit fields on an EXISTING Zotero "My Publications" item (add / update / delete).

Companion to add_zotero_output.py (which only *creates*). Identify the item by DOI
or Zotero item key, then set/clear top-level fields and add/update/delete labeled
lines in the `extra` block (e.g. a paper's `Software:` companion-code link).

Use it only on André's explicit request/approval — it writes to the live library.
Needs a read-write key in ~/.config/pyzotero.toml (api_key + user_id).

    # preview: set a paper's Homepage (paper page) + a Software companion-code line
    python tools/edit_zotero_item.py --doi 10.1038/s41598-026-46069-w \\
        --set-extra Homepage=https://medai.pages.idiap.ch/.../uveai \\
        --set-extra Software=https://gitlab.idiap.ch/.../uveai-validation --dry-run

    # remove a labeled extra line, or clear a top-level field
    python tools/edit_zotero_item.py --key ABCD1234 --del-extra Software
    python tools/edit_zotero_item.py --key ABCD1234 --del url

After writing, run `pixi run outputs` to refresh data/outputs.json.
"""

from __future__ import annotations

import argparse
import sys

import zotero_common as zc


def find_item(zot, uid: str, doi: str | None, key: str | None):
    """The live (authenticated) item, by key or by DOI lookup in My Publications."""
    if key:
        try:
            return zot.item(key)
        except Exception:  # noqa: BLE001 - not found / bad key
            return None
    nd = zc.normalize_doi(doi)
    for it in zc.fetch_public_items(uid):
        if zc.normalize_doi(it["data"].get("DOI")) == nd:
            return zot.item(it["key"])
    return None


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    who = ap.add_mutually_exclusive_group(required=True)
    who.add_argument("--doi")
    who.add_argument("--key", help="Zotero item key")
    ap.add_argument("--set-url", dest="set_url",
                    help="set the top-level url (e.g. a software repo). NOT the paper page — "
                    "that is `--set-extra Homepage=…`.")
    ap.add_argument("--set", dest="sets", action="append", default=[], metavar="FIELD=VALUE",
                    help="set any top-level field (repeatable)")
    ap.add_argument("--del", dest="dels", action="append", default=[], metavar="FIELD",
                    help="clear a top-level field (repeatable)")
    ap.add_argument("--set-extra", dest="set_extra", action="append", default=[],
                    metavar="LABEL=VALUE", help="add/update a labeled `extra` line (repeatable)")
    ap.add_argument("--del-extra", dest="del_extra", action="append", default=[],
                    metavar="LABEL", help="remove a labeled `extra` line (repeatable)")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()

    from pyzotero import zotero
    uid, key = zc.read_credentials()
    zot = zotero.Zotero(uid, "user", key)

    item = find_item(zot, uid, a.doi, a.key)
    if not item:
        sys.exit(f"item not found ({a.doi or a.key})")
    data = item["data"]
    print(f"[{item['key']}] {data.get('itemType')}: {(data.get('title') or '')[:70]}")

    changes: list[tuple[str, object, object]] = []
    sets = list(a.sets)
    if a.set_url is not None:
        sets.append(f"url={a.set_url}")
    for kv in sets:
        f, _, v = kv.partition("=")
        f = f.strip()
        if data.get(f) != v:
            changes.append((f, data.get(f), v))
            data[f] = v
    for f in a.dels:
        f = f.strip()
        if data.get(f):
            changes.append((f, data.get(f), ""))
            data[f] = ""

    extra = data.get("extra", "")
    for kv in a.set_extra:
        lbl, _, v = kv.partition("=")
        extra = zc.set_extra_field(extra, lbl.strip(), v.strip())
    for lbl in a.del_extra:
        extra = zc.del_extra_field(extra, lbl.strip())
    if extra != data.get("extra", ""):
        changes.append(("extra", data.get("extra", ""), extra))
        data["extra"] = extra

    if not changes:
        print("  no changes.")
        return 0
    for f, old, new in changes:
        print(f"  {f}: {old!r} -> {new!r}")
    if a.dry_run:
        print("(dry-run; nothing written)")
        return 0
    zot.update_item(data)
    print("  -> updated. Run `pixi run outputs` to refresh the site.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
