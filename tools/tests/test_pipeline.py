"""Offline unit tests for the Zotero-sourced publication tooling (no network)."""

import pathlib
import sys

import pytest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

import zotero_common as zc  # noqa: E402


# --------------------------------------------------------------------------- #
# Fixtures — shapes as returned by the Zotero public feed / ORCID public API.
# --------------------------------------------------------------------------- #
ZOTERO_ITEMS = [
    {   # a conference paper with a public PDF child + a DOI
        "key": "AAAA1111",
        "data": {
            "itemType": "conferencePaper",
            "title": "Fair Foundation Models for Medical Image Analysis",
            "citationKey": "queiroz_fair_2026",
            "proceedingsTitle": "Proc. of MedAI",
            "DOI": "https://doi.org/10.1145/3793542",
            "url": "",
            "date": "05/2026",
            "creators": [
                {"creatorType": "author", "firstName": "Dilermando", "lastName": "Queiroz"},
                {"creatorType": "author", "firstName": "A.", "lastName": "Anjos"},
                {"creatorType": "editor", "firstName": "Ed", "lastName": "Itor"},
            ],
        },
        "meta": {"parsedDate": "2026-05-01"},
    },
    {   # public PDF attachment of AAAA1111
        "key": "PDF00001",
        "data": {"itemType": "attachment", "linkMode": "imported_file",
                 "contentType": "application/pdf", "parentItem": "AAAA1111",
                 "inPublications": True},
    },
    {   # an older DOI-less preprint, no PDF
        "key": "BBBB2222",
        "data": {
            "itemType": "preprint",
            "title": "A Talk Without DOI",
            "citationKey": "heusch_talk_2019",
            "repository": "arXiv",
            "date": "2019",
            "creators": [
                {"creatorType": "author", "firstName": "Guillaume", "lastName": "Heusch"},
                {"creatorType": "author", "firstName": "André", "lastName": "Anjos"},
            ],
        },
        "meta": {"parsedDate": "2019"},
    },
    {   # a note child — must be ignored
        "key": "NOTE0001",
        "data": {"itemType": "note", "parentItem": "AAAA1111"},
    },
]

ORCID_PAYLOAD = {
    "group": [
        {
            "external-ids": {"external-id": [
                {"external-id-type": "doi", "external-id-value": "10.1145/3793542"}]},
            "work-summary": [{
                "put-code": "111",
                "title": {"title": {"value": "Fair Foundation Models for Medical Image Analysis"}},
                "publication-date": {"year": {"value": "2026"}},
                "type": "conference-paper",
            }],
        },
        {
            "external-ids": {"external-id": []},
            "work-summary": [{
                "put-code": "222",
                "title": {"title": {"value": "An ORCID-only Work"}},
                "publication-date": {"year": {"value": "2015"}},
                "type": "journal-article",
            }],
        },
    ]
}


# --------------------------------------------------------------------------- #
def test_normalize_doi():
    assert zc.normalize_doi("https://doi.org/10.1/AbC") == "10.1/abc"
    assert zc.normalize_doi("doi:10.2/x") == "10.2/x"
    assert zc.normalize_doi(None) is None and zc.normalize_doi("") is None


def test_normalize_author_name():
    for v in ["André Anjos", "Andre Anjos", "A. Anjos", "Andre Rabello dos Anjos", "A. dos Anjos"]:
        assert zc.normalize_author_name(v) == "André Anjos"
    assert zc.normalize_author_name("Ivana Chingovska") == "Ivana Chingovska"


def test_parsed_date():
    assert zc.parsed_date({}, {"parsedDate": "2026-05-01"}) == (2026, 5)
    assert zc.parsed_date({}, {"parsedDate": "2019"}) == (2019, 0)
    assert zc.parsed_date({"date": "05/2026"}, {}) == (2026, 5)
    assert zc.parsed_date({"date": "6 2005"}, {}) == (2005, 0)
    assert zc.parsed_date({"date": ""}, {}) == (None, 0)


def test_type_mapping():
    assert zc.type_label("journalArticle") == "Journal Article"
    assert zc.orcid_type("conferencePaper") == "conference-paper"
    assert zc.type_label("somethingElse") == "Other"
    # datasets are first-class research outputs
    assert zc.type_label("dataset") == "Dataset"
    assert zc.orcid_type("dataset") == "data-set"
    assert zc.type_slug("dataset") == "datasets"
    assert zc.type_slug("journalArticle") == "journals"
    assert zc.type_slug("somethingElse") == "other"
    # a conference abstract lives as a Zotero `presentation`
    assert zc.type_label("presentation") == "Presentation"
    assert zc.orcid_type("presentation") == "lecture-speech"
    assert zc.type_slug("presentation") == "presentations"


def test_presenter_is_an_author():
    # a presentation's `presenter` creators are surfaced as authors, and its
    # meetingName resolves as the venue
    d = {"itemType": "presentation", "title": "t", "meetingName": "Union World Conf",
         "creators": [{"creatorType": "presenter", "firstName": "Geoffrey", "lastName": "Raposo"},
                      {"creatorType": "presenter", "firstName": "André", "lastName": "Anjos"}]}
    assert zc.authors_of(d) == ["Geoffrey Raposo", "André Anjos"]
    assert zc.venue_of(d) == "Union World Conf"


def test_authors_and_venue():
    d = ZOTERO_ITEMS[0]["data"]
    # editor dropped, André normalised
    assert zc.authors_of(d) == ["Dilermando Queiroz", "André Anjos"]
    assert zc.venue_of(d) == "Proc. of MedAI"
    assert zc.venue_of(ZOTERO_ITEMS[2]["data"]) == "arXiv"  # repository fallback


def test_citation_key_is_required():
    """Zotero's BetterBibTeX key is the only key: `research_outputs:` refs address
    a work by it, so an item without one is an error to fix in Zotero, never
    something to paper over with a generated key nobody could have linked to."""
    item = {"key": "CK000001", "data": {
        "itemType": "journalArticle", "title": "Some Paper", "date": "2020",
        "citationKey": "curated_key_2020",
        "creators": [{"creatorType": "author", "firstName": "A.", "lastName": "Anjos"}]}}
    assert zc.build_site_entry(item, None, "5992358")["key"] == "curated_key_2020"
    del item["data"]["citationKey"]
    with pytest.raises(ValueError, match="no BetterBibTeX citation key"):
        zc.build_site_entry(item, None, "5992358")


def test_duplicate_citation_keys_raise():
    """A curated key is authoritative: a clash is Zotero's problem, not ours to
    paper over with a suffix."""
    def item(zkey, title):
        return {"key": zkey, "data": {
            "itemType": "journalArticle", "title": title, "date": "2020",
            "citationKey": "same_key_2020",
            "creators": [{"creatorType": "author", "lastName": "Anjos"}]}}
    with pytest.raises(ValueError, match="duplicate citation keys"):
        zc.build_entries([item("AAAA0001", "One"), item("BBBB0002", "Two")], "5992358")


def test_software_entry():
    item = {"key": "SW000001", "data": {
        "itemType": "computerProgram", "title": "mytool", "rights": "GPL-3.0",
        "citationKey": "anjos_mytool_2023",
        "abstractNote": "Does useful things.", "url": "https://git/repo", "date": "2023",
        "extra": "Docs: https://d/\nPyPI: https://p/\nconda-forge: https://c/\nArchived: true"},
        "meta": {"parsedDate": "2023"}}
    e = zc.build_site_entry(item, None, "5992358")
    assert e["type"] == "Software" and e["typeslug"] == "software"
    assert zc.orcid_type("computerProgram") == "software"
    assert e["license"] == "GPL-3.0" and e["summary"] == "Does useful things."
    assert e["links"] == {"repo": "https://git/repo", "docs": "https://d/",
                          "pypi": "https://p/", "conda": "https://c/"}
    assert e["archived"] is True
    # a package without conda/archived
    assert zc.parse_extra_links("Docs: https://x/\nPyPI: https://y/") == {
        "docs": "https://x/", "pypi": "https://y/"}


def test_publication_companion_software():
    # a paper carrying companion-code repo in `extra` -> entry["software"] link,
    # surfaced beside its DOI/PDF (not a standalone Software entry)
    assert zc.parse_extra_links("Software: https://git/uveai-validation") == {
        "software": "https://git/uveai-validation"}
    item = {"key": "PUB00001", "data": {
        "itemType": "journalArticle", "title": "UveAI", "date": "2026",
        "citationKey": "anjos_uveai_2026",
        "extra": "Software: https://git/uveai-validation",
        "creators": [{"creatorType": "author", "firstName": "A.", "lastName": "Anjos"}]},
        "meta": {"parsedDate": "2026"}}
    e = zc.build_site_entry(item, None, "5992358")
    assert e["type"] == "Journal Article"
    assert e["software"] == "https://git/uveai-validation"
    # a computerProgram is NOT given a companion-software field (it *is* the software)
    sw = zc.build_site_entry({"key": "SW1", "data": {
        "itemType": "computerProgram", "title": "t", "url": "https://r",
        "citationKey": "t_2020"}, "meta": {}}, None, "x")
    assert "software" not in sw


def test_paper_page_from_homepage():
    # the paper page is the Extra `Homepage:` line; the top-level url is ignored
    assert zc.parse_extra_links("Homepage: https://h/")["homepage"] == "https://h/"
    page = zc.build_site_entry({"key": "P1", "data": {
        "itemType": "journalArticle", "title": "x", "DOI": "10.1/abc",
        "url": "https://publisher.example/junk", "citationKey": "x_page_2020",
        "extra": "Homepage: https://medai.example/paper"}, "meta": {}}, None, "u")
    assert page["url"] == "https://medai.example/paper"
    # no Homepage -> no paper page, even when the unreliable top-level url is set
    none = zc.build_site_entry({"key": "P2", "data": {
        "itemType": "journalArticle", "title": "x", "citationKey": "x_none_2020",
        "url": "https://publisher.example/junk"}, "meta": {}}, None, "u")
    assert none["url"] is None


def test_extra_field_editors():
    assert zc.set_extra_field("", "Software", "https://r") == "Software: https://r"
    # update in place, keep siblings
    e = "Docs: https://d\nSoftware: https://old\nPyPI: https://p"
    got = zc.set_extra_field(e, "Software", "https://new")
    assert got == "Docs: https://d\nSoftware: https://new\nPyPI: https://p"
    # case-insensitive label match; delete removes the line
    assert zc.del_extra_field("docs: x\nSoftware: y", "software") == "docs: x"
    # collapse duplicates on set
    assert zc.set_extra_field("Software: a\nSoftware: b", "Software", "c") == "Software: c"


def test_build_site_entry_pdf_and_doi():
    e = zc.build_site_entry(ZOTERO_ITEMS[0], "PDF00001", "5992358")
    assert e["type"] == "Conference Paper"
    assert e["doi"] == "10.1145/3793542"
    assert e["url"] is None   # no distinct paper page; DOI carries the link
    assert e["pdf"] == "https://api.zotero.org/users/5992358/publications/items/PDF00001/file"
    assert e["year"] == 2026 and e["month"] == 5
    assert e["authors"][1] == "André Anjos"
    assert e["typeslug"] == "conferences"


def test_build_entries_end_to_end():
    entries = zc.build_entries(ZOTERO_ITEMS, "5992358")
    assert len(entries) == 2                       # note + attachment excluded
    assert [e["year"] for e in entries] == [2026, 2019]   # newest first
    top, older = entries
    assert top["pdf"] and top["pdf"].endswith("/PDF00001/file")
    assert older["pdf"] is None and older["doi"] is None  # no public PDF, no DOI


def test_related_resolution():
    # AAAA1111 (conferencePaper, has DOI) <-> BBBB2222 (preprint, no href)
    relmap = {"AAAA1111": ["BBBB2222"], "BBBB2222": ["AAAA1111"]}
    entries = zc.build_entries(ZOTERO_ITEMS, "5992358", relmap)
    pre = next(e for e in entries if e["type"] == "Preprint")
    # the related entry carries the sibling's type (for a pill) and its DOI
    assert pre["related"][0]["type"] == "Conference Paper"
    assert pre["related"][0]["doi"] == "10.1145/3793542"
    # with no relmap, nothing is linked
    assert all(not e["related"] for e in zc.build_entries(ZOTERO_ITEMS, "5992358"))


def test_parse_orcid_works():
    works = zc.parse_orcid_works(ORCID_PAYLOAD)
    assert len(works) == 2
    assert works[0]["doi"] == "10.1145/3793542"
    assert works[0]["type"] == "conference-paper"
    assert works[1]["doi"] is None and works[1]["year"] == 2015
