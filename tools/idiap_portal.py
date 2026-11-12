#!/usr/bin/env python3
"""Keep recent papers mirrored on Idiap's publication portal.

Idiap's funding reports are built from its own publication database, not from
Zotero or ORCID, so every recent paper on the CV must also be entered there —
with a funding project and research programs ticked, which is what attributes
it. The database has two faces:

* https://publidiap.idiap.ch — the editable one, reachable only on the Idiap
  intranet or VPN (`idiap-vpn`), signed in with the Idiap login;
* https://publications.idiap.ch — a public, read-only copy, refreshed from the
  former once an hour.

This tool only ever reads the public copy, so it needs no VPN and no login:

* the default mode **checks** that every journal, conference and chapter paper
  of the last :data:`RECENT_YEARS` calendar years in ``data/outputs.json`` is on
  the portal (DOI first, then a normalised title), and warns about records there
  that carry no project or no main research program;
* ``--prepare KEY`` **prints the form** for one work: each portal field, the
  projects and programs its sibling papers already carry on the portal, and
  Zotero's own BibTeX.

An unreachable portal warns and passes, as every other remote check here does.

SPDX-FileCopyrightText: Copyright © 2026 Idiap Research Institute <contact@idiap.ch>

SPDX-License-Identifier: BSD-3-Clause
"""

from __future__ import annotations

import argparse
import calendar
import collections
import datetime
import html
import json
import re
import sys
import unicodedata

import validate_content
import zotero_common

PORTAL = "https://publications.idiap.ch"
EDIT_PORTAL = "https://publidiap.idiap.ch"

#: André's author id on the portal (``/authors/show/921``).
AUTHOR_ID = 921

#: The same window as the CV's "last five years" donut (``tools/build-cv.py``).
RECENT_YEARS = 5

#: Site output types that must be on the portal, and the portal type to pick.
PAPER_TYPES = {
    "Journal Article": "Article (journal paper)",
    "Conference Paper": "Inproceedings (conference paper)",
    "Book Chapter": "Incollection (book chapter)",
}

#: Portal record types that never stand in for a paper: an Idiap-RR shares the
#: paper's title, and matching it would hide a paper that was never entered.
REPORT_TYPES = frozenset({"techreport"})


def _value(raw: str) -> str:
    """The value of one ``name = {value},`` field, outer delimiters removed."""
    v = raw.split("=", 1)[1].strip().rstrip(",").strip()
    return v[1:-1] if v[:1] in "{\"" else v


def parse_bibtex(text: str) -> list[dict[str, str]]:
    """Split a BibTeX dump into one flat dict per entry.

    Parameters
    ----------
    text
        BibTeX, possibly HTML-escaped and wrapped in a page, as the portal
        serves it.

    Returns
    -------
    list[dict[str, str]]
        Each entry's fields, lower-cased names, plus ``_type`` (lower-cased entry
        type) and ``_key`` (its citation key).
    """
    out = []
    for typ, key, body in re.findall(r"@(\w+)\{([^,]+),(.*?)\n\}", html.unescape(text), re.S):
        fields = {
            name.lower(): _value(raw)
            for name, raw in zotero_common._bibtex_fields(body)
        }
        out.append({"_type": typ.lower(), "_key": key.strip(), **fields})
    return out


def _fetch_portal() -> list[dict[str, str]]:
    """Every portal record of :data:`AUTHOR_ID`, from its BibTeX export.

    Returns
    -------
    list[dict[str, str]]
        Parsed records, as :func:`parse_bibtex` returns them.

    Raises
    ------
    requests.RequestException
        Any network or HTTP failure; the caller downgrades it to a warning.
    """
    import requests

    r = requests.post(
        f"{PORTAL}/export/author/{AUTHOR_ID}/bibtex",
        data={"formname": "export", "BibTeX": "BibTeX"},
        headers={"User-Agent": zotero_common.USER_AGENT},
        timeout=60,
    )
    r.raise_for_status()
    return parse_bibtex(r.text)


def find_record(entry: dict, records: list[dict[str, str]]) -> dict[str, str] | None:
    """The portal record for one site entry: same DOI, else same title.

    Parameters
    ----------
    entry
        One entry of ``data/outputs.json``.
    records
        Portal records, as :func:`parse_bibtex` returns them.

    Returns
    -------
    dict[str, str] | None
        The first matching record that is not a report, or None.
    """
    doi = zotero_common.normalize_doi(entry.get("doi"))
    title = zotero_common.slug_title(entry.get("title") or "")
    for r in records:
        if r["_type"] in REPORT_TYPES:
            continue
        if doi and zotero_common.normalize_doi(r.get("doi")) == doi:
            return r
        if title and zotero_common.slug_title(r.get("title", "")) == title:
            return r
    return None


def _since() -> int:
    """First calendar year of the recent window, inclusive."""
    return datetime.date.today().year - RECENT_YEARS + 1


def _entries() -> list[dict]:
    """The entries of ``data/outputs.json``."""
    return json.loads(zotero_common.OUTPUT_FILE.read_text())["entries"]


def check(entries: list[dict], records: list[dict[str, str]], since: int) -> list[str]:
    """Problems with the portal, in ``validate_content``'s message convention.

    Parameters
    ----------
    entries
        Site entries.
    records
        Portal records.
    since
        First year that must be mirrored.

    Returns
    -------
    list[str]
        One message per recent paper absent from the portal (fatal), and one
        ``WARN:`` per recent portal record lacking a project or main program.
    """
    errors = []
    for e in entries:
        if e["type"] in PAPER_TYPES and (e["year"] or 0) >= since and not find_record(e, records):
            errors.append(
                f"{e['key']} ({e['year']}, {e['type']}): \"{e['title']}\" is not on "
                f"{PORTAL} — `pixi run portal-entry {e['key']}`"
            )
    for r in records:
        year = int(re.sub(r"\D", "", r.get("year", "")) or 0)
        if r["_type"] in REPORT_TYPES or year < since:
            continue
        gaps = [f for f in ("projects", "mainresearchprogram") if not r.get(f)]
        if gaps:
            errors.append(f"WARN: {r['_key']} on the portal has no {' or '.join(gaps)}.")
    return errors


def _split(value: str | None) -> list[str]:
    """A comma-separated portal list field as clean items."""
    return [v.strip() for v in (value or "").split(",") if v.strip()]


def propose(entry: dict, entries: list[dict], records: list[dict[str, str]]):
    """Projects and programs the work's siblings already carry on the portal.

    A sibling is any other output listed on the same site project page(s). The
    site has no table from its projects to Idiap's, so the portal's own past
    choices for those siblings are the best available guess.

    Parameters
    ----------
    entry
        The site entry being prepared.
    entries
        All site entries, to resolve the pages' references.
    records
        Portal records.

    Returns
    -------
    tuple[list[str], dict[str, collections.Counter]]
        Names of the project pages that list the work, and a counter per portal
        field (``projects``, ``mainresearchprogram``,
        ``additionalresearchprograms``).
    """
    by_ref = {}
    for e in entries:
        for field in ("doi", "key"):
            if e.get(field):
                by_ref[e[field].lower()] = e
    mine = {r.lower() for r in (entry.get("doi"), entry.get("key")) if r}
    pages, counts = [], collections.defaultdict(collections.Counter)
    for page in sorted((zotero_common.ROOT / "content" / "projects").glob("*/index.md")):
        refs = {str(r).lower() for r in validate_content.parse_front_matter(page).get("research_outputs", [])}
        if not refs & mine:
            continue
        pages.append(page.parent.name)
        for ref in refs - mine:
            rec = find_record(by_ref[ref], records) if ref in by_ref else None
            for field in ("projects", "mainresearchprogram", "additionalresearchprograms"):
                counts[field].update(_split((rec or {}).get(field)))
    return pages, counts


def short_name(venue: str, alternates: list[str] | None = None) -> str | None:
    """A conference's short name: ``(ACRONYM)`` in its title, else a listed one.

    Parameters
    ----------
    venue
        The proceedings title, e.g. "2026 IEEE Congress on Evolutionary
        Computation (CEC)".
    alternates
        Other names for the venue, as Semantic Scholar lists them; the shortest
        all-capitals one is taken.

    Returns
    -------
    str | None
        The short name, or None when neither source has one.
    """
    m = re.search(r"\(([A-Z][A-Za-z0-9-]+)\)", venue or "")
    if m:
        return m.group(1)
    caps = [a for a in alternates or [] if re.fullmatch(r"[A-Z][A-Z0-9-]{1,15}", a)]
    return min(caps, key=len) if caps else None


def abstract_from_index(index: dict[str, list[int]] | None) -> str | None:
    """Rebuild a plain abstract from OpenAlex's ``abstract_inverted_index``.

    Parameters
    ----------
    index
        ``{word: [positions]}``, as OpenAlex stores abstracts.

    Returns
    -------
    str | None
        The abstract, or None if there is none.
    """
    if not index:
        return None
    return " ".join(w for _, w in sorted((p, w) for w, ps in index.items() for p in ps))


def _lookup(entry: dict) -> dict[str, object]:
    """Abstract and venue names for one work from OpenAlex and Semantic Scholar.

    Both are key-less and are looked up by DOI, or by title for a DOI-less work
    (accepted only when the normalised title matches exactly). Each source is
    best effort: a failure just leaves its fields out.

    Parameters
    ----------
    entry
        One entry of ``data/outputs.json``.

    Returns
    -------
    dict[str, object]
        ``abstracts`` (a list of ``(source, text)``, OpenAlex first),
        ``keywords`` (OpenAlex's, most relevant first) and ``alternates``
        (other names Semantic Scholar knows the venue by).
    """
    import requests

    doi, title = entry.get("doi"), entry.get("title") or ""
    slug = zotero_common.slug_title(title)
    headers = {"User-Agent": zotero_common.USER_AGENT}
    out: dict[str, object] = {"abstracts": [], "keywords": [], "alternates": []}

    def get(url: str, **params) -> dict:
        r = requests.get(url, params=params, headers=headers, timeout=30)
        r.raise_for_status()
        return r.json()

    try:
        if doi:
            work = get(f"https://api.openalex.org/works/doi:{doi}")
        else:
            hits = get("https://api.openalex.org/works", filter=f"title.search:{title}")["results"]
            work = next((w for w in hits if zotero_common.slug_title(w.get("title") or "") == slug), {})
        text = abstract_from_index(work.get("abstract_inverted_index"))
        if text:
            out["abstracts"].append(("OpenAlex", text))
        ranked = sorted(work.get("keywords") or [], key=lambda k: -k.get("score", 0))
        out["keywords"] = [k["display_name"] for k in ranked if k.get("display_name")]
    except Exception:  # best effort — the form then says where to look
        pass
    try:
        fields = "title,abstract,publicationVenue"
        if doi:
            paper = get(f"https://api.semanticscholar.org/graph/v1/paper/DOI:{doi}", fields=fields)
        else:
            hits = get("https://api.semanticscholar.org/graph/v1/paper/search/match", query=title, fields=fields)
            paper = next((p for p in hits.get("data", []) if zotero_common.slug_title(p.get("title") or "") == slug), {})
        if paper.get("abstract"):
            out["abstracts"].append(("Semantic Scholar", paper["abstract"]))
        out["alternates"] = (paper.get("publicationVenue") or {}).get("alternate_names") or []
    except Exception:
        pass
    return out


def prepare(
    key: str,
    entries: list[dict],
    records: list[dict[str, str]],
    zotero: dict[str, str],
    lookup: dict[str, object] | None = None,
) -> str:
    """The portal form for one work, as text to copy from.

    Parameters
    ----------
    key
        The work's citation key in ``data/outputs.json``.
    entries
        All site entries.
    records
        Portal records.
    zotero
        Zotero's BibTeX export, ``{citation key: entry}``.
    lookup
        What :func:`_lookup` found elsewhere, filling in an abstract or keywords
        Zotero lacks, and a short name the venue title does not carry.

    Returns
    -------
    str
        The filled-in form.

    Raises
    ------
    KeyError
        If ``key`` is not in ``data/outputs.json``.
    """
    entry = next((e for e in entries if e["key"] == key), None)
    if entry is None:
        raise KeyError(f"{key} is not in data/outputs.json — run `pixi run outputs`?")
    bib = (parse_bibtex(zotero.get(key, "")) or [{}])[0]
    venue = entry.get("container") or ""
    lookup = lookup or {}
    short = short_name(venue, lookup.get("alternates")) if entry["type"] == "Conference Paper" else None
    found = [("Zotero", bib["abstract"])] if bib.get("abstract") else []
    source, abstract = (found + list(lookup.get("abstracts") or []) + [(None, None)])[0]
    tags = _split(bib.get("keywords"))
    keywords = ("Zotero", tags) if tags else ("OpenAlex", lookup.get("keywords") or [])
    first = (bib.get("author", "").split(" and ")[0].split(",")[0] or "Author").strip("{} ")
    first = unicodedata.normalize("NFKD", first).encode("ascii", "ignore").decode()  # Idiap keys are ASCII
    pages, counts = propose(entry, entries, records)

    def top(field: str) -> str:
        c = counts.get(field)
        return ", ".join(f"{k} ({n})" for k, n in c.most_common()) if c else "— none seen, choose by hand"

    rows = [
        ("Type", PAPER_TYPES.get(entry["type"], f"{entry['type']} — not a paper type this check requires")),
        ("Status", "Published" if entry.get("doi") else "Accepted"),
        ("Citation", f"{first}_{short or '<VENUE>'}_{entry['year']}"),
        ("Title", entry["title"]),
        ("Authors", "; ".join(a.strip() for a in bib.get("author", "").split(" and ")) or ", ".join(entry["authors"])),
        ("Journal" if entry["type"] == "Journal Article" else "Booktitle", venue),
        ("Short name", (short or "— not found; take it from the call for papers") if entry["type"] == "Conference Paper" else ""),
        ("Year", str(entry["year"])),
        ("Month", calendar.month_name[entry["month"]] if entry.get("month") else "— unknown"),
        ("Volume", entry.get("volume") or ""),
        ("Number", entry.get("issue") or entry.get("number") or ""),
        ("Pages", entry.get("pages") or ""),
        ("DOI", entry.get("doi") or ""),
        ("URL", entry.get("url") or ""),
        (
            "Keywords",
            f"{', '.join(keywords[1])}  (from {keywords[0]})"
            if keywords[1]
            else "— none in Zotero or OpenAlex; take them from the paper",
        ),
        ("PDF", entry.get("pdf") or "— none public in Zotero; attach the accepted version"),
        ("Projects", top("projects")),
        ("Main program", top("mainresearchprogram")),
        ("Additional", top("additionalresearchprograms")),
    ]
    existing = find_record(entry, records)
    head = [
        f"Idiap portal entry for {key}",
        f"Enter it at {EDIT_PORTAL} (Idiap VPN: `idiap-vpn`; Idiap login).",
        f"ALREADY ON THE PORTAL as {existing['_key']} — edit that record instead." if existing else "",
        f"Proposals from the portal records of sibling papers on: {', '.join(pages) or 'no project page'}.",
    ]
    body = [f"  {name + ':':<14}{value}" for name, value in rows if value]
    tail = [
        "",
        f"Abstract (from {source}):" if source else "Abstract:",
        "  " + (" ".join(abstract.split()) if abstract else "— none in Zotero, OpenAlex or Semantic Scholar; copy it from the paper"),
        "",
        *(
            [
                "  ↳ Zotero has no abstract. Add it there, so the next `orcid-sync` carries it",
                "    to ORCID too: pixi run python tools/edit_zotero_item.py "
                + (f"--doi {entry['doi']}" if entry.get("doi") else "--key <ITEM_KEY>")
                + ' --set "abstractNote=…"',
            ]
            if source != "Zotero"
            else []
        ),
        "",
        "Zotero BibTeX:",
        zotero.get(key, "— not found").strip(),
    ]
    return "\n".join([h for h in head if h] + [""] + body + tail)


def main(argv: list[str] | None = None) -> int:
    """Run the check, or print one form with ``--prepare``.

    Parameters
    ----------
    argv
        Command-line arguments; ``sys.argv[1:]`` when None.

    Returns
    -------
    int
        0 when in sync (or the portal is unreachable), 1 when a recent paper is
        missing or ``--prepare`` names an unknown key.
    """
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--prepare", metavar="KEY", help="print the portal form for this citation key")
    args = ap.parse_args(argv)

    try:
        records = _fetch_portal()
    except Exception as e:  # an old, fragile server — never break the build on it
        print(f"  WARN: could not read {PORTAL} ({e}) — not checked.", file=sys.stderr)
        if not args.prepare:
            return 0
        records = []

    if args.prepare:
        try:
            zotero = zotero_common.fetch_public_bibtex(zotero_common.read_user_id())
            entries = _entries()
            entry = next((e for e in entries if e["key"] == args.prepare), {})
            print(prepare(args.prepare, entries, records, zotero, _lookup(entry) if entry else None))
        except KeyError as e:
            print(f"  ✗ {e.args[0]}", file=sys.stderr)
            return 1
        return 0

    since = _since()
    errors = check(_entries(), records, since)
    fatal = [e for e in errors if not e.startswith("WARN:")]
    for e in errors:
        print(("  " if e.startswith("WARN:") else "  ✗ ") + e, file=sys.stderr)
    if fatal:
        print(
            f"\nIdiap portal check FAILED: {len(fatal)} paper(s) since {since} missing. "
            f"New entries on {EDIT_PORTAL} reach {PORTAL} within the hour.",
            file=sys.stderr,
        )
        return 1
    print(f"Idiap portal: every paper since {since} is mirrored ({len(records)} records).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
