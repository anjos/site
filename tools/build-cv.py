#!/usr/bin/env python3
"""Assemble cv/generated.yaml — everything the CV borrows from the website.

Typst reads JSON, YAML and TOML on its own, so `cv/cv.typ` pulls
data/funding.json, data/cv.json, data/bio.yaml and hugo.toml straight from
disk. This tool exists only for the two things Typst cannot do:

  * read the YAML front-matter buried in `content/**/*.md`;
  * turn data/outputs.json into the Hayagriva form neat-cv's `publications()`
    expects, keyed by BetterBibTeX citation key.

Everything it writes is derived from committed data, so cv/generated.yaml is
git-ignored and rebuilt by `pixi run cv`. Nothing here is a source of truth:
add a grant on ORCID, a paper in Zotero, a thesis in content/theses/.

Sections that carry no website equivalent — employment, education, community
service, skills, bibliometrics — live hand-written in data/cv.json and are
read by cv/cv.typ directly.
"""

from __future__ import annotations

import collections
import datetime
import json
import pathlib
import re
import sys
import tomllib

import yaml

ROOT = pathlib.Path(__file__).resolve().parent.parent
CONTENT = ROOT / "content"
OUTPUTS = ROOT / "data" / "outputs.json"
GENERATED = ROOT / "cv" / "generated.yaml"

# outputs.json type -> CV heading, in print order. Types missing here are
# deliberate: Software and Dataset are rendered as entries (they want a summary
# and a repository, not a citation), and Press/Presentation belong to the
# website's Media section rather than to a CV.
PUBLICATION_GROUPS = (
    ("Journal Article", "Journal Articles"),
    ("Conference Paper", "Conference Papers"),
    ("Book Chapter", "Book Chapters"),
    ("Preprint", "Preprints"),
    ("Report", "Technical Reports"),
    ("Patent", "Patents"),
    ("Thesis", "Theses"),
)

# Hayagriva parent type per output type. neat-cv prints "in <venue>" only for a
# `proceedings` parent, which is exactly the conference-paper convention.
PARENT_TYPE = {"Conference Paper": "proceedings", "Book Chapter": "anthology"}

# How the donut charts group and colour outputs — shared with the website, which
# renders the same two charts on /outputs/. See the comment in the file itself
# for why there are five slices and not nine.
OUTPUT_TYPES = ROOT / "data" / "outputtypes.json"
RECENT_YEARS = 5

# Nobiliary particles, folded into the surname when they directly precede it.
PARTICLES = frozenset(
    ("de", "del", "della", "da", "das", "dos", "van", "von", "der", "den",
     "ten", "ter", "di", "du", "la", "le", "bin", "al")
)


# --------------------------------------------------------------------------- #
# Front matter
# --------------------------------------------------------------------------- #
def front_matter(path: pathlib.Path) -> dict:
    """The YAML front-matter block of a Hugo content page.

    Parameters
    ----------
    path
        The Markdown file to read.

    Returns
    -------
    dict
        The parsed front matter.

    Raises
    ------
    SystemExit
        If the file opens with no ``---`` delimited block. `check-content`
        would have caught it first; this is the belt to that's braces.
    """
    text = path.read_text(encoding="utf-8")
    match = re.match(r"---\r?\n(.*?)\r?\n---\r?\n", text, re.S)
    if not match:
        sys.exit(f"! {path.relative_to(ROOT)} has no YAML front matter.")
    return yaml.safe_load(match.group(1)) or {}


def pages(subdir: str, pattern: str = "*.md") -> list[tuple[pathlib.Path, dict]]:
    """Every content page under `subdir` with its front matter, `_index` aside."""
    found = sorted((CONTENT / subdir).glob(pattern))
    return [(p, front_matter(p)) for p in found if p.stem != "_index"]


def base_url() -> str:
    """The site's public base URL, so CV links to project pages survive a move."""
    return tomllib.loads((ROOT / "hugo.toml").read_text(encoding="utf-8"))["baseURL"]


def year_of(value) -> str:
    """The four-digit year of a front-matter date, which PyYAML hands over as a
    `date`, a `datetime`, or a plain string depending on how it was written."""
    return str(value)[:4] if value else ""


# --------------------------------------------------------------------------- #
# Publications (Hayagriva)
# --------------------------------------------------------------------------- #
def hayagriva_author(display_name: str) -> str:
    """Render a display name in the ``Surname, Given`` form neat-cv expects.

    neat-cv canonicalises every author to ``Surname, Given`` and prints it as
    initials plus surname, and it matches ``highlight-authors`` against that
    same canonical string. data/outputs.json stores display names instead, so
    they are split here: the surname is the last token together with any
    lowercase particles directly before it ("van der Berg"). Remaining
    lowercase tokens are dropped from the given names, so "Tiago de Freitas
    Pereira" initialises as "T. F. Pereira" and not "T. d. F. Pereira".

    Parameters
    ----------
    display_name
        A name as written on the website, e.g. ``"André Anjos"``.

    Returns
    -------
    str
        ``"Anjos, André"``; a single-token name is returned unchanged.
    """
    tokens = display_name.split()
    if len(tokens) < 2:
        return display_name
    first_of_surname = len(tokens) - 1
    while first_of_surname > 1 and tokens[first_of_surname - 1].lower() in PARTICLES:
        first_of_surname -= 1
    surname = " ".join(tokens[first_of_surname:])
    given = " ".join(t for t in tokens[:first_of_surname] if not t.islower())
    return f"{surname}, {given}" if given else surname


def hayagriva(entry: dict) -> dict:
    """One data/outputs.json entry as a Hayagriva publication.

    Parameters
    ----------
    entry
        An entry of ``data/outputs.json``.

    Returns
    -------
    dict
        A Hayagriva record. Only the keys neat-cv reads are emitted, and empty
        ones are omitted rather than set to null — its formatter tests for
        presence, not for truth.
    """
    pub: dict = {
        "type": "article",
        "title": entry["title"],
        "author": [hayagriva_author(a) for a in entry["authors"]],
        "date": entry["year"],
    }
    if entry.get("container"):
        parent = {
            "type": PARENT_TYPE.get(entry["type"], "periodical"),
            "title": entry["container"],
        }
        if entry.get("volume"):
            parent["volume"] = entry["volume"]
        if entry.get("issue"):
            parent["issue"] = entry["issue"]
        pub["parent"] = parent
    # A patent has no venue; its number is the thing that identifies it.
    if entry.get("pages") or entry.get("number"):
        pub["page-range"] = entry.get("pages") or entry["number"]
    if entry.get("doi"):
        pub["serial-number"] = {"doi": entry["doi"]}
    elif entry.get("url") or entry.get("pdf"):
        pub["url"] = entry.get("url") or entry["pdf"]
    return pub


def publication_groups(entries: list[dict]) -> list[dict]:
    """The publication sections of the CV, in print order, empty ones dropped."""
    groups = []
    for out_type, label in PUBLICATION_GROUPS:
        selected = {e["key"]: hayagriva(e) for e in entries if e["type"] == out_type}
        if selected:
            groups.append({"label": label, "entries": selected})
    return groups


# --------------------------------------------------------------------------- #
# Entry-shaped sections
# --------------------------------------------------------------------------- #
def entry(title, date="", institution="", location="", description="", url="") -> dict:
    """A record shaped like neat-cv's `entry()` arguments, so cv.typ can render
    any section without knowing where it came from. `url` is the one addition:
    cv.typ prints it as a trailing link, which `entry()` has no field for."""
    return {
        "title": title,
        "date": date,
        "institution": institution,
        "location": location,
        "description": description,
        "url": url,
    }


def software_and_data(entries: list[dict]) -> tuple[list[dict], list[dict]]:
    """The Open Software and Open Data sections, newest first.

    These are research outputs like any other, but a citation is the wrong
    shape for them: what a reader wants is what the thing does and where to get
    it, so they become entries with the summary as description.
    """
    def section(out_type: str, url_of) -> list[dict]:
        chosen = [e for e in entries if e["type"] == out_type]
        chosen.sort(key=lambda e: (e["year"] or 0, e["month"] or 0), reverse=True)
        return [
            entry(
                title=e["title"],
                date=str(e["year"] or ""),
                description=(e.get("summary") or "").strip(),
                url=url_of(e) or "",
            )
            for e in chosen
        ]

    software = section("Software", lambda e: (e.get("links") or {}).get("repo"))
    datasets = section(
        "Dataset",
        lambda e: e.get("url") or (f"https://doi.org/{e['doi']}" if e.get("doi") else ""),
    )
    return software, datasets


def supervision() -> list[dict]:
    """Supervised students, newest first, from content/theses/."""
    records = []
    for _, fm in pages("theses"):
        role = fm.get("role") or f"{fm['level']} thesis"
        records.append(
            (
                year_of(fm.get("date")),
                entry(
                    title=fm["author"],
                    date=year_of(fm.get("date")),
                    institution=role,
                    location=fm.get("university", ""),
                    description=fm["title"],
                    url=fm.get("report", ""),
                ),
            )
        )
    return [e for _, e in sorted(records, key=lambda r: r[0], reverse=True)]


def teaching() -> list[dict]:
    """Courses, newest first, from content/teaching/."""
    records = []
    for _, fm in pages("teaching"):
        span = fm.get("years") or year_of(fm.get("date"))
        # Sort on the year a course last ran, then on the year it started, so a
        # long-running course outranks a one-off that happened in the meantime.
        years = sorted(re.findall(r"\d{4}", span))
        records.append(
            (
                (years[-1], years[0]) if years else ("", ""),
                entry(
                    title=fm["title"],
                    date=span,
                    institution=fm.get("institution", ""),
                    description=fm.get("summary", "").strip(),
                ),
            )
        )
    return [e for _, e in sorted(records, key=lambda r: r[0], reverse=True)]


def projects(entries: list[dict]) -> list[dict]:
    """Research areas from content/projects/, in the website's own order.

    A project page carries no dates, so its span is read off the outputs it
    claims: the site already resolves `research_outputs:` by DOI or citation
    key, and the same resolution here gives a first and last year for free.
    """
    by_ref = {}
    for e in entries:
        by_ref[e["key"]] = e
        if e.get("doi"):
            by_ref[e["doi"]] = e

    records = []
    for path, fm in pages("projects", "*/index.md"):
        years = sorted(
            by_ref[r]["year"]
            for r in (fm.get("research_outputs") or [])
            if r in by_ref and by_ref[r]["year"]
        )
        span = ""
        if years:
            span = str(years[0]) if years[0] == years[-1] else f"{years[0]}–{years[-1]}"
        records.append(
            (
                fm.get("weight", 999),
                entry(
                    title=fm["title"],
                    date=span,
                    institution="; ".join(fm.get("partners") or []),
                    description=fm.get("summary", "").strip(),
                    url=f"{base_url()}projects/{path.parent.name}/",
                ),
            )
        )
    return [e for _, e in sorted(records, key=lambda r: r[0])]


def output_stats(entries: list[dict]) -> dict:
    """Slice counts for the two pie charts, whole-career and recent.

    Parameters
    ----------
    entries
        The entries of ``data/outputs.json``.

    Returns
    -------
    dict
        ``since`` (first year of the recent window), and ``all`` / ``recent``,
        each a list of ``{label, color, count}`` in data/outputtypes.json order
        with the empty slices dropped. Counts cover only the types that file
        names, which are exactly the outputs the CV goes on to list.
    """
    since = datetime.date.today().year - RECENT_YEARS + 1
    slices = json.loads(OUTPUT_TYPES.read_text(encoding="utf-8"))["slices"]

    def tally(chosen: list[dict]) -> list[dict]:
        counted = collections.Counter(e["type"] for e in chosen)
        out = []
        for s in slices:
            # `cvTypes` narrows a slice to what the CV lists — the Other wedge
            # carries the website's press items and presentations, which the CV
            # does not print and must therefore not count either.
            n = sum(counted[t] for t in s.get("cvTypes", s["types"]))
            if n:
                # The CV is printed: the light step is the only one it can use.
                out.append({"label": s["label"], "color": s["light"], "count": n})
        return out

    return {
        "since": since,
        "all": tally(entries),
        "recent": tally([e for e in entries if (e["year"] or 0) >= since]),
    }


# --------------------------------------------------------------------------- #
def build() -> dict:
    """Everything the CV takes from the website, ready to be dumped as YAML."""
    entries = json.loads(OUTPUTS.read_text(encoding="utf-8"))["entries"]
    software, datasets = software_and_data(entries)
    return {
        "publications": publication_groups(entries),
        "output-stats": output_stats(entries),
        "software": software,
        "datasets": datasets,
        "supervision": supervision(),
        "teaching": teaching(),
        "projects": projects(entries),
    }


def main() -> int:
    data = build()
    GENERATED.parent.mkdir(parents=True, exist_ok=True)
    GENERATED.write_text(
        "# GENERATED by tools/build-cv.py — do not edit, do not commit.\n"
        + yaml.safe_dump(data, allow_unicode=True, sort_keys=False, width=100),
        encoding="utf-8",
    )
    counts = ", ".join(
        f"{len(g['entries'])} {g['label'].lower()}" for g in data["publications"]
    )
    print(
        f"Wrote {GENERATED.relative_to(ROOT)}: {counts}; "
        f"{len(data['software'])} software, {len(data['datasets'])} datasets, "
        f"{len(data['supervision'])} supervised, {len(data['teaching'])} courses, "
        f"{len(data['projects'])} projects."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
