#!/usr/bin/env python3
"""Keep data/funding.json in step with the ORCID record's funding section.

ORCID is the source of truth for funding, exactly as Zotero is for research
outputs: grants are entered and curated on https://orcid.org, and this tool only
ever *reads* them. It has two modes:

  UPDATE (default)  Fetch the funding items and rewrite data/funding.json.
  CHECK  (--check)  Fetch them and verify the committed file is current;
                    exit 1 if it is stale.

Unlike the Zotero tooling there is no credential to switch on — the ORCID public
API needs no key — so CI runs the very same code path with `--check`.

Two ORCID quirks shape the code:

  * The `/fundings` summary endpoint omits the amount, the abstract and the
    funding instrument, and ORCID has no bulk funding endpoint, so each grant
    costs one extra request.
  * A grant asserted by both André and a third party (Dimensions, say) appears
    twice inside one group. ORCID groups by grant identifier, so we keep the
    self-asserted summary and drop the rest.

If ORCID cannot be reached, staleness is *unknown* rather than proven: the tool
warns, checks the committed file is structurally sound, and succeeds, so an
outage never breaks a deploy.

SPDX-FileCopyrightText: Copyright © 2026 Idiap Research Institute <contact@idiap.ch>

SPDX-License-Identifier: BSD-3-Clause
"""

from __future__ import annotations

import argparse
import collections.abc
import json
import sys
import time

import zotero_common as zc

SOURCE = f"orcid:{zc.ORCID_ID}/fundings"


def log(verbose: bool, msg: str) -> None:
    """Write a progress line to stderr when running verbosely."""
    if verbose:
        print(msg, file=sys.stderr)


# --------------------------------------------------------------------------- #
# Pure parsing — everything below is testable without a network.
# --------------------------------------------------------------------------- #
def pick_summary(group: dict) -> dict | None:
    """Choose the one summary to keep out of an ORCID funding group.

    A group collects every assertion of the same grant. André's own assertion
    carries the titles he wrote, so it wins over any third-party one.

    Parameters
    ----------
    group
        One entry of the ``/fundings`` payload's ``group`` list.

    Returns
    -------
    dict or None
        The preferred ``funding-summary``, or None for an empty group.
    """
    summaries = group.get("funding-summary") or []
    for s in summaries:
        source = (s.get("source") or {}).get("source-orcid") or {}
        if source.get("path") == zc.ORCID_ID:
            return s
    return summaries[0] if summaries else None


def year_month(date: dict | None) -> str | None:
    """Render an ORCID fuzzy date as ``YYYY-MM``, ``YYYY``, or None.

    ORCID stores year, month and day as separately-nullable fields; funding
    dates in practice carry a month but no day.

    Parameters
    ----------
    date
        An ORCID ``start-date``/``end-date`` object, or None.

    Returns
    -------
    str or None
        ``"2028-02"`` when the month is known, ``"2028"`` when it is not, and
        None when there is no year at all.
    """
    if not date:
        return None
    year = ((date.get("year") or {}) or {}).get("value")
    if not year:
        return None
    month = ((date.get("month") or {}) or {}).get("value")
    return f"{year}-{month}" if month else str(year)


def _self_external_id(detail: dict) -> dict:
    """The grant's own identifier record (``external-id-relationship: self``)."""
    for eid in (detail.get("external-ids") or {}).get("external-id", []):
        if (eid.get("external-id-relationship") or "self") == "self":
            return eid
    return {}


def build_entry(detail: dict) -> dict:
    """Reduce one ORCID funding record to the fields the site renders.

    Parameters
    ----------
    detail
        A ``/funding/{put_code}`` payload.

    Returns
    -------
    dict
        Keys: ``put_code``, ``title``, ``type``, ``instrument``, ``funder``,
        ``start``, ``end``, ``amount``, ``currency``, ``url``,
        ``grant_number``, ``description``. Everything but ``put_code``,
        ``title``, ``type`` and ``funder`` may be None.
    """
    eid = _self_external_id(detail)
    amount = detail.get("amount") or {}
    description = (detail.get("short-description") or "").strip()
    return {
        "put_code": detail.get("put-code"),
        "title": (((detail.get("title") or {}).get("title") or {}) or {}).get("value"),
        "type": (detail.get("type") or "").lower().replace("_", "-") or None,
        # ORCID's "organization defined type" is the funder's own name for the
        # instrument: Agora, CHIST-ERA, Lead Agency, Innovation check, ...
        "instrument": ((detail.get("organization-defined-type") or {}) or {}).get("value"),
        "funder": (detail.get("organization") or {}).get("name"),
        "start": year_month(detail.get("start-date")),
        "end": year_month(detail.get("end-date")),
        "amount": float(amount["value"]) if amount.get("value") else None,
        "currency": amount.get("currency-code"),
        # The grant's official page: ORCID's own `url` when set, else the
        # identifier's resolver (this is where the SNSF grant links come from).
        "url": ((detail.get("url") or {}) or {}).get("value")
        or ((eid.get("external-id-url") or {}) or {}).get("value"),
        "grant_number": eid.get("external-id-value"),
        "description": description or None,
    }


def sort_entries(entries: list[dict]) -> list[dict]:
    """Order grants by closing date, most recent first.

    A grant with no end date falls back to its start date, and one with neither
    sorts last. Ties break on the title so the order is deterministic.

    Parameters
    ----------
    entries
        Entries as built by :func:`build_entry`.

    Returns
    -------
    list[dict]
        The same entries, sorted. ``YYYY-MM`` and ``YYYY`` compare correctly as
        strings because the year is a fixed-width prefix.
    """
    entries.sort(key=lambda e: (e.get("title") or "").lower())
    entries.sort(key=lambda e: (e.get("end") or e.get("start") or ""), reverse=True)
    return entries


def build_entries(
    payload: dict,
    fetch: collections.abc.Callable[[int | str], dict] = zc.fetch_orcid_funding,
    verbose: bool = False,
) -> list[dict]:
    """Turn the ``/fundings`` payload into the site's sorted entry list.

    Parameters
    ----------
    payload
        The ``/fundings`` payload, as returned by
        :func:`zotero_common.fetch_orcid_fundings`.
    fetch
        How to retrieve one funding detail record by put-code. Injected so the
        tests can run offline.
    verbose
        Narrate every grant to stderr as it is retrieved.

    Returns
    -------
    list[dict]
        One entry per grant, deduplicated and sorted.
    """
    entries = []
    for group in payload.get("group", []):
        summary = pick_summary(group)
        if summary is None:
            continue
        entry = build_entry(fetch(summary["put-code"]))
        log(verbose, f"  {entry['start'] or '????'}–{entry['end'] or '????'}  "
                     f"{(entry['funder'] or '')[:28]:28s} {(entry['title'] or '')[:50]}")
        entries.append(entry)
    return sort_entries(entries)


# --------------------------------------------------------------------------- #
# Modes
# --------------------------------------------------------------------------- #
def sound_entries() -> list[dict] | None:
    """The committed entries, or None (having said why) if unusable."""
    rel = zc.FUNDING_FILE.relative_to(zc.ROOT)
    if not zc.FUNDING_FILE.exists():
        print(f"! {rel} is missing — run `pixi run funding` and commit it.",
              file=sys.stderr)
        return None
    try:
        entries = json.loads(zc.FUNDING_FILE.read_text()).get("entries", [])
    except json.JSONDecodeError as exc:
        print(f"! {rel} is not valid JSON: {exc}", file=sys.stderr)
        return None
    if not entries:
        print(f"! {rel} has no entries.", file=sys.stderr)
        return None
    return entries


def compare(committed: list[dict], fresh: list[dict]) -> tuple[list, list, list]:
    """(added, removed, changed) put-codes between the committed file and ORCID.

    Set-based, so it explains *what* differs; the caller has already
    established *that* something differs by comparing the ordered lists, and
    reports a pure reordering when all three come back empty.
    """
    cm = {e["put_code"]: e for e in committed}
    fm = {e["put_code"]: e for e in fresh}
    changed = []
    for pc in sorted(cm.keys() & fm.keys()):
        a, b = cm[pc], fm[pc]
        fields = sorted(f for f in set(a) | set(b) if a.get(f) != b.get(f))
        if fields:
            changed.append((pc, fields, a, b))
    return sorted(fm.keys() - cm.keys()), sorted(cm.keys() - fm.keys()), changed


def do_check(fresh: list[dict], verbose: bool) -> int:
    """Verify the committed file matches ORCID; report every difference."""
    rel = zc.FUNDING_FILE.relative_to(zc.ROOT)
    entries = sound_entries()
    if entries is None:
        return 1

    if entries == fresh:
        print(f"{rel} is up to date ({len(entries)} grants).")
        return 0

    added, removed, changed = compare(entries, fresh)
    print(f"\n! {rel} is STALE ({len(entries)} committed, {len(fresh)} on ORCID):",
          file=sys.stderr)
    by_pc = {e["put_code"]: e for e in fresh}
    for pc in added:
        print(f"    + {pc}  {(by_pc[pc]['title'] or '')[:62]}", file=sys.stderr)
    for pc in removed:
        print(f"    - {pc}", file=sys.stderr)
    for pc, fields, a, b in changed:
        print(f"    ~ {pc}  ({', '.join(fields)})", file=sys.stderr)
        if verbose:
            for f in fields:
                print(f"        {f}: {a.get(f)!r} -> {b.get(f)!r}", file=sys.stderr)
    if not (added or removed or changed):
        print("    ~ order changed", file=sys.stderr)
    print("\n  Run `pixi run funding` and commit the result."
          "\n  (Re-run with --verbose to see the changed values.)", file=sys.stderr)
    return 1


def do_update(fresh: list[dict]) -> int:
    """Rewrite data/funding.json from a fresh fetch."""
    rel = zc.FUNDING_FILE.relative_to(zc.ROOT)
    if not fresh:
        print("! ORCID returned no funding items; keeping the committed file.",
              file=sys.stderr)
        return 0
    zc.DATA_DIR.mkdir(parents=True, exist_ok=True)
    zc.FUNDING_FILE.write_text(
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
    with_amount = sum(1 for e in fresh if e.get("amount"))
    with_url = sum(1 for e in fresh if e.get("url"))
    print(f"Wrote {rel}: {len(fresh)} grants "
          f"({with_amount} with an amount, {with_url} with an official link).")
    return 0


def offline(exc: Exception) -> int:
    """Unreachable ORCID proves nothing about freshness — validate and pass."""
    print(f"! ORCID unreachable ({exc}); cannot verify freshness.", file=sys.stderr)
    entries = sound_entries()
    if entries is None:
        return 1
    print(f"  Committed file looks sound: {len(entries)} grants. Proceeding.",
          file=sys.stderr)
    return 0


def main() -> int:
    """Parse arguments, fetch ORCID, and update or check. Returns an exit code."""
    p = argparse.ArgumentParser(
        prog="update-funding",
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    mode = p.add_mutually_exclusive_group()
    mode.add_argument("--check", action="store_true",
                      help="only verify that data/funding.json is current; never write")
    mode.add_argument("--update", action="store_true",
                      help="rewrite data/funding.json (the default)")
    p.add_argument("-v", "--verbose", action="store_true",
                   help="narrate every grant as it is retrieved")
    args = p.parse_args()

    log(args.verbose, f"Fetching {SOURCE} ...")
    try:
        fresh = build_entries(zc.fetch_orcid_fundings(), verbose=args.verbose)
    except Exception as exc:  # noqa: BLE001 — any network/HTTP failure is "unknown"
        return offline(exc)

    return do_check(fresh, args.verbose) if args.check else do_update(fresh)


if __name__ == "__main__":
    raise SystemExit(main())
