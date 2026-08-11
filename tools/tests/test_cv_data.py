"""Offline unit tests for tools/build-cv.py, the CV's data step.

The interesting logic is the translation between the website's shapes and what
neat-cv expects: display names into Hayagriva's ``Surname, Given``, and an
outputs.json entry into a Hayagriva record. Everything else is front-matter
plumbing, covered by the end-to-end test at the bottom, which runs the real
generator over the real content tree.
"""

import importlib.util
import pathlib
import sys

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


def test_patent_number_stands_in_for_pages():
    pub = bcv.hayagriva(article(type="Patent", container=None, pages=None,
                                number="WO/2019/150254", doi=None))
    assert pub["page-range"] == "WO/2019/150254"


def test_build_over_the_real_content_tree():
    """The generator must survive every page actually in the repository, and
    hand back the sections cv/cv.typ indexes into."""
    data = bcv.build()
    assert set(data) == {"publications", "software", "datasets", "supervision",
                         "teaching", "projects"}
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
