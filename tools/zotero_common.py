#!/usr/bin/env python3
"""Shared helpers for the Zotero-sourced publication tooling.

Zotero "My Publications" is the single source of truth. This module holds the
pure, testable core (type mapping, date/author normalisation, entry building)
plus thin network wrappers used by:

  * tools/update-site-outputs.py   (Zotero public feed -> data/outputs.json)
  * tools/update-orcid-outputs.py  (Zotero + ORCID public API -> report)
  * the add-zotero-output skill     (write path; needs an API key)

Reading My Publications uses the *public* feed and needs only a numeric user id
(no key), so the site/report generators are safe to run in CI. Writing needs a
read-write key; both are read from ~/.config/pyzotero.toml (or env vars).
"""

from __future__ import annotations

import collections
import os
import pathlib
import re
import tomllib
import unicodedata

CONFIG_FILE = pathlib.Path.home() / ".config" / "pyzotero.toml"
DEFAULT_USER_ID = "5992358"                 # André's numeric Zotero id (public)
ORCID_ID = "0000-0001-7248-4014"
MAILTO = "andre.anjos@idiap.ch"
USER_AGENT = f"anjos-site/1.0 (mailto:{MAILTO})"

ROOT = pathlib.Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"
OUTPUT_FILE = DATA_DIR / "outputs.json"
FUNDING_FILE = DATA_DIR / "funding.json"     # ORCID-sourced; see update-funding.py

# Zotero itemType -> (site label / filter category, ORCID work-type, URL slug).
# Slugs are short single words (no dashes): they form /outputs/<slug>/ filter pages.
ZTYPE = {
    "journalArticle": ("Journal Article", "journal-article", "journals"),
    "conferencePaper": ("Conference Paper", "conference-paper", "conferences"),
    "preprint": ("Preprint", "preprint", "preprints"),
    "bookSection": ("Book Chapter", "book-chapter", "chapters"),
    "book": ("Book", "book", "books"),
    "patent": ("Patent", "patent", "patents"),
    "thesis": ("Thesis", "dissertation-thesis", "theses"),
    "report": ("Report", "report", "reports"),
    "newspaperArticle": ("Press", "newspaper-article", "press"),
    "magazineArticle": ("Press", "magazine-article", "press"),
    "dataset": ("Dataset", "data-set", "datasets"),
    "computerProgram": ("Software", "software", "software"),
    "presentation": ("Presentation", "lecture-speech", "presentations"),
}
DEFAULT_TYPE = ("Other", "other", "other")

# Where a work's venue lives, by item type (first non-empty wins otherwise).
# `meetingName` is a presentation's conference.
_VENUE_FIELDS = ("publicationTitle", "proceedingsTitle", "bookTitle",
                 "repository", "publisher", "institution", "meetingName")


# --------------------------------------------------------------------------- #
# Config / credentials
# --------------------------------------------------------------------------- #
def _config(field: str, env_var: str) -> str | None:
    if CONFIG_FILE.exists():
        val = tomllib.loads(CONFIG_FILE.read_text()).get(field)
        if val:
            return str(val)
    return os.environ.get(env_var) or None


def read_user_id() -> str:
    """Numeric Zotero user id for the public feed (config, env, or default)."""
    return _config("user_id", "ZOTERO_USER_ID") or DEFAULT_USER_ID


def read_credentials() -> tuple[str, str]:
    """(user_id, api_key) for write access. Exits if either is missing."""
    import sys
    user_id = _config("user_id", "ZOTERO_USER_ID") or DEFAULT_USER_ID
    api_key = _config("api_key", "ZOTERO_API_KEY")
    if not api_key:
        sys.exit(
            f"No Zotero api_key. Put `api_key = \"…\"` in {CONFIG_FILE} (chmod 600) "
            "or set $ZOTERO_API_KEY. A read-write key is needed to add works."
        )
    return user_id, api_key


# --------------------------------------------------------------------------- #
# Pure helpers (unit-tested, no network)
# --------------------------------------------------------------------------- #
def normalize_doi(doi: str | None) -> str | None:
    if not doi:
        return None
    doi = doi.strip().lower()
    doi = re.sub(r"^(https?://(dx\.)?doi\.org/|doi:)", "", doi)
    return doi or None


def slug_title(text: str) -> str:
    """Accent-folded alphanumeric slug of a title, for fuzzy matching/keys."""
    text = unicodedata.normalize("NFKD", text or "").encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]", "", text.lower())


def normalize_author_name(name: str) -> str:
    """Render André's authorship uniformly as 'André Anjos', folding every variant
    (full name, 'A. Anjos', 'A.R. Anjos', 'A. R. Anjos') into one form so the
    templates highlight it consistently."""
    raw = (name or "").strip()
    toks = raw.split()
    if len(toks) < 2 or toks[-1].strip(".,").lower() != "anjos":
        return raw
    if toks[0].strip(".,").lower()[:1] == "a":  # André / Andre / A. / A.R. …
        return "André Anjos"
    return raw


def assert_unique_keys(entries: list[dict]) -> None:
    """Every entry must be addressable by exactly one key — `research_outputs:`
    refs resolve by it, and a duplicate would silently pick the first match."""
    dupes = {
        k: n for k, n in collections.Counter(e["key"] for e in entries).items() if n > 1
    }
    if not dupes:
        return
    lines = []
    for k in sorted(dupes):
        lines.append(f"  {k} (x{dupes[k]})")
        lines += [f"      {e.get('year')} {e['title'][:70]}" for e in entries if e["key"] == k]
    raise ValueError(
        "duplicate citation keys:\n" + "\n".join(lines)
        + "\nFix the citation key in Zotero (BetterBibTeX) so each work is unique."
    )


def parsed_date(item_data: dict, meta: dict) -> tuple[int | None, int]:
    """(year, month) for a Zotero item. Prefers meta.parsedDate (ISO), then the
    free-form `date` field. Month is 0 when unknown."""
    iso = (meta or {}).get("parsedDate") or ""
    m = re.match(r"(\d{4})(?:-(\d{2}))?", iso)
    if m:
        return int(m.group(1)), int(m.group(2) or 0)
    raw = (item_data or {}).get("date") or ""
    ym = re.search(r"(\d{4})", raw)
    year = int(ym.group(1)) if ym else None
    mm = re.search(r"\b(0?[1-9]|1[0-2])[/-]\d{4}\b|\b\d{4}-(0?[1-9]|1[0-2])\b", raw)
    month = int(next(g for g in (mm.groups() if mm else []) if g)) if mm else 0
    return year, month


def type_label(item_type: str) -> str:
    return ZTYPE.get(item_type, DEFAULT_TYPE)[0]


def orcid_type(item_type: str) -> str:
    return ZTYPE.get(item_type, DEFAULT_TYPE)[1]


def type_slug(item_type: str) -> str:
    return ZTYPE.get(item_type, DEFAULT_TYPE)[2]


# Zotero splits "the people who made this" across a type-specific creator role.
# All four are authorship for our purposes; without them a patent and a package
# would list nobody, on the site and on the CV alike.
_AUTHOR_ROLES = ("author", "presenter", "inventor", "programmer")


def authors_of(item_data: dict) -> list[str]:
    out = []
    for c in item_data.get("creators", []) or []:
        if c.get("creatorType") not in _AUTHOR_ROLES:  # editors are not authors
            continue
        name = " ".join(p for p in (c.get("firstName", ""), c.get("lastName", "")) if p).strip()
        name = name or (c.get("name") or "").strip()
        if name:
            out.append(normalize_author_name(name))
    return out


def venue_of(item_data: dict) -> str | None:
    for f in _VENUE_FIELDS:
        if item_data.get(f):
            return item_data[f]
    return None


def parse_extra_links(extra: str) -> dict:
    """Parse labeled lines from an item's `extra` field into a link dict.
    `Docs`/`PyPI`/`conda-forge`/`Archived` describe a computerProgram; `Software`
    is a companion-code repo attached to a *publication* (a paper's validation
    code, etc.), surfaced next to the DOI/PDF links."""
    out: dict = {}
    for line in (extra or "").splitlines():
        m = re.match(r"\s*(Docs|PyPI|conda-forge|Archived|Software|Homepage)\s*:\s*(.+?)\s*$",
                     line, re.I)
        if not m:
            continue
        k, v = m.group(1).lower(), m.group(2).strip()
        if k == "conda-forge":
            out["conda"] = v
        elif k == "archived":
            out["archived"] = v.lower() in ("true", "yes", "1")
        else:
            out[k] = v  # docs / pypi / software / homepage
    return out


def set_extra_field(extra: str, label: str, value: str) -> str:
    """Add or replace a `Label: value` line in an `extra` block (case-insensitive
    on the label), keeping every other line. Any duplicate labels collapse to one."""
    out, done = [], False
    for line in (extra or "").splitlines():
        if re.match(rf"\s*{re.escape(label)}\s*:", line, re.I):
            if not done:
                out.append(f"{label}: {value}")
                done = True
        else:
            out.append(line)
    if not done:
        out.append(f"{label}: {value}")
    return "\n".join(out).strip()


def del_extra_field(extra: str, label: str) -> str:
    """Remove any `Label: …` line(s) from an `extra` block."""
    return "\n".join(
        line for line in (extra or "").splitlines()
        if not re.match(rf"\s*{re.escape(label)}\s*:", line, re.I)
    ).strip()


def public_pdf_url(user_id: str, attachment_key: str) -> str:
    return f"https://api.zotero.org/users/{user_id}/publications/items/{attachment_key}/file"




def build_site_entry(top: dict, pdf_key: str | None, user_id: str) -> dict:
    """One outputs.json entry from a Zotero top-level item (+ optional public
    PDF attachment key). Shape matches layouts/partials/out-ref.html & out-cite.html."""
    d = top["data"]
    year, month = parsed_date(d, top.get("meta", {}))
    doi = normalize_doi(d.get("DOI"))
    links = parse_extra_links(d.get("extra", ""))
    entry = {
        "authors": authors_of(d),
        "title": (d.get("title") or "").strip(),
        "container": venue_of(d),
        "year": year,
        "month": month,
        "doi": doi,
        # The article's *paper page* is the authoritative `Homepage:` line in `extra`.
        # The top-level Zotero `url` field is unreliable (earlier enrichment) and ignored,
        # except as a computerProgram's repo (its Source link) below.
        "url": links.get("homepage"),
        "pdf": public_pdf_url(user_id, pdf_key) if pdf_key else None,
        "type": type_label(d.get("itemType", "")),
        "typeslug": type_slug(d.get("itemType", "")),
    }
    if d.get("itemType") == "computerProgram":
        entry["license"] = d.get("rights") or None
        entry["summary"] = (d.get("abstractNote") or "").strip() or None
        entry["links"] = {"repo": d.get("url") or None, "docs": links.get("docs"),
                          "pypi": links.get("pypi"), "conda": links.get("conda")}
        entry["archived"] = bool(links.get("archived"))
    else:
        # A publication may carry a companion-code repo (`Software: <url>` in extra),
        # rendered as a "Software" link beside its DOI/PDF.
        entry["software"] = links.get("software")
        # Bibliographic locators. The website does not print them, but the CV does
        # ("vol. 12, no. 3, pp. 1-10"), and they are public-feed fields, so CHECK
        # still verifies them without a key. `number` folds the two type-specific
        # identifiers Zotero keeps apart — a patent's and a report's — into one.
        entry["volume"] = d.get("volume") or None
        entry["issue"] = d.get("issue") or None
        entry["pages"] = d.get("pages") or None
        entry["number"] = d.get("patentNumber") or d.get("reportNumber") or None
    entry["zkey"] = top["key"]
    # Zotero's own BetterBibTeX key is authoritative, and the public feed exposes
    # it. It is required: `research_outputs:` refs address a work by this key, so
    # anything generated here would be a key nobody could predict or link to.
    entry["key"] = (d.get("citationKey") or "").strip()
    if not entry["key"]:
        raise ValueError(
            f"no BetterBibTeX citation key on item {top['key']}: {entry['title'][:60]!r}"
            "\nSet one in Zotero (BetterBibTeX) — the site addresses works by it."
        )
    return entry


def build_entries(items: list[dict], user_id: str, relmap: dict | None = None) -> list[dict]:
    """Turn a raw public-feed item list (tops + public attachments) into sorted
    site entries. Public attachments appear in the feed only when shared, so any
    PDF child found here is by definition publicly downloadable."""
    tops = [it for it in items if it["data"].get("itemType") not in ("attachment", "note")]
    pdf_by_parent: dict[str, str] = {}
    for it in items:
        d = it["data"]
        if d.get("itemType") == "attachment" and d.get("contentType") == "application/pdf":
            pdf_by_parent.setdefault(d.get("parentItem"), it["key"])
    entries = [build_site_entry(t, pdf_by_parent.get(t["key"]), user_id) for t in tops]
    # Resolve Zotero dc:relation links (from relmap: {zkey: [zkey,…]}) to sibling
    # entries: keep the sibling's type (for a pill) and its DOI/URL. The public feed
    # strips relations, so relmap comes from the authenticated API (fetch_relations).
    by_zkey = {e["zkey"]: e for e in entries}
    for e in entries:
        rel = []
        for rk in (relmap or {}).get(e["zkey"], []):
            o = by_zkey.get(rk)
            if not o:
                continue
            href = o.get("url") or o.get("pdf")
            if o.get("doi") or href:
                rel.append({"type": o["type"], "doi": o.get("doi"), "href": href})
        e["related"] = rel
    assert_unique_keys(entries)
    for e in entries:
        e.pop("zkey", None)
    entries.sort(key=lambda e: (e.get("year") or 0, e.get("month") or 0), reverse=True)
    return entries


# --------------------------------------------------------------------------- #
# Network (thin). Reading My Publications is key-less; ORCID public API is too.
# --------------------------------------------------------------------------- #
def fetch_relations(user_id: str) -> dict[str, list[str]] | None:
    """{zkey: [related zkey, …]} from the *authenticated* library. This is the one
    call that needs an API key: `dc:relation` is the only field the public feed
    cannot supply. Returns None when no key is configured, which is what puts
    update-site-outputs.py into check mode."""
    api_key = _config("api_key", "ZOTERO_API_KEY")
    if not api_key:
        return None
    from pyzotero import zotero

    zot = zotero.Zotero(user_id, "user", api_key)
    out: dict[str, list[str]] = {}
    for it in zot.everything(zot.top()):
        r = (it["data"].get("relations") or {}).get("dc:relation")
        r = [r] if isinstance(r, str) else (r or [])
        if r:
            out[it["key"]] = [x.rstrip("/").split("/")[-1] for x in r]
    return out


def fetch_public_items(user_id: str) -> list[dict]:
    """All items (tops + public attachments) from the public My Publications feed."""
    import requests

    out: list[dict] = []
    start = 0
    while True:
        r = requests.get(
            f"https://api.zotero.org/users/{user_id}/publications/items",
            params={"format": "json", "limit": 100, "start": start},
            headers={"Zotero-API-Version": "3", "User-Agent": USER_AGENT},
            timeout=30,
        )
        r.raise_for_status()
        batch = r.json()
        out.extend(batch)
        total = int(r.headers.get("Total-Results", len(out)))
        start += len(batch)
        if not batch or start >= total:
            break
    return out


def fetch_orcid_works(orcid_id: str = ORCID_ID) -> dict:
    import requests

    r = requests.get(
        f"https://pub.orcid.org/v3.0/{orcid_id}/works",
        headers={"Accept": "application/json", "User-Agent": USER_AGENT},
        timeout=30,
    )
    r.raise_for_status()
    return r.json()


def _orcid_get(path: str) -> dict:
    """GET a public ORCID v3.0 endpoint as JSON.

    Parameters
    ----------
    path
        Path below the record, e.g. ``"fundings"`` or ``"funding/1631985"``.

    Returns
    -------
    dict
        The decoded payload.

    Raises
    ------
    requests.RequestException
        Any network or HTTP failure; callers decide whether that is fatal.
    """
    import requests

    r = requests.get(
        f"https://pub.orcid.org/v3.0/{ORCID_ID}/{path}",
        headers={"Accept": "application/json", "User-Agent": USER_AGENT},
        timeout=30,
    )
    r.raise_for_status()
    return r.json()


def fetch_orcid_fundings() -> dict:
    """The ORCID funding *summaries*, grouped by grant identifier.

    Returns
    -------
    dict
        The ``/fundings`` payload. Each group holds one summary per asserting
        source, and none of them carries the amount, the abstract, or the
        instrument — those need :func:`fetch_orcid_funding`.
    """
    return _orcid_get("fundings")


def fetch_orcid_funding(put_code: int | str) -> dict:
    """The full ORCID record for one funding item.

    ORCID has no bulk funding endpoint, so this is one request per grant.

    Parameters
    ----------
    put_code
        The item's ORCID put-code, as found in the summary.

    Returns
    -------
    dict
        The ``/funding/{put_code}`` payload, adding ``amount``,
        ``short-description`` and ``organization-defined-type`` to what the
        summary already provides.
    """
    return _orcid_get(f"funding/{put_code}")


def parse_orcid_works(payload: dict) -> list[dict]:
    """One dict per ORCID work: {doi, title, container, year, type, putcode}."""
    out = []
    for group in payload.get("group", []):
        summaries = group.get("work-summary") or []
        if not summaries:
            continue
        s = summaries[0]
        doi = None
        for eid in (group.get("external-ids") or {}).get("external-id", []):
            if (eid.get("external-id-type") or "").lower() == "doi":
                doi = normalize_doi(eid.get("external-id-value"))
                break
        url = None
        for eid in (group.get("external-ids") or {}).get("external-id", []):
            if (eid.get("external-id-value") or "").startswith("http"):
                url = eid.get("external-id-value")
        title = (((s.get("title") or {}).get("title") or {}) or {}).get("value")
        pub = s.get("publication-date") or {}
        year = ((pub.get("year") or {}) or {}).get("value")
        out.append({
            "doi": doi,
            "title": title,
            "container": ((s.get("journal-title") or {}) or {}).get("value"),
            "year": int(year) if (year or "").isdigit() else None,
            "type": (s.get("type") or "").lower().replace("_", "-") or None,
            "url": (s.get("url") or {}).get("value") if s.get("url") else url,
            "putcode": s.get("put-code"),
        })
    return out


def fetch_crossref(doi: str) -> dict | None:
    """Crossref 'message' for a DOI (best-effort; None on failure)."""
    import requests

    try:
        r = requests.get(
            f"https://api.crossref.org/works/{doi}",
            params={"mailto": MAILTO},
            headers={"User-Agent": USER_AGENT},
            timeout=30,
        )
        r.raise_for_status()
        return r.json().get("message")
    except Exception:  # noqa: BLE001 - best-effort enrichment
        return None
