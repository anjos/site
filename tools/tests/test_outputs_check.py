"""Tests for the update-or-check behaviour of tools/update-site-outputs.py.

The drift tests are offline and fixture-based. The last one talks to the Zotero
*public* feed to keep make_key() honest against the real BetterBibTeX keys; it
skips itself when the network is unavailable.
"""

import importlib.util
import pathlib
import re
import sys

import pytest

TOOLS = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(TOOLS))

import zotero_common as zc  # noqa: E402

# The script has a dash in its name, so it cannot be imported by name.
_spec = importlib.util.spec_from_file_location("uso", TOOLS / "update-site-outputs.py")
uso = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(uso)


def entry(key="anjos_fair_2026", **over):
    e = {"key": key, "title": "Fair Foundation Models", "year": 2026,
         "doi": "10.1145/3793542", "type": "Conference Paper", "related": []}
    e.update(over)
    return e


def test_no_drift():
    assert uso.compare([entry()], [entry()]) == ([], [], [])


def test_changed_field_is_reported():
    added, removed, changed = uso.compare([entry()], [entry(title="Renamed")])
    assert (added, removed) == ([], [])
    assert changed[0][0] == "anjos_fair_2026" and changed[0][1] == ["title"]


def test_tampered_key_shows_as_add_and_remove():
    """A key rename cannot hide: it leaves the old key missing and a new one
    unaccounted for."""
    added, removed, changed = uso.compare([entry(key="TAMPERED")], [entry()])
    assert added == ["anjos_fair_2026"] and removed == ["TAMPERED"] and changed == []


def test_related_is_not_compared():
    """`related` comes from dc:relation, which the public feed cannot supply, so
    check mode must ignore it — otherwise every keyless run would report drift."""
    committed = [entry(related=[{"type": "Preprint", "doi": "10.1/x", "href": None}])]
    assert uso.compare(committed, [entry(related=[])]) == ([], [], [])


def test_added_and_removed_entries():
    added, removed, _ = uso.compare([entry(key="gone_2020")], [entry(key="new_2026")])
    assert added == ["new_2026"] and removed == ["gone_2020"]


def test_bbt_key_parity():
    """make_key() must reproduce Zotero's BetterBibTeX base key for every real
    entry. It is only a fallback today, but this is what stops it drifting into
    something that would generate different keys the day it is needed."""
    try:
        items = zc.fetch_public_items(zc.read_user_id())
    except Exception as exc:  # noqa: BLE001
        pytest.skip(f"Zotero public feed unavailable: {exc}")

    tops = [i for i in items if i["data"].get("itemType") not in ("attachment", "note")]
    if not any(t["data"].get("citationKey") for t in tops):
        pytest.skip("no citationKey in the feed to compare against")

    mismatches = []
    for t in tops:
        d = t["data"]
        bbt = d.get("citationKey")
        if not bbt:
            continue
        # strip BBT's own a/b/c suffix: its ordering comes from dateAdded, which
        # the public feed does not expose, so only the base key is comparable.
        base = re.sub(r"(?<=\d{4})[a-z]$", "", bbt)
        got = zc.make_key(zc.build_site_entry(t, None, "5992358"), d.get("creators"))
        if got != base:
            mismatches.append(f"{got} != {bbt}  ({d.get('title', '')[:50]})")
    assert not mismatches, "make_key drifted from BetterBibTeX:\n  " + "\n  ".join(mismatches)
