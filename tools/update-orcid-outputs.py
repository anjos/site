#!/usr/bin/env python3
"""Compare Zotero "My Publications" (source of truth) with the ORCID record and
write a to-do report. It NEVER writes to ORCID (that needs the paid Member API)
and NEVER proposes deletions — ORCID-only works are just reported.

Output: orcid-sync-report.md with three sections —
  1. Missing on ORCID   — Zotero works absent from ORCID (add them by hand).
  2. Outdated / incomplete — matched works where ORCID lacks what Zotero has
     (DOI, public-PDF link, work-type, venue, year) as a field-level table.
  3. On ORCID, not in Zotero — reported only; decide for yourself.

    python tools/update-orcid-outputs.py       # (aka `pixi run orcid-report`)
"""

from __future__ import annotations

import sys
import time

import zotero_common as zc

REPORT = zc.ROOT / "orcid-sync-report.md"


def zotero_records(user_id: str) -> list[dict]:
    """Rich per-work records from Zotero for the ORCID comparison."""
    items = zc.fetch_public_items(user_id)
    pdf_by_parent: dict[str, str] = {}
    for it in items:
        d = it["data"]
        if d.get("itemType") == "attachment" and d.get("contentType") == "application/pdf":
            pdf_by_parent.setdefault(d.get("parentItem"), it["key"])
    recs = []
    for it in items:
        d = it["data"]
        if d.get("itemType") in ("attachment", "note"):
            continue
        year, _ = zc.parsed_date(d, it.get("meta", {}))
        doi = zc.normalize_doi(d.get("DOI"))
        pdf = zc.public_pdf_url(user_id, pdf_by_parent[it["key"]]) if it["key"] in pdf_by_parent else None
        recs.append({
            "title": (d.get("title") or "").strip(),
            "slug": zc.slug_title(d.get("title") or ""),
            "doi": doi,
            "orcid_type": zc.orcid_type(d.get("itemType", "")),
            "container": zc.venue_of(d),
            "year": year,
            "url": d.get("url") or (f"https://doi.org/{doi}" if doi else None),
            "pdf": pdf,
        })
    return recs


def match(zrec: dict, by_doi: dict, by_title: dict):
    if zrec["doi"] and zrec["doi"] in by_doi:
        return by_doi[zrec["doi"]]
    return by_title.get(zrec["slug"])


def field_diffs(z: dict, o: dict) -> list[tuple[str, str, str]]:
    """(field, 'ORCID has', 'Zotero has') rows where ORCID should catch up."""
    rows = []
    if z["doi"] and not o.get("doi"):
        rows.append(("DOI", "—", z["doi"]))
    if z["pdf"] and not o.get("url"):
        rows.append(("URL (public PDF)", "—", z["pdf"]))
    if z["orcid_type"] and o.get("type") and o["type"] != z["orcid_type"]:
        rows.append(("work-type", o["type"], z["orcid_type"]))
    if z["container"] and not o.get("container"):
        rows.append(("venue", "—", z["container"]))
    if z["year"] and o.get("year") and o["year"] != z["year"]:
        rows.append(("year", str(o["year"]), str(z["year"])))
    return rows


def main() -> int:
    user_id = zc.read_user_id()
    try:
        zrecs = zotero_records(user_id)
        orcid = zc.parse_orcid_works(zc.fetch_orcid_works())
    except Exception as exc:  # noqa: BLE001
        print(f"! fetch failed: {exc}", file=sys.stderr)
        return 1

    by_doi = {o["doi"]: o for o in orcid if o.get("doi")}
    by_title = {zc.slug_title(o["title"]): o for o in orcid if o.get("title")}

    missing, outdated = [], []
    matched_orcid = set()
    for z in zrecs:
        o = match(z, by_doi, by_title)
        if o is None:
            missing.append(z)
            continue
        matched_orcid.add(id(o))
        diffs = field_diffs(z, o)
        if diffs:
            outdated.append((z, diffs))
    orphan = [o for o in orcid if id(o) not in matched_orcid]

    lines = ["# ORCID sync report", "",
             f"Zotero works: {len(zrecs)} · ORCID works: {len(orcid)} · "
             f"generated {time.strftime('%Y-%m-%d %H:%M UTC', time.gmtime())}",
             "",
             "Zotero is the source of truth. Apply the items below on your ORCID "
             "record by hand (ORCID writes need the paid Member API). Nothing here "
             "deletes anything.", ""]

    lines += [f"## 1. Missing on ORCID ({len(missing)})", ""]
    if missing:
        lines += ["| Year | Type | Title | DOI | Public PDF |",
                  "|---|---|---|---|---|"]
        for z in sorted(missing, key=lambda x: (x["year"] or 0), reverse=True):
            lines.append(f"| {z['year'] or '—'} | {z['orcid_type']} | {z['title'][:70]} "
                         f"| {z['doi'] or '—'} | {z['pdf'] or '—'} |")
    else:
        lines.append("_Nothing missing — every Zotero work is on ORCID._")
    lines.append("")

    lines += [f"## 2. Outdated / incomplete on ORCID ({len(outdated)})", ""]
    if outdated:
        lines += ["| Work | Field | ORCID has | Zotero has |",
                  "|---|---|---|---|"]
        for z, diffs in sorted(outdated, key=lambda x: (x[0]["year"] or 0), reverse=True):
            for i, (field, has, want) in enumerate(diffs):
                title = z["title"][:50] if i == 0 else ""
                lines.append(f"| {title} | {field} | {has} | {want} |")
    else:
        lines.append("_All matched ORCID works already carry the Zotero metadata._")
    lines.append("")

    lines += [f"## 3. On ORCID, not in Zotero ({len(orphan)}) — review only", ""]
    if orphan:
        lines += ["_Reported, never deleted. Add to Zotero if they belong, or leave as-is._", "",
                  "| Year | Title | DOI |", "|---|---|---|"]
        for o in sorted(orphan, key=lambda x: (x["year"] or 0), reverse=True):
            lines.append(f"| {o['year'] or '—'} | {(o['title'] or '')[:70]} | {o['doi'] or '—'} |")
    else:
        lines.append("_Every ORCID work matches a Zotero work._")
    lines.append("")

    REPORT.write_text("\n".join(lines))
    print(f"Wrote {REPORT.relative_to(zc.ROOT)}")
    print(f"  missing on ORCID:      {len(missing)}")
    print(f"  outdated/incomplete:   {len(outdated)}")
    print(f"  on ORCID not in Zotero:{len(orphan)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
