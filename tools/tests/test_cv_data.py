"""Offline unit tests for tools/build-cv.py, the CV's data step.

The interesting logic is the translation between the website's shapes and what
neat-cv expects: display names into Hayagriva's ``Surname, Given``, and an
outputs.json entry into a Hayagriva record. Everything else is front-matter
plumbing, covered by the end-to-end test at the bottom, which runs the real
generator over the real content tree.
"""

import datetime
import importlib.util
import json
import pathlib
import sys

import pytest

TOOLS = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(TOOLS))

# The script has a dash in its name, so it cannot be imported by name.
_spec = importlib.util.spec_from_file_location("build_cv", TOOLS / "build-cv.py")
bcv = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(bcv)


def test_author_names_become_hayagriva():
    # the one that must be exact: neat-cv matches highlight-authors on this
    assert bcv.hayagriva_author("André Anjos") == "Anjos, André"
    assert bcv.hayagriva_author("Jean-Marc Odobez") == "Odobez, Jean-Marc"
    # particles glued to the surname they belong to
    assert bcv.hayagriva_author("Ludwig van Beethoven") == "van Beethoven, Ludwig"
    # a stray particle mid-name is dropped rather than initialised as "d."
    assert bcv.hayagriva_author("Tiago de Freitas Pereira") == "Pereira, Tiago Freitas"
    # a mononym survives untouched
    assert bcv.hayagriva_author("Spot") == "Spot"


def article(**over):
    entry = {
        "key": "anjos_fair_2026", "title": "Fair Foundation Models",
        "authors": ["André Anjos"], "type": "Journal Article", "year": 2026,
        "container": "Nature", "volume": "12", "issue": "3", "pages": "1-10",
        "number": None, "doi": "10.1145/3793542", "url": None, "pdf": None,
    }
    entry.update(over)
    return entry


def test_hayagriva_carries_the_locators():
    pub = bcv.hayagriva(article())
    assert pub["author"] == ["Anjos, André"]
    assert pub["parent"] == {"type": "periodical", "title": "Nature",
                             "volume": "12", "issue": "3"}
    assert pub["page-range"] == "1-10"
    assert pub["serial-number"] == {"doi": "10.1145/3793542"}
    # a conference paper's parent is a proceedings — that is what makes neat-cv
    # print "in <venue>"
    assert bcv.hayagriva(article(type="Conference Paper"))["parent"]["type"] == (
        "proceedings"
    )


def test_hayagriva_omits_what_is_absent():
    pub = bcv.hayagriva(article(container=None, volume=None, issue=None,
                                pages=None, doi=None, url="https://example/p"))
    assert "parent" not in pub and "page-range" not in pub
    # no DOI: the paper page stands in as the link
    assert "serial-number" not in pub and pub["url"] == "https://example/p"


def test_the_public_pdf_outranks_the_paper_page():
    # A DOI-less work may carry both; the CV links the file, not the landing page.
    both = bcv.hayagriva(article(doi=None, url="https://example/p",
                                 pdf="https://example/f.pdf"))
    assert both["url"] == "https://example/f.pdf"
    # a DOI still outranks either
    assert "url" not in bcv.hayagriva(article(url="https://example/p",
                                              pdf="https://example/f.pdf"))


def test_patent_number_stands_in_for_pages():
    pub = bcv.hayagriva(article(type="Patent", container=None, pages=None,
                                number="WO/2019/150254", doi=None))
    assert pub["page-range"] == "WO/2019/150254"


def test_output_stats_count_every_output_there_is():
    entries = [
        article(key="a", type="Journal Article", year=2026),
        article(key="b", type="Conference Paper", year=2026),
        article(key="c", type="Conference Paper", year=1999),
        article(key="d", type="Software", year=1999),
        # the minor types share one neutral wedge
        article(key="e", type="Patent", year=1999),
        article(key="f", type="Dataset", year=2026),
        article(key="g", type="Press", year=2026),
    ]
    stats = bcv.output_stats(entries)
    assert [(s["label"], s["count"]) for s in stats["all"]] == [
        ("Journals", 1), ("Conferences", 2), ("Software", 1),
        ("Datasets", 1), ("Other", 2),
    ]
    # the recent window is the last RECENT_YEARS calendar years, inclusive
    assert [(s["label"], s["count"]) for s in stats["recent"]] == [
        ("Journals", 1), ("Conferences", 1), ("Datasets", 1), ("Other", 1),
    ]
    assert stats["since"] == datetime.date.today().year - bcv.RECENT_YEARS + 1
    # THE invariant: the chart accounts for every output, so its total is the
    # same number the website prints under the list
    assert sum(s["count"] for s in stats["all"]) == len(entries)
    # every slice carries both colour steps, so the PDF and the page cannot
    # colour one category two ways
    palette = {s["label"]: s for s in json.loads(
        bcv.OUTPUT_TYPES.read_text(encoding="utf-8"))["slices"]}
    assert all(s["light"] == palette[s["label"]]["light"] for s in stats["all"])
    assert all(s["dark"] == palette[s["label"]]["dark"] for s in stats["all"])


def test_an_unclaimed_output_type_fails_the_build():
    """A new Zotero type nobody added to data/outputtypes.json would silently
    shrink the chart below the number of outputs the site lists. Stop the build
    instead — this guard is what makes the two totals verifiable, not just equal
    today."""
    with pytest.raises(SystemExit) as exc:
        bcv.output_stats([article(key="a", type="Sculpture", year=2026)])
    assert "Sculpture" in str(exc.value) and "outputtypes.json" in str(exc.value)


def test_build_over_the_real_content_tree():
    """The generator must survive every page actually in the repository, and
    hand back the sections cv/cv.typ indexes into."""
    data = bcv.build()
    assert set(data) == {"publications", "output-stats", "software", "datasets",
                         "supervision", "teaching", "projects"}
    assert data["publications"], "no publication groups"
    for group in data["publications"]:
        assert group["entries"], f"empty group: {group['label']}"
        for key, pub in group["entries"].items():
            assert pub["author"], f"{key} would render with no authors"
            assert pub["date"], f"{key} has no year and would be dropped silently"
    # every entry-shaped section speaks neat-cv's `entry()` signature
    fields = {"title", "date", "institution", "location", "description", "url"}
    for name in ("software", "datasets", "supervision", "teaching", "projects"):
        assert data[name], f"{name} came out empty"
        for record in data[name]:
            assert set(record) == fields, f"{name}: {record}"
            assert record["title"]


def test_hand_written_contributions_carry_every_key_the_cv_reads():
    """data/contributions.json is the one funding file nothing generates.

    `grant()` in cv/cv.typ dereferences its keys directly, and Typst panics on a
    missing one — mid-build, with no mention of which entry is at fault. Fail
    here instead, where the message names it, and check the `role` that is the
    whole reason the file exists.
    """
    doc = json.loads(
        (bcv.ROOT / "data" / "contributions.json").read_text(encoding="utf-8")
    )
    assert doc["entries"], "no contributed grants — delete the file instead"
    for e in doc["entries"]:
        assert e.get("role", "").strip(), f"{e.get('title')} states no role"
        for key in ("title", "start", "end", "instrument", "funder", "url"):
            assert key in e, f"{e.get('title')} has no `{key}` — Typst will panic"
