#!/usr/bin/env python3
"""Shared helpers for the Zotero-sourced publication tooling.

Zotero "My Publications" is the single source of truth. This module holds the
pure, testable core (type mapping, date/author normalisation, entry building)
plus thin network wrappers used by:

  * tools/update-site-outputs.py   (Zotero public feed -> data/outputs.json)
  * tools/sync_orcid.py            (Zotero + ORCID public API -> report/sync)
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
#: The one canonical spelling of the record holder's name, which is what
#: normalize_author_name() folds every variant to and what identifies "me" among
#: a work's authors — see sync_orcid.contributor_grouped.
SELF_NAME = "André Anjos"
MAILTO = "andre.anjos@idiap.ch"
USER_AGENT = f"anjos-site/1.0 (mailto:{MAILTO})"

ROOT = pathlib.Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"
OUTPUT_FILE = DATA_DIR / "outputs.json"
FUNDING_FILE = DATA_DIR / "funding.json"     # ORCID-sourced; see update-funding.py
INTERESTS_FILE = DATA_DIR / "interests.json"  # ORCID Keywords; see update-interests.py

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


# Language guessing for ORCID's `language-code`, over the only three languages
# this record uses. Markers are chosen to be *unambiguous*: English is the
# default and the overwhelming majority, so a false positive is far worse than a
# miss. Words shared across the romance pair ("de", "la", "e") carry no weight,
# and short words that are also English ("no", "a", "e", "um") are excluded —
# "No Free Lunch" must not read as Portuguese.
_PT_WORDS = frozenset("""
    ção ções uma umas uns dos das para pela pelo com não são está entre sobre
    sistema análise redes neurais elétron níveis alta taxa eventos baseado
    filtros segundo nível experimento classificação validação separação
    discriminação otimização mapeamento anéis máquina distribuído partículas
    submetido ambiente protótipo integrando plataformas algoritmos usando
    calorímetros multi-camadas especialistas neuronal online
""".split())
_FR_WORDS = frozenset("""
    les des du aux dans pour avec une sur par selon est cette ces leur
    réseaux données apprentissage profond image images médicale médicales
    reconnaissance détection analyse système systèmes méthode méthodes étude
""".split())
#: Characters that occur in one language and not the other two.
_PT_CHARS = "ãõ"
_FR_CHARS = "œùû"


def detect_language(title: str) -> str:
    """Best-guess ISO 639-1 language of a work, from its title.

    Only English, Portuguese and French are considered — the three languages
    this record uses. English is the default and by far the most common, so the
    markers are deliberately conservative: a title has to look positively
    Portuguese or French to be classified as such.

    Parameters
    ----------
    title
        The work's title. May be empty.

    Returns
    -------
    str
        ``"pt"``, ``"fr"`` or ``"en"``.
    """
    text = (title or "").lower()
    words = set(re.findall(r"[\w'-]+", text, flags=re.UNICODE))

    pt = len(words & _PT_WORDS) + sum(3 for c in _PT_CHARS if c in text)
    fr = len(words & _FR_WORDS) + sum(3 for c in _FR_CHARS if c in text)
    # "ção"/"ções" are endings as often as words; catch them either way.
    pt += 3 * len(re.findall(r"ç[ãõ]e?s?\b", text))

    if max(pt, fr) < 2:          # one weak hit is noise, not a language
        return "en"
    return "pt" if pt >= fr else "fr"


# Zotero field -> (ORCID identifier type, relationship). `part-of` is not
# cosmetic: ORCID groups works by their `self` identifiers, so an ISSN marked
# `self` would fold every article in that journal into one work group — and
# ORCID rejects later ones as duplicates. An ISSN identifies the journal and an
# ISBN the book, hence part-of for both.
_ID_FIELDS = {
    "DOI": ("doi", "self"),
    "ISSN": ("issn", "part-of"),
    "ISBN": ("isbn", "part-of"),
    # ORCID's type for a patent number is the terse "pat". Self: it names the
    # patent itself, unlike an ISSN naming a journal.
    "patentNumber": ("pat", "self"),
}
#: Prefixes Zotero uses in `archiveID` and in labelled `extra` lines, mapped to
#: ORCID's controlled vocabulary. Anything else is skipped rather than guessed.
_ID_PREFIXES = {"arxiv": "arxiv", "ssrn": "ssrn", "pmid": "pmid", "pmcid": "pmc"}


def normalize_identifier(id_type: str, value: str) -> str:
    """A comparable form of an identifier, for telling "same" from "missing".

    The same identifier reaches ORCID spelled several ways — this record already
    holds ``2009.01907``, ``abs/2408.16130`` and ``arXiv:1709.00962`` as arXiv
    ids. Comparing raw strings would re-add one that is already there, leaving
    the work with two spellings of a single identifier.

    Parameters
    ----------
    id_type
        ORCID's identifier type, e.g. ``"doi"``.
    value
        The identifier as written.

    Returns
    -------
    str
        The comparison key; never used as the value actually written.
    """
    v = (value or "").strip()
    t = (id_type or "").lower()
    if t == "doi":
        return normalize_doi(v) or ""
    if t == "arxiv":
        v = re.sub(r"^\s*(arxiv:)?\s*(abs/)?", "", v, flags=re.IGNORECASE)
    if t in ("issn", "isbn"):
        v = re.sub(r"[-\s]", "", v)
    return v.lower()


def work_identifiers(item_data: dict) -> list[dict]:
    """Every work identifier Zotero holds, as ORCID external ids.

    Covers the identifier fields (DOI, ISSN, ISBN), the ``archiveID`` prefix
    form (``SSRN:4960069``) and labelled ``extra`` lines (``arXiv: 2407.14064``,
    ``PMID: …``). Unrecognised prefixes are skipped rather than guessed at, and
    patent and report numbers are left out: ORCID has no type for them beyond
    the catch-all ``other-id``.

    Parameters
    ----------
    item_data
        The Zotero item's ``data`` block.

    Returns
    -------
    list of dict
        ``{"type", "value", "relationship"}`` per identifier, de-duplicated on
        the normalised value.
    """
    out: list[dict] = []
    seen: set[tuple[str, str]] = set()

    def add(id_type: str, value: str, relationship: str) -> None:
        value = (value or "").strip()
        # Zotero fields sometimes repeat the label inside the value — one item
        # here stores "ISBN 978-3-319-92627-8". Written through verbatim that
        # becomes a malformed identifier on ORCID.
        value = re.sub(rf"^{id_type}\s*:?\s*", "", value, flags=re.IGNORECASE).strip()
        if not value:
            return
        key = (id_type, normalize_identifier(id_type, value))
        if key[1] and key not in seen:
            seen.add(key)
            out.append({"type": id_type, "value": value,
                        "relationship": relationship})

    for field, (id_type, rel) in _ID_FIELDS.items():
        raw = (item_data.get(field) or "").strip()
        # Zotero happily stores several ISSNs in one field.
        for part in re.split(r"[,;]| and ", raw) if raw else []:
            add(id_type, part, rel)

    for source in (item_data.get("archiveID") or "", item_data.get("extra") or ""):
        for prefix, id_type in _ID_PREFIXES.items():
            m = re.search(rf"^\s*{prefix}\s*:\s*(\S+)", source,
                          re.IGNORECASE | re.MULTILINE)
            if m:
                add(id_type, m.group(1), "self")
    return out


#: BibTeX fields dropped before a citation reaches ORCID. `abstract` is bulky
#: and duplicated by ORCID's own field; `note` is where Zotero puts its Extra
#: block, which on this library holds purely local bookkeeping (Homepage:,
#: Software:, Docs:, GSCC: lines); `file` and `urldate` name things on one
#: machine. `copyright` is kept — for software it carries the real licence.
BIBTEX_DROP = ("abstract", "note", "file", "urldate", "keywords", "annote")

#: A cleaned citation longer than this is skipped rather than written. ORCID's
#: column is unbounded `text` and its validator only requires a non-empty value,
#: so this is our policy, not ORCID's: a 2048-author entry runs to 32 kB, which
#: is unusable in ORCID's UI and in whatever a funder ingests it into. Skipping
#: is silent-safe — the record simply carries no citation, and the diff then has
#: nothing to propose, so the sync still converges.
MAX_CITATION_CHARS = 10_000


def _bibtex_fields(body: str):
    """Yield ``(name, raw_text)`` for each field in a BibTeX entry body.

    Brace-counting rather than line splitting: a value may span lines and
    contain commas, and Zotero's abstracts routinely do both.
    """
    i, n = 0, len(body)
    pattern = re.compile(r"\s*(\w+)\s*=\s*")
    while i < n:
        m = pattern.match(body, i)
        if not m:
            break
        j = m.end()
        if j < n and body[j] == "{":
            depth = 0
            while j < n:
                if body[j] == "{":
                    depth += 1
                elif body[j] == "}":
                    depth -= 1
                    if depth == 0:
                        j += 1
                        break
                j += 1
        elif j < n and body[j] == '"':
            j += 1
            while j < n and body[j] != '"':
                j += 1
            j += 1
        else:
            while j < n and body[j] not in ",\n":
                j += 1
        k = j
        while k < n and body[k] in " \t":
            k += 1
        if k < n and body[k] == ",":
            k += 1
        yield m.group(1), body[i:k]
        i = k


def clean_bibtex(entry: str, drop: tuple[str, ...] = BIBTEX_DROP) -> str:
    """One BibTeX entry with local and bulky fields removed, re-emitted evenly.

    Whitespace inside values is collapsed, which both tidies Zotero's wrapped
    abstracts-turned-titles and makes the result stable to compare — otherwise
    a re-flowed line would read as drift and be rewritten on every run.

    Parameters
    ----------
    entry
        One ``@type{key, ...}`` entry.
    drop
        Field names to remove, case-insensitively.

    Returns
    -------
    str
        The cleaned entry, or the input stripped if it does not parse.
    """
    m = re.match(r"\s*(@\w+\s*\{\s*[^,]+,)", entry)
    if not m:
        return entry.strip()
    body = entry[m.end():].rstrip()
    if body.endswith("}"):
        body = body[:-1]
    lowered = {d.lower() for d in drop}
    kept = []
    for name, raw in _bibtex_fields(body):
        if name.lower() in lowered:
            continue
        kept.append("\t" + " ".join(raw.strip().rstrip(",").split()) + ",")
    return m.group(1) + "\n" + "\n".join(kept) + "\n}"


def normalize_bibtex(entry: str) -> str:
    """A whitespace-insensitive form of a BibTeX entry, for comparison only."""
    return " ".join((entry or "").split())


def fetch_public_bibtex(user_id: str) -> dict[str, str]:
    """Zotero's own BibTeX export of My Publications, keyed by citation key.

    Zotero renders this itself, so the entries carry its field mapping rather
    than a re-implementation of it. The keys match each item's ``citationKey``
    exactly across this library, which is what lets records be paired up by key.

    Parameters
    ----------
    user_id
        The Zotero user id whose public feed to read.

    Returns
    -------
    dict
        ``{citation key: entry text}``, uncleaned.

    Raises
    ------
    requests.RequestException
        Any network or HTTP failure.
    """
    import requests

    url = f"https://api.zotero.org/users/{user_id}/publications/items"
    out: dict[str, str] = {}
    start, total = 0, None
    while True:
        r = requests.get(
            url,
            params={"format": "bibtex", "limit": 100, "start": start},
            headers={"User-Agent": USER_AGENT},
            timeout=60,
        )
        r.raise_for_status()
        if total is None:
            total = int(r.headers.get("Total-Results", 0))
        for entry, key in re.findall(r"(@\w+\{([^,]+),.*?\n\})", r.text, re.S):
            out[key.strip()] = entry
        start += 100
        if start >= (total or 0):
            return out


def attach_bibtex(records: list[dict], bibtex: dict[str, str],
                  max_chars: int = MAX_CITATION_CHARS) -> list[dict]:
    """Give each Zotero record its cleaned BibTeX, in place, keyed by citation key.

    A record whose citation is unusable gets ``bibtex = None`` and a reason in
    ``bibtex_skipped``. That pairing matters: with no citation the diff proposes
    nothing for it, so a skipped work converges instead of failing on every run,
    and the reason is still there to show the user why.

    Parameters
    ----------
    records
        Records from :func:`zotero_records`.
    bibtex
        The mapping from :func:`fetch_public_bibtex`.
    max_chars
        Longest citation to accept; see :data:`MAX_CITATION_CHARS`.

    Returns
    -------
    list of dict
        The same list; each record gains ``bibtex`` (str or None) and
        ``bibtex_skipped`` (str or None).
    """
    for rec in records:
        rec["bibtex"] = None
        rec["bibtex_skipped"] = None
        entry = bibtex.get(rec.get("key") or "")
        if not entry:
            rec["bibtex_skipped"] = "Zotero produced no BibTeX entry for it"
            continue
        cleaned = clean_bibtex(entry)
        if len(cleaned) > max_chars:
            rec["bibtex_skipped"] = (
                f"its BibTeX runs to {len(cleaned):,} characters, over the "
                f"{max_chars:,} limit"
            )
            continue
        rec["bibtex"] = cleaned
    return records


def normalize_author_name(name: str) -> str:
    """Render André's authorship uniformly as 'André Anjos', folding every variant
    (full name, 'A. Anjos', 'A.R. Anjos', 'A. R. Anjos') into one form so the
    templates highlight it consistently."""
    raw = (name or "").strip()
    toks = raw.split()
    if len(toks) < 2 or toks[-1].strip(".,").lower() != "anjos":
        return raw
    if toks[0].strip(".,").lower()[:1] == "a":  # André / Andre / A. / A.R. …
        return SELF_NAME
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


def parsed_ymd(item_data: dict, meta: dict) -> tuple[int | None, int, int]:
    """(year, month, day) for a Zotero item, 0 for whatever it does not know.

    Zotero's granularity varies a lot — on this library 125 works carry only a
    year, 8 a year and month, 12 a full date — and that difference is
    meaningful: a missing month is "unknown", not "no month". Callers must not
    push a 0 onto a record that knows better.

    Parameters
    ----------
    item_data
        The Zotero item's ``data`` block.
    meta
        Its ``meta`` block, whose ``parsedDate`` is preferred when present.

    Returns
    -------
    tuple
        ``(year, month, day)``; year may be None, month and day are 0 when
        unknown.
    """
    iso = (meta or {}).get("parsedDate") or ""
    m = re.match(r"(\d{4})(?:-(\d{2}))?(?:-(\d{2}))?", iso)
    if m:
        return int(m.group(1)), int(m.group(2) or 0), int(m.group(3) or 0)
    year, month = _parsed_date_freeform(item_data)
    return year, month, 0


def parsed_date(item_data: dict, meta: dict) -> tuple[int | None, int]:
    """(year, month) for a Zotero item — see :func:`parsed_ymd`."""
    year, month, _day = parsed_ymd(item_data, meta)
    return year, month


def _parsed_date_freeform(item_data: dict) -> tuple[int | None, int]:
    """(year, month) dug out of Zotero's free-form ``date`` string."""
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


def fetch_orcid_keywords() -> dict:
    """The ORCID record's Keywords, which the site and CV call "interests".

    Returns
    -------
    dict
        The ``/keywords`` payload. Each entry carries its ``content`` and a
        ``display-index``; ORCID serves them highest index first, which is the
        order it shows them in.
    """
    return _orcid_get("keywords")


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


def self_asserted(summary: dict) -> bool:
    """Whether the record holder — not a third party — asserted this summary.

    ORCID lets several sources assert the same work; only the source that
    created an item may later edit or delete it. Ours are the ones whose
    ``source-orcid`` is the record itself, as opposed to a client such as
    Crossref.

    Parameters
    ----------
    summary
        One ``work-summary`` (or any activity summary) from an ORCID payload.

    Returns
    -------
    bool
        True when the summary's source is :data:`ORCID_ID`.
    """
    src = (summary.get("source") or {}).get("source-orcid") or {}
    return src.get("path") == ORCID_ID


def pick_work_summary(summaries: list[dict]) -> dict:
    """The summary of a work group to treat as ours.

    ORCID does not order a group's summaries, so the self-asserted one is not
    reliably first — on this record a Crossref assertion precedes ours in every
    co-asserted group. Anything that means to *edit* a work has to find the
    right put-code, hence this rather than ``summaries[0]``.

    Parameters
    ----------
    summaries
        A work group's ``work-summary`` list, which must not be empty.

    Returns
    -------
    dict
        The self-asserted summary when there is one, else the first.
    """
    return next((s for s in summaries if self_asserted(s)), summaries[0])


def parse_orcid_works(payload: dict) -> list[dict]:
    """One dict per ORCID work: {doi, title, container, year, type, putcode}."""
    out = []
    for group in payload.get("group", []):
        summaries = group.get("work-summary") or []
        if not summaries:
            continue
        s = pick_work_summary(summaries)
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
        month = ((pub.get("month") or {}) or {}).get("value")
        day = ((pub.get("day") or {}) or {}).get("value")
        out.append({
            "doi": doi,
            "title": title,
            "container": ((s.get("journal-title") or {}) or {}).get("value"),
            "year": int(year) if (year or "").isdigit() else None,
            "month": int(month) if (month or "").isdigit() else 0,
            "day": int(day) if (day or "").isdigit() else 0,
            "type": (s.get("type") or "").lower().replace("_", "-") or None,
            "url": (s.get("url") or {}).get("value") if s.get("url") else url,
            "putcode": s.get("put-code"),
            "ours": self_asserted(s),
            "identifiers": [
                {"type": (e.get("external-id-type") or "").lower(),
                 "value": e.get("external-id-value") or "",
                 "relationship": e.get("external-id-relationship") or "self"}
                for e in ((s.get("external-ids") or {}).get("external-id") or [])
            ],
        })
    return out


def ui_work_authors(work: dict) -> list[str]:
    """Credit names as ORCID's record page shows them, in order.

    Reads ``contributorsGroupedByOrcid``, **not** the flat ``contributors``
    list. The two are separate stores and routinely disagree: a work can serve
    nine contributors over the public v3.0 API while its Contributors panel is
    blank, because only the grouped one is rendered. Since the panel is what a
    reader sees, it is what "does ORCID have the authors?" has to mean.

    Parameters
    ----------
    work
        One work from :func:`fetch_orcid_ui_works`.

    Returns
    -------
    list of str
        The credit names, empty when the panel would show none.
    """
    names = []
    for c in work.get("contributorsGroupedByOrcid") or []:
        name = ((c.get("creditName") or {}) or {}).get("content")
        if name:
            names.append(name.strip())
    return names


def ui_self_linked(work: dict) -> bool:
    """Whether the record holder is linked *as a profile* on this work.

    ORCID distinguishes "Add contributor" (a loose credit name) from "Add
    yourself as a contributor" (the name plus your iD, which links the work to
    your profile). Only the latter carries ``contributorOrcid.path``.

    Parameters
    ----------
    work
        One work from :func:`fetch_orcid_ui_works`.

    Returns
    -------
    bool
        True when some contributor carries this record's ORCID iD.
    """
    for c in work.get("contributorsGroupedByOrcid") or []:
        if ((c.get("contributorOrcid") or {}) or {}).get("path") == ORCID_ID:
            return True
    return False


def fetch_orcid_ui_works(page_size: int = 50) -> dict[int, dict]:
    """Every work as ORCID's own record page sees it, keyed by put-code.

    Uses the undocumented endpoint the public record page itself calls — the
    same class of thing as ``featuredWorks.json`` in ``check_featured.py``, and
    likewise key-less for a public record. It is the only source for the grouped
    contributor list, and it carries the language code too, so one paged sweep
    replaces a second trip to the documented API.

    Parameters
    ----------
    page_size
        Works per request. ORCID rejects large pages outright (200 comes back as
        an HTML error), so this stays at 50.

    Returns
    -------
    dict
        ``{put_code: work}`` across every group and every assertion in it.

    Raises
    ------
    requests.RequestException
        Any network or HTTP failure.
    """
    import requests

    url = f"https://orcid.org/{ORCID_ID}/worksExtendedPage.json"
    out: dict[int, dict] = {}
    offset = 0
    while True:
        r = requests.get(
            url,
            params={"offset": offset, "sort": "date", "sortAsc": "false",
                    "pageSize": page_size},
            headers={"Accept": "application/json", "User-Agent": USER_AGENT},
            timeout=30,
        )
        r.raise_for_status()
        payload = r.json()
        groups = payload.get("groups") or []
        for group in groups:
            for work in group.get("works") or []:
                code = ((work.get("putCode") or {}) or {}).get("value")
                if code is not None:
                    out[int(code)] = work
        if len(groups) < page_size:
            return out
        offset += page_size


def fetch_orcid_work_details(put_codes: list[int], chunk: int = 50) -> dict[int, dict]:
    """Full ORCID work records by put-code, from the documented bulk endpoint.

    Parameters
    ----------
    put_codes
        The put-codes to fetch.
    chunk
        How many to request at once; ORCID's ceiling is 100.

    Returns
    -------
    dict
        ``{put_code: work record}``. Put-codes ORCID does not return are absent.

    Raises
    ------
    requests.RequestException
        Any network or HTTP failure.
    """
    details: dict[int, dict] = {}
    for i in range(0, len(put_codes), chunk):
        batch = put_codes[i:i + chunk]
        payload = _orcid_get("works/" + ",".join(str(p) for p in batch))
        for item in payload.get("bulk", []):
            work = item.get("work")
            if work and work.get("put-code") is not None:
                details[int(work["put-code"])] = work
    return details


def enrich_orcid_works(works: list[dict]) -> list[dict]:
    """Add ``authors`` and ``language`` to parsed ORCID works, in place.

    :func:`parse_orcid_works` reads the summary feed, which has neither — and
    they have to come from *different* places, which is not obvious and cost two
    rounds of "the sync keeps redoing the same change":

    * **authors** from the record page's own feed, because only its grouped list
      reflects what the Contributors panel shows;
    * **language** from the documented API, because the page feed has a
      ``languageCode`` field but always leaves it null, even on works whose
      public record plainly says ``en``.

    Reading either from the other source makes every work look permanently out
    of date, and the sync rewrites them on every run without ever converging.

    Parameters
    ----------
    works
        Works from :func:`parse_orcid_works`.

    Returns
    -------
    list of dict
        The same list, each work gaining ``authors`` (list of str) and
        ``language`` (str or None). Their presence is what tells
        :func:`field_diffs` it may compare them at all.
    """
    ui = fetch_orcid_ui_works()
    put_codes = [w["putcode"] for w in works if w.get("putcode") is not None]
    details = fetch_orcid_work_details(put_codes)
    for w in works:
        code = w.get("putcode")
        page = ui.get(code)
        if page is not None:
            w["authors"] = ui_work_authors(page)
            w["self_linked"] = ui_self_linked(page)
        detail = details.get(code)
        if detail is not None:
            w["language"] = detail.get("language-code")
            citation = detail.get("citation") or {}
            w["citation"] = citation.get("citation-value")
            w["citation_type"] = citation.get("citation-type")
    return works


def zotero_records(user_id: str) -> list[dict]:
    """Rich per-work records from Zotero for the ORCID comparison.

    This is the Zotero side of the Zotero-is-the-source-of-truth diff, shaped
    for comparison against :func:`parse_orcid_works` rather than for the
    website (which wants :func:`build_site_entry`).

    Parameters
    ----------
    user_id
        The Zotero user id whose "My Publications" feed to read.

    Returns
    -------
    list of dict
        One record per work, with ``title``, ``slug``, ``authors``, ``doi``,
        ``orcid_type``, ``container``, ``year``, ``url`` and ``pdf``. Attachments
        and notes are skipped; a work's first public PDF attachment becomes
        ``pdf``.
    """
    items = fetch_public_items(user_id)
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
        year, month, day = parsed_ymd(d, it.get("meta", {}))
        doi = normalize_doi(d.get("DOI"))
        pdf = public_pdf_url(user_id, pdf_by_parent[it["key"]]) if it["key"] in pdf_by_parent else None
        recs.append({
            "title": (d.get("title") or "").strip(),
            "slug": slug_title(d.get("title") or ""),
            "key": d.get("citationKey"),
            "authors": authors_of(d),
            "language": detect_language(d.get("title") or ""),
            "identifiers": work_identifiers(d),
            "doi": doi,
            "orcid_type": orcid_type(d.get("itemType", "")),
            "container": venue_of(d),
            "year": year,
            "month": month,
            "day": day,
            "url": d.get("url") or (f"https://doi.org/{doi}" if doi else None),
            "pdf": pdf,
        })
    return recs


def index_orcid_works(orcid: list[dict]) -> tuple[dict, dict]:
    """Index ORCID works by DOI and by title slug, keeping *every* collision.

    The indexes map to **lists**, not single works. Keying one work per slug
    silently hides duplicates, and a Zotero record that then finds no free
    candidate is reported as missing and re-added on every run — which is how
    seven copies of one ATLAS paper accumulated on the live record.

    Parameters
    ----------
    orcid
        Works from :func:`parse_orcid_works`.

    Returns
    -------
    tuple
        ``(by_doi, by_title)``, each ``{key: [work, ...]}`` in input order.
    """
    by_doi: dict[str, list[dict]] = {}
    by_title: dict[str, list[dict]] = {}
    for o in orcid:
        if o.get("doi"):
            by_doi.setdefault(o["doi"], []).append(o)
        if o.get("title"):
            by_title.setdefault(slug_title(o["title"]), []).append(o)
    return by_doi, by_title


def match(zrec: dict, by_doi: dict, by_title: dict,
          claimed: set | None = None) -> dict | None:
    """The ORCID work a Zotero record refers to, skipping any already claimed.

    DOI is authoritative; the accent-folded title slug is the fallback for the
    many works carrying no DOI at all (software, datasets, older papers).
    Matching is one-to-one: two genuinely different works can share a slug — the
    ATLAS DataFlow conference paper and its journal version differ only by
    "baseline"/"base-line" — and letting both claim one entry makes them propose
    conflicting edits that undo each other on every run.

    Parameters
    ----------
    zrec
        One record from :func:`zotero_records`.
    by_doi, by_title
        Indexes from :func:`index_orcid_works`.
    claimed
        ``id()`` of works already taken by another record; those are skipped.

    Returns
    -------
    dict or None
        The matching ORCID work, or None when nothing free matches.
    """
    taken = claimed if claimed is not None else set()
    for index, key in ((by_doi, zrec["doi"]), (by_title, zrec["slug"])):
        if not key:
            continue
        free = [c for c in index.get(key) or [] if id(c) not in taken]
        if free:
            return max(free, key=lambda c: match_score(zrec, c))
    return None


def match_score(zrec: dict, owork: dict) -> int:
    """How well an ORCID work fits a Zotero record, for breaking slug ties.

    Only ever consulted when several candidates share a key. Taking the first
    instead cross-matched the two ATLAS DataFlow works — each then proposed
    turning the other into its own type and date, and applying that reordered
    ORCID's date-sorted feed, which flipped the pairing back on the next run.
    Scoring on content makes the pairing independent of serving order, and so
    stable across runs.

    The exact title outweighs everything: slug twins are twins precisely because
    :func:`slug_title` folded away the punctuation and case that still tell them
    apart ("base-line DataFlow" vs "baseline dataflow").

    Parameters
    ----------
    zrec
        One record from :func:`zotero_records`.
    owork
        A candidate ORCID work.

    Returns
    -------
    int
        Higher is a better fit; 0 means nothing beyond the shared key agrees.
    """
    score = 0
    zt, ot = zrec.get("title") or "", owork.get("title") or ""
    if zt and " ".join(zt.split()).casefold() == " ".join(ot.split()).casefold():
        score += 4
    if zrec.get("year") and zrec["year"] == owork.get("year"):
        score += 2
    if zrec.get("orcid_type") and zrec["orcid_type"] == owork.get("type"):
        score += 1
    return score


def authors_summary(names: list[str], width: int = 46) -> str:
    """A short, order-revealing rendering of an author list for a diff row.

    Shows the count and as many names as fit, in order — a bare count would
    hide a pure reordering, which is exactly the drift worth seeing.

    Parameters
    ----------
    names
        Credit names in order.
    width
        Roughly how many characters of names to show.

    Returns
    -------
    str
        e.g. ``"André Anjos, Jane Roe, … (3)"``, or ``"—"`` when empty.
    """
    if not names:
        return "—"
    joined = ", ".join(names)
    if len(joined) > width:
        joined = joined[:width].rsplit(", ", 1)[0] + ", …"
    return f"{joined} ({len(names)})"


def format_date(year: int | None, month: int | None, day: int | None) -> str:
    """A publication date as ``YYYY-MM-DD``, trimmed at the first unknown part.

    Parameters
    ----------
    year, month, day
        Components; 0 or None means unknown.

    Returns
    -------
    str
        e.g. ``"2024-09-13"``, ``"2024-09"``, ``"2024"`` or ``"—"``.
    """
    if not year:
        return "—"
    if not month:
        return str(year)
    if not day:
        return f"{year}-{month:02d}"
    return f"{year}-{month:02d}-{day:02d}"


def date_mismatch(z: dict, o: dict) -> bool:
    """Whether ORCID's publication date disagrees with what Zotero *knows*.

    Compared component by component, and only for components Zotero actually
    has. Zotero records the year alone for 125 of these 145 works while ORCID
    often holds a full Crossref date, so demanding an exact match would strip a
    known month and day off most of the record. A missing month in Zotero means
    "unknown", never "no month".

    Parameters
    ----------
    z
        One record from :func:`zotero_records`.
    o
        The ORCID work it matched.

    Returns
    -------
    bool
        True when at least one component Zotero knows differs on ORCID.
    """
    if z.get("year") and z["year"] != o.get("year"):
        return True
    if z.get("month") and z["month"] != (o.get("month") or 0):
        return True
    return bool(z.get("day") and z["day"] != (o.get("day") or 0))


def missing_identifiers(z: dict, o: dict) -> list[dict]:
    """Zotero identifiers that ORCID's matched work does not already carry.

    One-directional, like every other rule here: identifiers ORCID has and
    Zotero does not are left alone, because ORCID's are often richer (this
    record holds ``uri`` ids for OpenReview pages that Zotero never had).

    Parameters
    ----------
    z
        One record from :func:`zotero_records`.
    o
        The ORCID work it matched.

    Returns
    -------
    list of dict
        The identifiers to add, in Zotero's order.
    """
    have = {(i["type"], normalize_identifier(i["type"], i["value"]))
            for i in o.get("identifiers") or []}
    return [i for i in z.get("identifiers") or []
            if (i["type"], normalize_identifier(i["type"], i["value"])) not in have]


def field_diffs(z: dict, o: dict) -> list[tuple[str, str, str]]:
    """(field, 'ORCID has', 'Zotero has') rows where ORCID should catch up.

    Deliberately one-directional: it only reports what ORCID is *missing* or
    has *wrong*, never the reverse, because Zotero is the source of truth.

    Parameters
    ----------
    z
        One record from :func:`zotero_records`.
    o
        The ORCID work it matched, from :func:`parse_orcid_works`.

    Returns
    -------
    list of tuple of str
        One ``(field, orcid_value, zotero_value)`` row per difference, empty
        when ORCID already carries everything Zotero knows.
    """
    rows = []
    if z["pdf"] and not o.get("url"):
        rows.append(("URL (public PDF)", "—", z["pdf"]))
    if z["orcid_type"] and o.get("type") and o["type"] != z["orcid_type"]:
        rows.append(("work-type", o["type"], z["orcid_type"]))
    if z["container"] and not o.get("container"):
        rows.append(("venue", "—", z["container"]))
    if date_mismatch(z, o):
        rows.append(("date", format_date(o.get("year"), o.get("month"), o.get("day")),
                     format_date(z["year"], z["month"], z["day"])))
    # `authors` and `language` only exist once enrich_orcid_works has run; the
    # `in` guards keep an unenriched work from looking as though ORCID had
    # nothing, which would propose rewriting every author list on the record.
    if "authors" in o and z.get("authors") and z["authors"] != o["authors"]:
        rows.append(("authors", authors_summary(o["authors"]),
                     authors_summary(z["authors"])))
    if "language" in o and z.get("language") and z["language"] != o["language"]:
        rows.append(("language", o["language"] or "—", z["language"]))
    for ident in missing_identifiers(z, o):
        rows.append(("identifier", "—",
                     f"{ident['type']}: {ident['value']} ({ident['relationship']})"))
    # The BibTeX citation is what grant systems ingest, so it tracks Zotero
    # like everything else. Compared whitespace-insensitively: ORCID re-flows
    # what it stores, and a re-flow is not drift.
    if "citation" in o and z.get("bibtex") and (
        o.get("citation_type") != "bibtex"
        or normalize_bibtex(o.get("citation")) != normalize_bibtex(z["bibtex"])
    ):
        rows.append(("citation", o.get("citation_type") or "—", "bibtex"))
    # Names can match while the work is still not *linked* to the profile, which
    # is the difference between ORCID's "Add contributor" and "Add yourself as a
    # contributor". Without this row an already-synced work would never be
    # revisited, and the link would only ever reach brand-new entries.
    if "self_linked" in o and not o["self_linked"] and any(
        normalize_author_name(a) == SELF_NAME for a in z.get("authors") or []
    ):
        rows.append(("profile link", "—", "linked to ORCID iD"))
    return rows


def diff_against_orcid(zrecs: list[dict], orcid: list[dict]) -> dict:
    """The Zotero-to-ORCID difference, as both the report and the sync see it.

    Pure, so it is testable without touching the network; the callers fetch.

    Parameters
    ----------
    zrecs
        Records from :func:`zotero_records`.
    orcid
        Works from :func:`parse_orcid_works`.

    Returns
    -------
    dict
        ``missing`` — Zotero records absent from ORCID, to be added.
        ``outdated`` — ``(zrec, owork, diffs)`` triples for matched works ORCID
        should catch up on; *owork* carries the put-code the sync edits.
        ``orphan`` — ORCID works no Zotero record matched; reported, never
        deleted.
    """
    by_doi, by_title = index_orcid_works(orcid)

    # Matching is one-to-one, and DOIs are resolved in a first pass so an
    # identifier-less title twin can never steal the work its DOI names.
    # Whatever is left unclaimed is genuinely missing from ORCID.
    pairs: list[tuple[dict, dict | None]] = [(z, None) for z in zrecs]
    claimed: set[int] = set()

    for i, (z, _) in enumerate(pairs):
        if not z["doi"]:
            continue
        o = match(z, by_doi, {}, claimed)
        if o is not None:
            claimed.add(id(o))
            pairs[i] = (z, o)

    for i, (z, o) in enumerate(pairs):
        if o is not None:
            continue
        cand = match(z, {}, by_title, claimed)
        if cand is not None:
            claimed.add(id(cand))
            pairs[i] = (z, cand)

    missing, outdated = [], []
    for z, o in pairs:
        if o is None:
            missing.append(z)
            continue
        diffs = field_diffs(z, o)
        if diffs:
            outdated.append((z, o, diffs))
    orphan = [o for o in orcid if id(o) not in claimed]
    return {"missing": missing, "outdated": outdated, "orphan": orphan}


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
