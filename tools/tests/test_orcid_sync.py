"""Offline unit tests for the Zotero -> ORCID difference and its WorkForms.

Two things here are load-bearing and were previously untested. First, the
matching and diffing that this tool has always reported now also decides what
gets *written*, so a wrong match is no longer a cosmetic report bug.
Second, ORCID replaces a work outright on save, which makes the read-modify-write
guard in `patch_form` the difference between updating a field and silently
dropping every field the diff does not model.

No network: ORCID and Zotero payloads are fixtures.

SPDX-FileCopyrightText: Copyright © 2026 Idiap Research Institute <contact@idiap.ch>

SPDX-License-Identifier: BSD-3-Clause
"""

import contextlib
import pathlib
import sys

import pytest

TOOLS = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(TOOLS))

import sync_orcid as so  # noqa: E402
import zotero_common as zc  # noqa: E402


def zrec(**over):
    """A Zotero-side record, with sensible defaults for everything unset."""
    rec = {
        "title": "A Paper",
        "slug": zc.slug_title("A Paper"),
        "authors": ["André Anjos"],
        "language": "en",
        "month": 0,
        "day": 0,
        "doi": None,
        "orcid_type": "journal-article",
        "container": None,
        "year": 2024,
        "url": None,
        "pdf": None,
    }
    rec.update(over)
    if "title" in over:
        rec["slug"] = zc.slug_title(over["title"])
    rec.setdefault("identifiers", [])
    if rec["doi"] and not any(i["type"] == "doi" for i in rec["identifiers"]):
        rec["identifiers"] = [{"type": "doi", "value": rec["doi"],
                               "relationship": "self"}] + rec["identifiers"]
    return rec


def owork(**over):
    """An ORCID-side work, self-asserted unless stated otherwise."""
    work = {
        "doi": None,
        "title": "A Paper",
        "container": None,
        "year": 2024,
        "month": 0,
        "day": 0,
        "self_linked": True,
        "citation": None,
        "citation_type": None,
        "identifiers": [],
        "type": "journal-article",
        "url": None,
        "putcode": 1,
        "ours": True,
    }
    work.update(over)
    return work


# --------------------------------------------------------------------------
# Source selection — which assertion in a group is ours
# --------------------------------------------------------------------------

def _summary(putcode, source_orcid=None, client=None, title="A Paper"):
    """One ORCID work-summary asserted by either the record holder or a client."""
    return {
        "put-code": putcode,
        "title": {"title": {"value": title}},
        "type": "JOURNAL_ARTICLE",
        "publication-date": {"year": {"value": "2024"}},
        "source": {
            "source-orcid": {"path": source_orcid} if source_orcid else None,
            "source-client-id": {"path": client} if client else None,
        },
    }


def test_self_asserted_distinguishes_holder_from_client():
    assert zc.self_asserted(_summary(1, source_orcid=zc.ORCID_ID))
    assert not zc.self_asserted(_summary(2, client="0000-0001-9884-1913"))


def test_pick_work_summary_prefers_ours_even_when_not_first():
    """The real record lists Crossref *before* our assertion in every co-asserted
    group, so taking summaries[0] would edit the wrong put-code."""
    crossref = _summary(211988924, client="0000-0001-9884-1913")
    mine = _summary(203605419, source_orcid=zc.ORCID_ID)
    assert zc.pick_work_summary([crossref, mine])["put-code"] == 203605419


def test_pick_work_summary_falls_back_to_first():
    only = _summary(7, client="0000-0001-9884-1913")
    assert zc.pick_work_summary([only])["put-code"] == 7


def test_parse_orcid_works_marks_ownership_and_putcode():
    payload = {"group": [{
        "external-ids": {"external-id": []},
        "work-summary": [
            _summary(99, client="0000-0001-9884-1913"),
            _summary(42, source_orcid=zc.ORCID_ID),
        ],
    }]}
    works = zc.parse_orcid_works(payload)
    assert len(works) == 1
    assert works[0]["putcode"] == 42
    assert works[0]["ours"] is True


# --------------------------------------------------------------------------
# Matching
# --------------------------------------------------------------------------

def test_match_prefers_doi_over_title():
    by_doi = {"10.1/x": [owork(putcode=10, title="Wholly Different Title")]}
    by_title = {zc.slug_title("A Paper"): [owork(putcode=20)]}
    got = zc.match(zrec(doi="10.1/x"), by_doi, by_title)
    assert got["putcode"] == 10


def test_match_falls_back_to_accent_folded_title():
    by_title = {zc.slug_title("Détection Précoce"): [owork(putcode=30)]}
    got = zc.match(zrec(title="Detection Precoce"), {}, by_title)
    assert got["putcode"] == 30


def test_match_skips_a_work_another_record_already_claimed():
    first, second = owork(putcode=1), owork(putcode=2)
    by_title = {zc.slug_title("A Paper"): [first, second]}
    got = zc.match(zrec(), {}, by_title, claimed={id(first)})
    assert got["putcode"] == 2


def test_index_orcid_works_keeps_collisions():
    orcid = [owork(putcode=1, title="Same", doi="10.1/x"),
             owork(putcode=2, title="Same", doi="10.1/x")]
    by_doi, by_title = zc.index_orcid_works(orcid)
    assert len(by_doi["10.1/x"]) == 2
    assert len(by_title[zc.slug_title("Same")]) == 2


def test_match_returns_none_when_absent():
    assert zc.match(zrec(doi="10.1/nope"), {}, {}) is None


# --------------------------------------------------------------------------
# Field diffs
# --------------------------------------------------------------------------

def test_field_diffs_empty_when_orcid_is_current():
    z = zrec(doi="10.1/x", container="Nature", year=2024)
    o = owork(doi="10.1/x", container="Nature", year=2024,
              identifiers=[{"type": "doi", "value": "10.1/x", "relationship": "self"}])
    assert zc.field_diffs(z, o) == []


def test_field_diffs_reports_each_stale_field():
    z = zrec(doi="10.1/x", container="Nature", year=2024,
             pdf="https://example.org/p.pdf", orcid_type="software")
    o = owork(doi=None, container=None, year=2023, url=None, type="journal-article")
    fields = {f for f, _h, _w in zc.field_diffs(z, o)}
    assert fields == {"identifier", "URL (public PDF)", "work-type", "venue", "date"}


def test_field_diffs_is_one_directional():
    """Zotero is the source of truth: a field ORCID has and Zotero lacks is not
    a difference to apply."""
    z = zrec(doi=None, container=None)
    o = owork(doi="10.1/x", container="Nature")
    assert zc.field_diffs(z, o) == []


# --------------------------------------------------------------------------
# Planning
# --------------------------------------------------------------------------

def test_plan_actions_splits_adds_from_edits():
    diff = {
        "missing": [zrec(title="New Work")],
        "outdated": [(zrec(title="Old Work", doi="10.1/x"),
                      owork(title="Old Work"),
                      [("identifier", "—", "doi: 10.1/x (self)")])],
        "orphan": [],
    }
    actions, skipped = so.plan_actions(diff)
    assert [a["kind"] for a in actions] == ["add", "edit"]
    assert actions[1]["putcode"] == 1
    assert skipped == []


def test_plan_actions_skips_works_asserted_by_others():
    """ORCID refuses edits from a source that did not create the item, so these
    have to be reported rather than attempted."""
    diff = {
        "missing": [],
        "outdated": [(zrec(doi="10.1/x"), owork(ours=False), [("identifier", "—", "doi: 10.1/x (self)")])],
        "orphan": [],
    }
    actions, skipped = so.plan_actions(diff)
    assert actions == []
    assert len(skipped) == 1
    assert "not editable" in skipped[0]


# --------------------------------------------------------------------------
# Form building
# --------------------------------------------------------------------------

def test_new_form_wraps_scalars_and_omits_putcode():
    form = so.new_form(zrec(title="T", container="Nature", doi="10.1/x", year=2024))
    assert form["putCode"] is None
    assert form["title"]["value"] == "T"
    assert form["journalTitle"]["value"] == "Nature"
    assert form["publicationDate"]["year"] == "2024"
    eid = form["workExternalIdentifiers"][0]
    assert eid["externalIdentifierId"]["value"] == "10.1/x"
    assert eid["externalIdentifierType"]["value"] == "doi"


def test_new_form_prefers_the_public_pdf_as_url():
    form = so.new_form(zrec(pdf="https://z/p.pdf", url="https://example.org"))
    assert form["url"]["value"] == "https://z/p.pdf"


@pytest.mark.parametrize("item_type,expected", sorted(
    (k, v[1]) for k, v in zc.ZTYPE.items()
))
def test_new_form_carries_every_orcid_work_type(item_type, expected):
    """Every Zotero type must reach ORCID as its own work-type — this is what
    BibTeX import cannot do for software and datasets."""
    form = so.new_form(zrec(orcid_type=zc.orcid_type(item_type)))
    assert form["workType"]["value"] == expected


def test_patch_form_preserves_fields_the_diff_does_not_model():
    """The read-modify-write guard. POST replaces the work, so anything dropped
    here is destroyed on ORCID."""
    current = {
        "putCode": {"value": "12345"},
        "title": so._text("Existing Title"),
        "contributors": [{"creditName": so._text("A Coauthor")}],
        "shortDescription": so._text("An abstract ORCID has and Zotero lacks."),
        "workExternalIdentifiers": [],
        "url": so._text(None),
    }
    patched = so.patch_form(current, zrec(doi="10.1/x"), [("identifier", "—", "doi: 10.1/x (self)")])

    assert patched["contributors"] == current["contributors"]
    assert patched["shortDescription"]["value"].startswith("An abstract")
    assert patched["putCode"]["value"] == "12345"
    assert patched["workExternalIdentifiers"][0]["externalIdentifierId"]["value"] == "10.1/x"


def test_patch_form_does_not_mutate_the_fetched_form():
    current = {"workExternalIdentifiers": [], "url": so._text(None)}
    so.patch_form(current, zrec(doi="10.1/x"), [("identifier", "—", "doi: 10.1/x (self)")])
    assert current["workExternalIdentifiers"] == []


def test_patch_form_applies_each_field():
    current = {
        "workExternalIdentifiers": [],
        "url": so._text(None),
        "workType": so._text("journal-article"),
        "journalTitle": so._text(None),
        "publicationDate": {"year": "2023", "month": "04", "day": None},
    }
    z = zrec(pdf="https://z/p.pdf", orcid_type="software",
             container="Nature", year=2024)
    patched = so.patch_form(current, z, [
        ("URL (public PDF)", "—", z["pdf"]),
        ("work-type", "journal-article", "software"),
        ("venue", "—", "Nature"),
        ("date", "2023", "2024"),
    ])
    assert patched["url"]["value"] == "https://z/p.pdf"
    assert patched["workType"]["value"] == "software"
    assert patched["journalTitle"]["value"] == "Nature"
    assert patched["publicationDate"]["year"] == "2024"
    assert patched["publicationDate"]["month"] == "04", "month must survive a year fix"


def test_patch_form_rejects_an_unknown_diff_field():
    """field_diffs growing a row this tool cannot apply must fail loudly, not
    silently report success while leaving ORCID stale."""
    with pytest.raises(ValueError, match="no patch rule"):
        so.patch_form({}, zrec(), [("abstract", "—", "something")])


def test_every_field_diffs_row_has_a_patch_rule():
    """The coverage guard: drive field_diffs to emit every row it can, and prove
    patch_form handles all of them."""
    z = zrec(doi="10.1/x", pdf="https://z/p.pdf", orcid_type="software",
             container="Nature", year=2024)
    o = owork(doi=None, url=None, type="journal-article", container=None, year=2023)
    diffs = zc.field_diffs(z, o)
    assert len(diffs) == 5, "fixture should trigger every rule"
    so.patch_form({"workExternalIdentifiers": []}, z, diffs)  # must not raise


def test_add_external_id_is_idempotent():
    form = {"workExternalIdentifiers": []}
    so.add_external_id(form, "doi", "10.1/x")
    so.add_external_id(form, "doi", "10.1/x")
    assert len(form["workExternalIdentifiers"]) == 1


def test_add_external_id_keeps_other_identifiers():
    form = {"workExternalIdentifiers": []}
    so.add_external_id(form, "doi", "10.1/x")
    so.add_external_id(form, "arxiv", "2401.00001")
    assert len(form["workExternalIdentifiers"]) == 2


# --------------------------------------------------------------------------
# Response handling
# --------------------------------------------------------------------------

def test_collect_errors_finds_nested_field_errors():
    """ORCID answers a rejected save with HTTP 200 and per-field errors, so a
    top-level check alone would report a silent failure as a success."""
    saved = {
        "errors": [],
        "title": {"value": "T", "errors": []},
        "publicationDate": {"year": "9999", "errors": ["Invalid date"]},
        "workExternalIdentifiers": [
            {"externalIdentifierId": {"value": "x", "errors": ["Invalid DOI"]}}
        ],
    }
    assert sorted(so.collect_errors(saved)) == ["Invalid DOI", "Invalid date"]


def test_collect_errors_empty_on_a_clean_save():
    assert so.collect_errors({"errors": [], "title": {"value": "T", "errors": []}}) == []


class _Response:
    """The parts of a Playwright APIResponse that _json_or_lapsed reads."""

    def __init__(self, url, content_type, payload=None):
        self.url = url
        self.headers = {"content-type": content_type}
        self._payload = payload

    def json(self):
        return self._payload


def test_json_or_lapsed_names_a_lapsed_session():
    """An expired session redirects to the sign-in page as HTTP 200 + HTML, so
    a bare .json() would fail with an error that hides the real cause."""
    r = _Response("https://orcid.org/signin", "text/html;charset=UTF-8")
    with pytest.raises(RuntimeError, match="session has lapsed"):
        so._json_or_lapsed(r, "fetching work 1")


def test_json_or_lapsed_passes_real_json_through():
    r = _Response("https://orcid.org/works/work.json",
                  "application/json;charset=UTF-8", {"putCode": {"value": "1"}})
    assert so._json_or_lapsed(r, "saving work")["putCode"]["value"] == "1"


def test_report_and_dry_run_never_import_playwright(monkeypatch):
    """The reason one tool can replace two: playwright is imported lazily inside
    session(), so the read-only modes keep working if the browser path breaks."""
    import builtins
    real = builtins.__import__

    def guard(name, *args, **kwargs):
        assert not name.startswith("playwright"), f"{name} imported eagerly"
        return real(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", guard)
    diff = zc.diff_against_orcid([zrec(title="New")], [])
    so.render_report([], [], diff)
    so.plan_actions(diff)


def test_render_report_has_all_three_sections():
    diff = zc.diff_against_orcid(
        [zrec(title="Missing Work")],
        [owork(title="Orphan Work", putcode=9)],
    )
    text = so.render_report([zrec()], [owork()], diff)
    assert "## 1. Missing on ORCID (1)" in text
    assert "## 2. Outdated / incomplete on ORCID (0)" in text
    assert "## 3. On ORCID, not in Zotero (1)" in text
    assert "Missing Work" in text and "Orphan Work" in text


def test_render_report_flags_works_that_are_not_ours():
    """The skip reason belongs in the report too, not only in the dry-run."""
    diff = {
        "missing": [],
        "outdated": [(zrec(doi="10.1/x"), owork(ours=False), [("identifier", "—", "doi: 10.1/x (self)")])],
        "orphan": [],
    }
    assert "**no**" in so.render_report([], [], diff)


def _fake_session(monkeypatch, fail_on=()):
    """Stand in for the browser: record writes, optionally failing some titles."""
    written = []

    @contextlib.contextmanager
    def session(_profile, _headless=None):
        yield object(), "csrf-token"

    def post_work(_ctx, _csrf, form):
        title = (form.get("title") or {}).get("value", "")
        if title in fail_on:
            raise RuntimeError("ORCID said no")
        written.append(title)
        return form

    monkeypatch.setattr(so, "session", session)
    monkeypatch.setattr(so, "post_work", post_work)
    monkeypatch.setattr(so, "fetch_work_form", lambda _c, pc: {
        "putCode": {"value": str(pc)}, "title": so._text("Old Work"),
        "workExternalIdentifiers": [],
    })
    return written


def test_apply_prints_each_change_as_it_goes(monkeypatch, capsys):
    """Progress must be visible during the run, not only summarised after it."""
    _fake_session(monkeypatch)
    actions, _ = so.plan_actions({
        "missing": [zrec(title="A New Paper", year=2026)],
        "outdated": [(zrec(title="Old Work", year=2019, doi="10.1/x"),
                      owork(title="Old Work"), [("identifier", "—", "doi: 10.1/x (self)")])],
        "orphan": [],
    })
    assert so.apply_actions(actions, delay=0) == 0

    out = capsys.readouterr().out
    assert "[1/2] add    [2026] A New Paper" in out
    assert "[2/2] update [2019] Old Work" in out
    assert "Applied 2/2 change(s)." in out


def test_apply_reports_a_failure_and_keeps_going(monkeypatch, capsys):
    """One rejected work must not abandon the other ninety."""
    written = _fake_session(monkeypatch, fail_on=("Bad Paper",))
    actions, _ = so.plan_actions({
        "missing": [zrec(title="Bad Paper"), zrec(title="Good Paper")],
        "outdated": [], "orphan": [],
    })
    assert so.apply_actions(actions, delay=0) == 1

    out = capsys.readouterr().out
    assert "! failed: ORCID said no" in out
    assert "Applied 1/2 change(s)." in out
    assert written == ["Good Paper"], "the run must continue past a failure"


# --------------------------------------------------------------------------
# Contributors
# --------------------------------------------------------------------------

def test_zotero_records_shape_carries_authors():
    """new_form reads z["authors"], so the record shape has to provide it."""
    item = {"data": {"itemType": "journalArticle", "title": "T", "creators": [
        {"creatorType": "author", "firstName": "A.", "lastName": "Anjos"},
        {"creatorType": "author", "firstName": "Jane", "lastName": "Roe"},
        {"creatorType": "editor", "firstName": "Ed", "lastName": "Itor"},
    ]}, "key": "K", "meta": {"parsedDate": "2024-05"}}
    monkey = [item]
    import unittest.mock
    with unittest.mock.patch.object(zc, "fetch_public_items", return_value=monkey):
        recs = zc.zotero_records("5992358")
    assert recs[0]["authors"] == ["André Anjos", "Jane Roe"], "editors are not authors"


def test_new_form_carries_every_author_in_order():
    form = so.new_form(zrec(authors=["André Anjos", "Jane Roe", "John Doe"]))
    names = [c["creditName"]["value"] for c in form["contributors"]]
    assert names == ["André Anjos", "Jane Roe", "John Doe"]
    assert all(c["contributorRole"]["value"] == "author" for c in form["contributors"])


def test_new_form_handles_a_work_with_no_authors():
    assert so.new_form(zrec(authors=[]))["contributors"] == []


def test_contributor_omits_sequence():
    """Left out on purpose — the list order carries authorship order, and this
    avoids guessing a second enum on an undocumented endpoint."""
    assert "contributorSequence" not in so.contributor("André Anjos")


# --------------------------------------------------------------------------
# Progress detail
# --------------------------------------------------------------------------

def test_change_details_for_an_update_shows_old_and_new():
    action = {"kind": "edit", "zrec": zrec(), "putcode": 1,
              "diffs": [("work-type", "book-chapter", "conference-paper"),
                        ("identifier", "—", "doi: 10.1/x (self)")]}
    assert so.change_details(action) == [
        "work-type: book-chapter → conference-paper",
        "identifier: — → doi: 10.1/x (self)",
    ]


def test_change_details_for_an_add_shows_what_is_sent():
    action = {"kind": "add", "zrec": zrec(
        orcid_type="software", container="Nature", doi="10.1/x",
        authors=["André Anjos", "Jane Roe", "John Doe", "Ann Poe"])}
    lines = so.change_details(action)
    assert "type: software" in lines
    assert "venue: Nature" in lines
    assert "doi: 10.1/x (self)" in lines
    assert "authors: André Anjos, Jane Roe, John Doe, Ann Poe (4)" in lines
    assert "language: en" in lines


def test_apply_prints_update_fields_as_it_writes(monkeypatch, capsys):
    _fake_session(monkeypatch)
    actions, _ = so.plan_actions({
        "missing": [], "orphan": [],
        "outdated": [(zrec(title="Old Work", year=2019, doi="10.1/x"),
                      owork(title="Old Work"),
                      [("identifier", "—", "doi: 10.1/x (self)")])],
    })
    so.apply_actions(actions, delay=0)
    out = capsys.readouterr().out
    assert "[1/1] update [2019] Old Work" in out
    assert "identifier: — → doi: 10.1/x (self)" in out


# --------------------------------------------------------------------------
# Sign-in detection
# --------------------------------------------------------------------------

class _FakeRequest:
    """A context.request stand-in returning a canned userStatus.json."""

    def __init__(self, logged_in, ok=True):
        self._logged_in = logged_in
        self._ok = ok
        self.calls = []

    def get(self, url, **_kw):
        self.calls.append(url)
        outer = self

        class R:
            ok = outer._ok
            url = "https://orcid.org/userStatus.json"
            headers = {"content-type": "application/json"}

            @staticmethod
            def json():
                return {"loggedIn": outer._logged_in}

        return R()


class _FakeCtx:
    def __init__(self, logged_in, ok=True):
        self.request = _FakeRequest(logged_in, ok)


def test_signed_in_asks_the_server_not_the_page_url():
    """The page URL is decided client-side by ORCID's Angular app and still reads
    /my-orcid for seconds after load, so it cannot be trusted. userStatus.json is
    the authority."""
    ctx = _FakeCtx(logged_in=True)
    assert so.signed_in(ctx) is True
    assert "userStatus.json" in ctx.request.calls[0]


def test_signed_in_false_when_logged_out():
    assert so.signed_in(_FakeCtx(logged_in=False)) is False


def test_signed_in_false_on_a_failed_probe():
    assert so.signed_in(_FakeCtx(logged_in=True, ok=False)) is False


# --------------------------------------------------------------------------
# Language detection
# --------------------------------------------------------------------------

# Real titles from data/outputs.json — the detector's job is these eleven and
# nothing else out of 145.
PT_TITLES = [
    "Sistema Online de Filtragem em um Ambiente com Alta Taxa de Eventos",
    "Os Filtros de Alto Nível do Experimento ATLAS",
    "Um Protótipo do Sistema de Validação do Nível 2 para as Condições do LHC",
    "Discriminação Neural de Elétrons no Segundo Nível de Trigger do ATLAS",
    "Sistema de classificação baseado em uma máquina com sistema distribuído",
    "Mapeamento em anéis para uma separação neuronal elétron-jato usando calorímetros",
]
EN_TITLES = [
    "Beyond the Last Frame: Temporal Modelling of Fluorescein Angiography",
    "No Free Lunch in Medical Image Segmentation",
    "The Little W-Net That Could: State-of-the-Art Retinal Vessel Segmentation",
    "Refining Tuberculosis Detection in CXR Imaging: Addressing Bias",
    "fairical",
    "WMCA (Wide Multi-Channel presentation Attack)",
    "Method and Device for Biometric Vascular Recognition and/or Identification",
    "A configuration system for the ATLAS trigger",
]
FR_TITLES = [
    "Détection automatique des lésions dans les images médicales",
    "Une méthode d'apprentissage profond pour l'analyse des données",
]


@pytest.mark.parametrize("title", PT_TITLES)
def test_detects_portuguese(title):
    assert zc.detect_language(title) == "pt"


@pytest.mark.parametrize("title", EN_TITLES)
def test_defaults_to_english(title):
    """English is the overwhelming majority, so a false positive is far worse
    than a miss — note 'No Free Lunch', whose 'no' is Portuguese too."""
    assert zc.detect_language(title) == "en"


@pytest.mark.parametrize("title", FR_TITLES)
def test_detects_french(title):
    assert zc.detect_language(title) == "fr"


def test_detect_language_handles_empty_title():
    assert zc.detect_language("") == "en"
    assert zc.detect_language(None) == "en"


# --------------------------------------------------------------------------
# Author and language syncing on updates
# --------------------------------------------------------------------------

def test_field_diffs_flags_a_reordered_author_list():
    """Order is part of the match, so a pure reordering must be caught."""
    z = zrec(authors=["André Anjos", "Jane Roe"])
    o = owork(authors=["Jane Roe", "André Anjos"], language="en")
    assert [f for f, _h, _w in zc.field_diffs(z, o)] == ["authors"]


def test_field_diffs_ignores_authors_when_not_enriched():
    """Without enrich_orcid_works the key is absent, and assuming ORCID has no
    authors would propose rewriting every author list on the record."""
    z = zrec(authors=["André Anjos"])
    o = owork()
    o.pop("authors", None)
    o.pop("language", None)
    assert zc.field_diffs(z, o) == []


def test_field_diffs_flags_missing_authors_and_language():
    z = zrec(authors=["André Anjos"], language="pt")
    o = owork(authors=[], language=None)
    assert {f for f, _h, _w in zc.field_diffs(z, o)} == {"authors", "language"}


def test_field_diffs_quiet_when_authors_and_language_already_match():
    z = zrec(authors=["André Anjos", "Jane Roe"], language="pt")
    o = owork(authors=["André Anjos", "Jane Roe"], language="pt")
    assert zc.field_diffs(z, o) == []


def test_patch_form_replaces_the_author_list_wholesale():
    """A merge could not express a reordering or a removal."""
    current = {"contributors": [{"creditName": so._text("Roe, Jane")}]}
    z = zrec(authors=["André Anjos", "Jane Roe"])
    patched = so.patch_form(current, z, [("authors", "x", "y")])
    assert [c["creditName"]["value"] for c in patched["contributors"]] == [
        "André Anjos", "Jane Roe"]


def test_patch_form_sets_the_language():
    patched = so.patch_form({}, zrec(language="pt"), [("language", "—", "pt")])
    assert patched["languageCode"]["value"] == "pt"


def test_new_form_carries_the_language():
    assert so.new_form(zrec(language="pt"))["languageCode"]["value"] == "pt"


def test_every_field_diffs_row_still_has_a_patch_rule():
    """Coverage guard, now including authors and language."""
    z = zrec(doi="10.1/x", pdf="https://z/p.pdf", orcid_type="software",
             container="Nature", year=2024, authors=["A B"], language="pt")
    o = owork(doi=None, url=None, type="journal-article", container=None,
              year=2023, authors=[], language=None)
    diffs = zc.field_diffs(z, o)
    assert len(diffs) == 7, "fixture should trigger every rule"
    so.patch_form({"workExternalIdentifiers": []}, z, diffs)  # must not raise


# --------------------------------------------------------------------------
# Bulk enrichment
# --------------------------------------------------------------------------

def test_ui_work_authors_reads_the_grouped_list_the_page_renders():
    """A work can serve contributors over the public API while its Contributors
    panel is blank — only the grouped list is rendered, so only it counts."""
    work = {
        "contributors": [{"creditName": {"value": "Ignored, Flat"}}],
        "contributorsGroupedByOrcid": [
            {"creditName": {"content": "Mautuit, Thibaud"}},
            {"creditName": {"content": "Anjos, André"}},
            {"creditName": None},
        ],
    }
    assert zc.ui_work_authors(work) == ["Mautuit, Thibaud", "Anjos, André"]


def test_ui_work_authors_empty_when_panel_would_be_blank():
    assert zc.ui_work_authors({"contributorsGroupedByOrcid": None}) == []
    assert zc.ui_work_authors({"contributors": [{"creditName": {"value": "X"}}]}) == []


def test_enrich_orcid_works_attaches_authors_and_language(monkeypatch):
    monkeypatch.setattr(zc, "fetch_orcid_ui_works", lambda **k: {
        1: {"putCode": {"value": "1"},
            "contributorsGroupedByOrcid": [{"creditName": {"content": "A B"}}]},
    })
    monkeypatch.setattr(zc, "fetch_orcid_work_details", lambda pcs, **k: {
        1: {"put-code": 1, "language-code": "pt"},
    })
    works = [owork(putcode=1), owork(putcode=2)]
    for w in works:
        w.pop("authors", None)
        w.pop("language", None)
    zc.enrich_orcid_works(works)
    assert works[0]["authors"] == ["A B"] and works[0]["language"] == "pt"
    assert "authors" not in works[1], "a work ORCID did not return stays unenriched"


# --------------------------------------------------------------------------
# Session persistence between runs
# --------------------------------------------------------------------------

class _CookieCtx:
    """A browser context stand-in that records add_cookies/cookies calls."""

    def __init__(self, jar=None):
        self._jar = list(jar or [])

    def add_cookies(self, cookies):
        self._jar.extend(cookies)

    def cookies(self, *_a):
        return self._jar


def test_cookies_round_trip_a_session_cookie(tmp_path):
    """Chrome drops cookies with expires=-1 when the profile closes, which is how
    ORCID's login is stored — so it has to be saved and restored explicitly."""
    jar = tmp_path / "jar.json"
    src = _CookieCtx([{"name": "XSRF-TOKEN", "value": "t", "domain": ".orcid.org",
                       "path": "/", "expires": -1}])
    so.save_cookies(src, jar)

    dest = _CookieCtx()
    assert so.load_cookies(dest, jar) is True
    assert [c["name"] for c in dest.cookies()] == ["XSRF-TOKEN"]


def test_save_cookies_is_owner_only(tmp_path):
    """The jar holds a live ORCID session — as good as the password."""
    jar = tmp_path / "jar.json"
    so.save_cookies(_CookieCtx([{"name": "a", "value": "b"}]), jar)
    assert jar.stat().st_mode & 0o077 == 0, "must not be group- or world-readable"


def test_load_cookies_absent_jar_is_not_an_error(tmp_path):
    assert so.load_cookies(_CookieCtx(), tmp_path / "nope.json") is False


def test_load_cookies_survives_a_corrupt_jar(tmp_path):
    jar = tmp_path / "jar.json"
    jar.write_text("{not json")
    assert so.load_cookies(_CookieCtx(), jar) is False


# --------------------------------------------------------------------------
# Convergence: an apply must leave nothing for the next run to redo
# --------------------------------------------------------------------------

def test_patch_form_clears_the_shadow_contributor_list():
    """ORCID's toWork() calls populateContributors() and THEN
    populateContributorsGroupedByOrcid(), and the second overwrites the first
    whenever contributorsGroupedByOrcid is non-empty. Replacing `contributors`
    while copying that field verbatim means the old names win and the sync never
    converges."""
    current = {
        "contributors": [{"creditName": so._text("Roe, Jane")}],
        "contributorsGroupedByOrcid": [{"creditName": {"content": "Roe, Jane"}}],
    }
    patched = so.patch_form(current, zrec(authors=["Jane Roe"]),
                            [("authors", "x", "y")])
    assert [c["creditName"]["value"] for c in patched["contributors"]] == ["Jane Roe"]
    assert [g["creditName"]["content"] for g in patched["contributorsGroupedByOrcid"]] \
        == ["Jane Roe"], "the grouped list is what the record page renders"


def test_two_zotero_records_cannot_claim_one_orcid_work():
    """Two real works collapse to one title slug ('The baseline dataflow system
    of the ATLAS trigger and DAQ' vs 'The base-line DataFlow system of the ATLAS
    Trigger and DAQ'). Letting both match one ORCID entry makes them propose
    conflicting edits to the same put-code, which oscillate forever."""
    a = zrec(title="The baseline dataflow system of the ATLAS trigger and DAQ",
             year=2003, orcid_type="conference-paper")
    b = zrec(title="The base-line DataFlow system of the ATLAS Trigger and DAQ",
             year=2004, orcid_type="journal-article")
    assert a["slug"] == b["slug"], "fixture must reproduce the slug collision"

    o = owork(title=a["title"], year=2004, type="conference-paper", putcode=51366694)
    diff = zc.diff_against_orcid([a, b], [o])

    claimed = [ow["putcode"] for _z, ow, _d in diff["outdated"]]
    assert len(claimed) == len(set(claimed)), "one ORCID work, at most one editor"
    assert len(diff["missing"]) == 1, "the unmatched record is missing, not an edit"


def test_doi_match_beats_a_title_collision():
    """The record holding the DOI must win the work, whatever the iteration
    order, so a title twin cannot steal it."""
    twin = zrec(title="Same Title", doi=None)
    real = zrec(title="Same Title", doi="10.1/x")
    o = owork(title="Same Title", doi="10.1/x", putcode=7)

    for order in ([twin, real], [real, twin]):
        diff = zc.diff_against_orcid(order, [o])
        matched = [z for z, _ow, _d in diff["outdated"]]
        assert diff["missing"] == [twin] or matched == [] or matched[0] is real
        assert all(z is not twin for z, _ow, _d in diff["outdated"]), \
            "the DOI-less twin must not claim the DOI's work"


def _orcid_view(form):
    """What ORCID stores for a WorkForm, back in parse_orcid_works shape.

    Models the one server behaviour that broke convergence: toWork() applies
    `contributors` first and `contributorsGroupedByOrcid` second, so a non-empty
    grouped list wins.
    """
    authors = [g["creditName"]["content"]
               for g in (form.get("contributorsGroupedByOrcid") or [])]
    eids = form.get("workExternalIdentifiers") or []
    doi = next((e["externalIdentifierId"]["value"] for e in eids
                if e["externalIdentifierType"]["value"] == "doi"), None)
    pub = form.get("publicationDate") or {}
    year, month, day = pub.get("year"), pub.get("month"), pub.get("day")
    return {
        "doi": doi,
        "identifiers": [
            {"type": (e["externalIdentifierType"] or {}).get("value", ""),
             "value": (e["externalIdentifierId"] or {}).get("value", ""),
             "relationship": (e.get("relationship") or {}).get("value", "self")}
            for e in (form.get("workExternalIdentifiers") or [])
        ],
        "title": (form.get("title") or {}).get("value"),
        "container": (form.get("journalTitle") or {}).get("value"),
        "year": int(year) if year else None,
        "month": int(month) if month else 0,
        "day": int(day) if day else 0,
        "type": (form.get("workType") or {}).get("value"),
        "url": (form.get("url") or {}).get("value"),
        "putcode": 1,
        "ours": True,
        "authors": authors,
        "language": (form.get("languageCode") or {}).get("value"),
    }


def test_an_update_converges_in_one_pass():
    """The invariant behind 'running --apply twice must be a no-op': after
    writing, re-diffing the stored result must find nothing left to do."""
    z = zrec(title="A Paper", doi="10.1/x", container="Nature", year=2024,
             orcid_type="journal-article", pdf="https://z/p.pdf",
             authors=["André Anjos", "Jane Roe"], language="pt")
    stale = {
        "putCode": so._text("1"),
        "title": so._text("A Paper"),
        "journalTitle": so._text(None),
        "workType": so._text("conference-paper"),
        "workExternalIdentifiers": [],
        "url": so._text(None),
        "languageCode": so._text(None),
        "publicationDate": {"year": "2019", "month": None, "day": None},
        "contributors": [{"creditName": so._text("Roe, Jane")}],
        "contributorsGroupedByOrcid": [{"creditName": {"content": "Roe, Jane"}}],
    }

    o = _orcid_view(stale)
    diffs = zc.field_diffs(z, o)
    assert diffs, "fixture must start out of date"

    saved = so.patch_form(stale, z, diffs)
    assert zc.field_diffs(z, _orcid_view(saved)) == [], (
        "a second --apply would redo these; the update did not converge"
    )


# --------------------------------------------------------------------------
# Publication date: month and day
# --------------------------------------------------------------------------

def test_parsed_ymd_reads_each_granularity():
    """Zotero's parsedDate is year, year-month or a full date — 125/8/12 of the
    145 works here, respectively."""
    assert zc.parsed_ymd({}, {"parsedDate": "2024"}) == (2024, 0, 0)
    assert zc.parsed_ymd({}, {"parsedDate": "2024-09"}) == (2024, 9, 0)
    assert zc.parsed_ymd({}, {"parsedDate": "2024-09-13"}) == (2024, 9, 13)


def test_parsed_date_still_returns_year_and_month():
    """build_site_entry sorts on this; it must keep its two-value contract."""
    assert zc.parsed_date({}, {"parsedDate": "2024-09-13"}) == (2024, 9)


def test_zotero_records_carry_month_and_day():
    item = {"data": {"itemType": "journalArticle", "title": "T", "creators": []},
            "key": "K", "meta": {"parsedDate": "2024-09-13"}}
    import unittest.mock
    with unittest.mock.patch.object(zc, "fetch_public_items", return_value=[item]):
        rec = zc.zotero_records("5992358")[0]
    assert (rec["year"], rec["month"], rec["day"]) == (2024, 9, 13)


def test_date_mismatch_ignores_what_zotero_does_not_know():
    """The data-loss guard. Zotero knows only 2024; ORCID holds a full Crossref
    date. That is not drift, and forcing it would strip month and day from most
    of the record."""
    z = zrec(year=2024, month=0, day=0)
    o = owork(year=2024, month=9, day=13)
    assert zc.date_mismatch(z, o) is False
    assert zc.field_diffs(z, o) == []


def test_date_mismatch_catches_each_component():
    assert zc.date_mismatch(zrec(year=2023), owork(year=2024)) is True
    assert zc.date_mismatch(zrec(year=2024, month=9), owork(year=2024)) is True
    assert zc.date_mismatch(zrec(year=2024, month=9, day=13),
                            owork(year=2024, month=9, day=1)) is True


def test_set_date_preserves_components_zotero_lacks():
    """A year-only Zotero record must not blank a month ORCID already has."""
    form = {"publicationDate": {"year": "2019", "month": "09", "day": "13"}}
    so.set_date(form, zrec(year=2024, month=0, day=0))
    assert form["publicationDate"] == {"year": "2024", "month": "09", "day": "13"}


def test_set_date_writes_zero_padded_month_and_day():
    form = {}
    so.set_date(form, zrec(year=2024, month=9, day=3))
    assert form["publicationDate"] == {"year": "2024", "month": "09", "day": "03"}


def test_new_form_carries_the_full_date():
    form = so.new_form(zrec(year=2026, month=9, day=13))
    assert form["publicationDate"] == {"year": "2026", "month": "09", "day": "13"}


def test_format_date_trims_at_the_first_unknown():
    assert zc.format_date(2024, 9, 13) == "2024-09-13"
    assert zc.format_date(2024, 9, 0) == "2024-09"
    assert zc.format_date(2024, 0, 0) == "2024"
    assert zc.format_date(None, 0, 0) == "—"


def test_a_date_update_converges():
    z = zrec(year=2024, month=9, day=13)
    stale = {"publicationDate": {"year": "2019", "month": None, "day": None}}
    diffs = [("date", "2019", "2024-09-13")]
    saved = so.patch_form(stale, z, diffs)
    pub = saved["publicationDate"]
    o = owork(year=int(pub["year"]), month=int(pub["month"]), day=int(pub["day"]))
    assert zc.date_mismatch(z, o) is False


def test_language_is_read_from_the_api_not_the_ui_payload(monkeypatch):
    """worksExtendedPage.json carries a languageCode field but leaves it null,
    even on works whose public record says 'en'. Reading language from there
    makes every work look untranslated forever, so the two fields come from two
    sources: contributors from the UI (the only view of the rendered panel),
    language from the documented API (the only one that populates it)."""
    monkeypatch.setattr(zc, "fetch_orcid_ui_works", lambda **k: {
        1: {"putCode": {"value": "1"}, "languageCode": None,
            "contributorsGroupedByOrcid": [{"creditName": {"content": "A B"}}]},
    })
    monkeypatch.setattr(zc, "fetch_orcid_work_details", lambda pcs, **k: {
        1: {"put-code": 1, "language-code": "en"},
    })
    works = [owork(putcode=1)]
    works[0].pop("authors", None)
    works[0].pop("language", None)
    zc.enrich_orcid_works(works)
    assert works[0]["authors"] == ["A B"]
    assert works[0]["language"] == "en", "language must not come from the UI payload"


def test_duplicate_orcid_titles_are_all_matchable():
    """A slug index keyed one-work-per-slug hides every duplicate but one, so a
    second Zotero record finds nothing free, is called 'missing', and is added
    again on every run. That is how seven copies of the ATLAS DataFlow work
    reached the live record."""
    a = zrec(title="The baseline dataflow system of the ATLAS trigger and DAQ",
             year=2003, orcid_type="conference-paper")
    b = zrec(title="The base-line DataFlow system of the ATLAS Trigger and DAQ",
             year=2004, orcid_type="journal-article")
    assert a["slug"] == b["slug"]

    orcid = [
        owork(title=a["title"], year=2003, type="conference-paper", putcode=1),
        owork(title=b["title"], year=2004, type="journal-article", putcode=2),
    ]
    diff = zc.diff_against_orcid([a, b], orcid)

    assert diff["missing"] == [], "both records already exist; nothing to add"
    assert diff["orphan"] == [], "both ORCID works were claimed"


def test_duplicate_orcid_dois_do_not_hide_each_other():
    z1 = zrec(title="One", doi="10.1/x")
    z2 = zrec(title="Two", doi="10.1/x")
    orcid = [owork(title="One", doi="10.1/x", putcode=1),
             owork(title="Two", doi="10.1/x", putcode=2)]
    diff = zc.diff_against_orcid([z1, z2], orcid)
    assert diff["missing"] == [] and diff["orphan"] == []


# --------------------------------------------------------------------------
# Linking the record holder to their own works
# --------------------------------------------------------------------------

def test_is_self_folds_every_zotero_spelling():
    for spelling in ("André Anjos", "Andre Anjos", "A. Anjos", "A.R. Anjos"):
        assert so.is_self(spelling), spelling
    for other in ("Jane Roe", "Sébastien Marcel", "The ATLAS Collaboration"):
        assert not so.is_self(other), other


def test_self_contributor_is_linked_to_the_orcid_profile():
    """ORCID's 'Add yourself as a contributor' attaches the iD, which links the
    work to the profile; a bare credit name does not."""
    grouped = so.contributor_grouped("André Anjos")
    assert grouped["contributorOrcid"]["path"] == zc.ORCID_ID
    assert grouped["contributorOrcid"]["uri"].endswith(zc.ORCID_ID)
    flat = so.contributor("A. Anjos")
    assert flat["orcid"]["value"] == zc.ORCID_ID


def test_co_authors_are_not_linked_to_any_profile():
    """Zotero holds no ORCID iDs for co-authors, and guessing one would attribute
    a work to the wrong researcher."""
    grouped = so.contributor_grouped("Jane Roe")
    assert grouped["contributorOrcid"] == {"uri": None, "path": None, "host": None}
    assert "orcid" not in so.contributor("Jane Roe")


def test_new_form_links_only_the_record_holder():
    form = so.new_form(zrec(authors=["Jane Roe", "André Anjos", "John Doe"]))
    linked = [(g["creditName"]["content"], (g["contributorOrcid"] or {}).get("path"))
              for g in form["contributorsGroupedByOrcid"]]
    assert linked == [("Jane Roe", None), ("André Anjos", zc.ORCID_ID), ("John Doe", None)]


def test_profile_link_is_flagged_even_when_names_match():
    """Otherwise an already-synced work is never revisited and the ORCID link
    only ever reaches brand-new entries."""
    z = zrec(authors=["Jane Roe", "André Anjos"])
    o = owork(authors=["Jane Roe", "André Anjos"], language="en", self_linked=False)
    assert [f for f, _h, _w in zc.field_diffs(z, o)] == ["profile link"]


def test_profile_link_quiet_once_linked():
    z = zrec(authors=["André Anjos"])
    o = owork(authors=["André Anjos"], language="en", self_linked=True)
    assert zc.field_diffs(z, o) == []


def test_profile_link_not_flagged_on_works_without_the_record_holder():
    z = zrec(authors=["Jane Roe"])
    o = owork(authors=["Jane Roe"], language="en", self_linked=False)
    assert zc.field_diffs(z, o) == []


def test_ui_self_linked_reads_the_contributor_orcid():
    linked = {"contributorsGroupedByOrcid": [
        {"creditName": {"content": "André Anjos"},
         "contributorOrcid": {"path": zc.ORCID_ID, "uri": None, "host": None}}]}
    loose = {"contributorsGroupedByOrcid": [
        {"creditName": {"content": "André Anjos"},
         "contributorOrcid": {"path": None, "uri": None, "host": None}}]}
    assert zc.ui_self_linked(linked) is True
    assert zc.ui_self_linked(loose) is False


def test_patching_a_profile_link_actually_links():
    patched = so.patch_form({}, zrec(authors=["Jane Roe", "André Anjos"]),
                            [("profile link", "—", "linked to ORCID iD")])
    paths = [(g["contributorOrcid"] or {}).get("path")
             for g in patched["contributorsGroupedByOrcid"]]
    assert paths == [None, zc.ORCID_ID]


def test_same_slug_works_pair_up_by_content_not_feed_order():
    """The ATLAS pair. Both Zotero records share a slug, and so do both ORCID
    works; taking candidates in feed order cross-matched them, so each proposed
    turning the other's entry into its own type and date. Applying that swapped
    the two, which reordered ORCID's date-sorted feed, which flipped the pairing
    back — an oscillation that never converges."""
    z2003 = zrec(title="The baseline dataflow system of the ATLAS trigger and DAQ",
                 year=2003, orcid_type="conference-paper")
    z2004 = zrec(title="The base-line DataFlow system of the ATLAS Trigger and DAQ",
                 year=2004, orcid_type="journal-article")
    o2003 = owork(title=z2003["title"], year=2003, type="conference-paper",
                  putcode=51366694)
    o2004 = owork(title=z2004["title"], year=2004, type="journal-article",
                  putcode=223540895)

    # Whatever order ORCID happens to serve them in, the pairing must hold.
    for orcid in ([o2003, o2004], [o2004, o2003]):
        diff = zc.diff_against_orcid([z2003, z2004], orcid)
        assert diff["outdated"] == [], f"cross-matched with order {[w['putcode'] for w in orcid]}"
        assert diff["missing"] == [] and diff["orphan"] == []


def test_match_prefers_the_exact_title_among_slug_twins():
    exact = owork(title="The base-line DataFlow system", putcode=1)
    twin = owork(title="The baseline dataflow system", putcode=2)
    z = zrec(title="The baseline dataflow system")
    by_title = {z["slug"]: [exact, twin]}
    assert zc.match(z, {}, by_title)["putcode"] == 2


def test_match_falls_back_to_year_then_type_among_twins():
    a = owork(title="X", year=2003, type="conference-paper", putcode=1)
    b = owork(title="X", year=2004, type="journal-article", putcode=2)
    z = zrec(title="Y", year=2004, orcid_type="journal-article")
    by_title = {zc.slug_title("X"): [a, b]}
    z["slug"] = zc.slug_title("X")
    assert zc.match(z, {}, by_title)["putcode"] == 2


# --------------------------------------------------------------------------
# Work identifiers
# --------------------------------------------------------------------------

def test_issn_and_isbn_are_part_of_not_self():
    """Load-bearing. ORCID groups works by their `self` identifiers, so a
    journal's ISSN marked `self` collapses every article in that journal into
    one group and later ones are refused as duplicates. An ISSN names the
    journal, an ISBN the book — both part-of."""
    ids = zc.work_identifiers({"DOI": "10.1/x", "ISSN": "1748-0221",
                               "ISBN": "978-3-031-95838-0"})
    by_type = {i["type"]: i["relationship"] for i in ids}
    assert by_type == {"doi": "self", "issn": "part-of", "isbn": "part-of"}


def test_identifiers_from_archive_id_prefixes():
    assert zc.work_identifiers({"archiveID": "SSRN:4960069"}) == [
        {"type": "ssrn", "value": "4960069", "relationship": "self"}]
    assert zc.work_identifiers({"archiveID": "arXiv:2407.14064"}) == [
        {"type": "arxiv", "value": "2407.14064", "relationship": "self"}]


def test_identifiers_from_labelled_extra_lines():
    extra = "arXiv: 2407.14064\nPMID: 12345678\nHomepage: https://example.org"
    got = {i["type"]: i["value"] for i in zc.work_identifiers({"extra": extra})}
    assert got == {"arxiv": "2407.14064", "pmid": "12345678"}


def test_unknown_prefixes_are_skipped_not_guessed():
    assert zc.work_identifiers({"archiveID": "WHATEVER:123"}) == []


def test_multiple_issns_in_one_field():
    got = zc.work_identifiers({"ISSN": "1748-0221, 1234-5678"})
    assert [i["value"] for i in got] == ["1748-0221", "1234-5678"]
    assert all(i["relationship"] == "part-of" for i in got)


def test_normalize_identifier_folds_arxiv_spellings():
    """This record already holds 2009.01907, abs/2408.16130 and arXiv:1709.00962
    as arXiv ids; without folding, syncing would add a second spelling."""
    forms = ["2407.14064", "arXiv:2407.14064", "abs/2407.14064", "ARXIV: 2407.14064"]
    assert len({zc.normalize_identifier("arxiv", f) for f in forms}) == 1
    assert zc.normalize_identifier("issn", "1748-0221") == \
        zc.normalize_identifier("issn", "17480221")


def test_missing_identifiers_ignores_ones_orcid_already_has():
    z = zrec(doi="10.1/X")
    o = owork(identifiers=[{"type": "doi", "value": "https://doi.org/10.1/x",
                            "relationship": "self"}])
    assert zc.missing_identifiers(z, o) == []


def test_missing_identifiers_keeps_orcid_extras():
    """ORCID's own ids are often richer — this record carries `uri` ids for
    OpenReview pages Zotero never had. One-directional, like every rule here."""
    z = zrec(doi=None)
    z["identifiers"] = []
    o = owork(identifiers=[{"type": "uri", "value": "https://openreview.net/x",
                            "relationship": "self"}])
    assert zc.missing_identifiers(z, o) == []
    assert zc.field_diffs(z, o) == []


def test_new_form_carries_every_identifier_with_its_relationship():
    z = zrec(doi="10.1/x")
    z["identifiers"] = [
        {"type": "doi", "value": "10.1/x", "relationship": "self"},
        {"type": "issn", "value": "1748-0221", "relationship": "part-of"},
        {"type": "ssrn", "value": "4960069", "relationship": "self"},
    ]
    eids = so.new_form(z)["workExternalIdentifiers"]
    got = [(e["externalIdentifierType"]["value"], e["externalIdentifierId"]["value"],
            e["relationship"]["value"]) for e in eids]
    assert got == [("doi", "10.1/x", "self"), ("issn", "1748-0221", "part-of"),
                   ("ssrn", "4960069", "self")]


def test_add_external_id_will_not_duplicate_a_differently_spelled_arxiv():
    form = {"workExternalIdentifiers": []}
    so.add_external_id(form, "arxiv", "arXiv:2407.14064")
    so.add_external_id(form, "arxiv", "2407.14064")
    assert len(form["workExternalIdentifiers"]) == 1


def test_identifier_update_converges():
    z = zrec(doi="10.1/x")
    z["identifiers"] = [
        {"type": "doi", "value": "10.1/x", "relationship": "self"},
        {"type": "issn", "value": "1748-0221", "relationship": "part-of"},
    ]
    form = {"workExternalIdentifiers": []}
    patched = so.patch_form(form, z, [("identifier", "—", "doi")])
    o = owork(identifiers=so._current_ids(patched))
    assert zc.missing_identifiers(z, o) == []


def test_patent_numbers_become_pat_identifiers():
    """ORCID's controlled vocabulary calls it `pat`. Self, not part-of: it names
    the patent itself, unlike an ISSN naming a journal."""
    assert zc.work_identifiers({"patentNumber": "US9973503B2"}) == [
        {"type": "pat", "value": "US9973503B2", "relationship": "self"}]
    assert zc.work_identifiers({"patentNumber": "WO/2019/150254"}) == [
        {"type": "pat", "value": "WO/2019/150254", "relationship": "self"}]


def test_identifier_values_drop_a_repeated_label():
    """One Zotero item stores 'ISBN 978-3-319-92627-8' in the ISBN field;
    written verbatim that is a malformed identifier on ORCID."""
    assert zc.work_identifiers({"ISBN": "ISBN 978-3-319-92627-8"}) == [
        {"type": "isbn", "value": "978-3-319-92627-8", "relationship": "part-of"}]
    assert zc.work_identifiers({"ISSN": "ISSN: 1748-0221"}) == [
        {"type": "issn", "value": "1748-0221", "relationship": "part-of"}]
    assert zc.work_identifiers({"DOI": "10.1/x"})[0]["value"] == "10.1/x"


# --------------------------------------------------------------------------
# BibTeX citation
# --------------------------------------------------------------------------

ENTRY = """@inproceedings{key_2024,
\taddress = {Milan, Italy},
\ttitle = {A {Title}, with a comma},
\tabstract = {Long prose with {braces} and, commas, spanning
\tseveral lines.},
\tnote = {Homepage: https://example.org
\tGSCC: 0000002 2026-06-16T06:01:05.431Z 0.01},
\turldate = {2024-11-15},
\tdoi = {10.1/x},
\tauthor = {Anjos, André and Roe, Jane},
\tmonth = sep,
\tyear = {2024},
}"""


def test_clean_bibtex_drops_abstract_and_local_fields():
    """`note` is Zotero's Extra block, which on this library holds purely local
    bookkeeping (Homepage:, Software:, GSCC:)."""
    out = zc.clean_bibtex(ENTRY)
    for gone in ("abstract", "note", "urldate", "Homepage", "GSCC"):
        assert gone not in out, gone
    for kept in ("address", "title", "doi", "author", "month", "year"):
        assert kept in out, kept


def test_clean_bibtex_survives_commas_and_braces_in_values():
    """Brace counting, not line splitting: abstracts contain both."""
    out = zc.clean_bibtex(ENTRY)
    assert "{A {Title}, with a comma}" in out
    assert out.startswith("@inproceedings{key_2024,")
    assert out.rstrip().endswith("}")
    assert "month = sep," in out, "unbraced values must survive"


def test_clean_bibtex_keeps_copyright_for_licences():
    entry = "@misc{k,\n\ttitle = {T},\n\tcopyright = {GPL-3.0},\n}"
    assert "GPL-3.0" in zc.clean_bibtex(entry)


def test_clean_bibtex_passes_through_unparseable_input():
    assert zc.clean_bibtex("not bibtex at all") == "not bibtex at all"


def test_normalize_bibtex_ignores_reflowing():
    """Two spellings of one entry must compare equal, or ORCID's re-flow would
    read as drift and every work would be rewritten on every run."""
    tabbed = "@misc{k,\n\ttitle = {T},\n}"
    spaced = "@misc{k,   title = {T},   }"
    assert zc.normalize_bibtex(tabbed) == zc.normalize_bibtex(spaced)
    assert zc.normalize_bibtex("a  b\n\tc") == "a b c"


def test_attach_bibtex_pairs_on_the_citation_key():
    recs = [zrec(title="One"), zrec(title="Two")]
    recs[0]["key"], recs[1]["key"] = "a_one_2024", "b_two_2024"
    zc.attach_bibtex(recs, {"a_one_2024": "@misc{a_one_2024,\n\ttitle = {One},\n}"})
    assert recs[0]["bibtex"].startswith("@misc{a_one_2024,")
    assert recs[1]["bibtex"] is None


def test_field_diffs_flags_a_missing_or_stale_citation():
    z = zrec()
    z["bibtex"] = "@misc{k,\n\ttitle = {T},\n}"
    absent = owork(citation=None, citation_type=None, language="en")
    assert [f for f, _h, _w in zc.field_diffs(z, absent)] == ["citation"]

    stale = owork(citation="@misc{k,\n\ttitle = {Different},\n}",
                  citation_type="bibtex", language="en")
    assert [f for f, _h, _w in zc.field_diffs(z, stale)] == ["citation"]


def test_field_diffs_quiet_when_the_citation_only_differs_in_whitespace():
    """ORCID re-flows what it stores; a re-flow is not drift, and treating it as
    drift would rewrite every work on every run."""
    z = zrec()
    z["bibtex"] = "@misc{k,\n\ttitle = {T},\n}"
    o = owork(citation="@misc{k,   title = {T}, }", citation_type="bibtex",
              language="en")
    assert zc.field_diffs(z, o) == []


def test_field_diffs_flags_a_non_bibtex_citation_type():
    z = zrec()
    z["bibtex"] = "@misc{k,\n\ttitle = {T},\n}"
    o = owork(citation="Anjos, A. (2024).", citation_type="formatted-apa",
              language="en")
    assert [f for f, _h, _w in zc.field_diffs(z, o)] == ["citation"]


def test_field_diffs_ignores_citation_when_not_enriched():
    z = zrec()
    z["bibtex"] = "@misc{k,\n\ttitle = {T},\n}"
    o = owork(language="en")
    o.pop("citation", None)
    assert zc.field_diffs(z, o) == []


def test_set_citation_uses_orcids_bibtex_type():
    form = {}
    so.set_citation(form, "@misc{k,\n\ttitle = {T},\n}")
    assert form["citation"]["citationType"]["value"] == "bibtex"
    assert form["citation"]["citation"]["value"].startswith("@misc{k,")


def test_set_citation_leaves_orcid_alone_when_zotero_has_none():
    form = {"citation": {"citation": so._text("keep me"),
                         "citationType": so._text("bibtex")}}
    so.set_citation(form, None)
    assert form["citation"]["citation"]["value"] == "keep me"


def test_new_form_carries_the_citation():
    z = zrec()
    z["bibtex"] = "@misc{k,\n\ttitle = {T},\n}"
    assert so.new_form(z)["citation"]["citationType"]["value"] == "bibtex"


def test_a_citation_update_converges():
    z = zrec()
    z["bibtex"] = "@misc{k,\n\ttitle = {T},\n}"
    patched = so.patch_form({}, z, [("citation", "—", "bibtex")])
    o = owork(citation=patched["citation"]["citation"]["value"],
              citation_type=patched["citation"]["citationType"]["value"],
              language="en")
    assert zc.field_diffs(z, o) == []


def test_attach_bibtex_skips_an_oversized_citation_with_a_reason():
    """Skipping must leave bibtex None as well as recording why: with no
    citation the diff proposes nothing, so the work converges instead of
    failing on every run."""
    rec = zrec()
    rec["key"] = "big_2008"
    huge = "@misc{big_2008,\n\tauthor = {" + " and ".join(
        f"Author{i}, A" for i in range(3000)) + "},\n}"
    zc.attach_bibtex([rec], {"big_2008": huge})
    assert rec["bibtex"] is None
    assert "over the" in rec["bibtex_skipped"]
    assert "characters" in rec["bibtex_skipped"]


def test_a_skipped_citation_proposes_nothing_and_converges():
    rec = zrec()
    rec["key"] = "big_2008"
    zc.attach_bibtex([rec], {"big_2008": "@misc{big_2008,\n\ttitle = {" + "x" * 20000 + "},\n}"})
    o = owork(citation=None, citation_type=None, language="en")
    assert zc.field_diffs(rec, o) == [], "a skipped citation must not be flagged"


def test_attach_bibtex_reports_a_missing_entry():
    rec = zrec()
    rec["key"] = "absent_2024"
    zc.attach_bibtex([rec], {})
    assert rec["bibtex"] is None
    assert "no BibTeX entry" in rec["bibtex_skipped"]


def test_attach_bibtex_clears_the_reason_when_it_succeeds():
    rec = zrec()
    rec["key"] = "ok_2024"
    zc.attach_bibtex([rec], {"ok_2024": "@misc{ok_2024,\n\ttitle = {T},\n}"})
    assert rec["bibtex"].startswith("@misc{ok_2024,")
    assert rec["bibtex_skipped"] is None


# --------------------------------------------------------------------------
# Contributor roles the save endpoint cannot accept
# --------------------------------------------------------------------------

def test_credit_roles_are_normalised_before_posting():
    """`POST /works/work.json` answers HTTP 500 when a work's grouped
    contributors carry a CRediT role such as "writing - original draft" — those
    belong to a different vocabulary from the eleven legacy roles this endpoint
    takes. The names are kept; only the role is brought back into range."""
    form = {"contributorsGroupedByOrcid": [
        {"creditName": {"content": "Jung Park"},
         "contributorOrcid": {"uri": None, "path": None, "host": None},
         "rolesAndSequences": [{"contributorSequence": None,
                                "contributorRole": "writing - original draft"}]},
        {"creditName": {"content": "André Anjos"},
         "contributorOrcid": {"uri": None, "path": zc.ORCID_ID, "host": None},
         "rolesAndSequences": [{"contributorSequence": None,
                                "contributorRole": "writing - original draft"}]},
    ]}
    assert so.sanitize_contributors(form) is True

    grouped = form["contributorsGroupedByOrcid"]
    assert [g["creditName"]["content"] for g in grouped] == ["Jung Park", "André Anjos"]
    assert all(r["contributorRole"] == "author"
               for g in grouped for r in g["rolesAndSequences"])
    assert grouped[1]["contributorOrcid"]["path"] == zc.ORCID_ID, \
        "the profile link must survive the rewrite"


def test_legacy_roles_are_left_alone():
    """editor, principal-investigator and the rest post fine; rewriting them
    would destroy real information."""
    for role in ("author", "editor", "principal-investigator", "co-inventor"):
        form = {"contributorsGroupedByOrcid": [
            {"creditName": {"content": "Jane Roe"},
             "contributorOrcid": {"uri": None, "path": None, "host": None},
             "rolesAndSequences": [{"contributorSequence": None,
                                    "contributorRole": role}]}]}
        assert so.sanitize_contributors(form) is False, role
        assert form["contributorsGroupedByOrcid"][0]["rolesAndSequences"][0][
            "contributorRole"] == role


def test_sanitize_handles_an_absent_or_empty_grouped_list():
    assert so.sanitize_contributors({}) is False
    assert so.sanitize_contributors({"contributorsGroupedByOrcid": None}) is False


def test_patch_form_sanitizes_even_when_authors_are_not_in_the_diff():
    """The failing work only needed a citation; the unpostable role came along
    in the fetched form, so every patch has to clear it."""
    form = {"contributorsGroupedByOrcid": [
        {"creditName": {"content": "Jung Park"},
         "contributorOrcid": {"uri": None, "path": None, "host": None},
         "rolesAndSequences": [{"contributorRole": "conceptualization"}]}]}
    z = zrec()
    z["bibtex"] = "@misc{k,\n\ttitle = {T},\n}"
    patched = so.patch_form(form, z, [("citation", "—", "bibtex")])
    roles = [r["contributorRole"]
             for g in patched["contributorsGroupedByOrcid"]
             for r in g["rolesAndSequences"]]
    assert roles == ["author"]


# --------------------------------------------------------------------------
# Headless operation
# --------------------------------------------------------------------------

def _stub_playwright(monkeypatch):
    """Keep session() from starting a real Playwright driver process."""
    import playwright.sync_api

    @contextlib.contextmanager
    def fake_sync_playwright():
        yield object()

    monkeypatch.setattr(playwright.sync_api, "sync_playwright", fake_sync_playwright)


def test_no_browser_unless_there_is_something_to_apply(monkeypatch):
    """A browser is a side effect worth avoiding: --apply with an empty plan, and
    every dry-run, must finish without one."""
    def boom(*_a, **_k):
        pytest.fail("a browser must not be opened here")

    monkeypatch.setattr(so, "session", boom)
    monkeypatch.setattr(zc, "zotero_records", lambda _u: [zrec(doi="10.1/x")])
    monkeypatch.setattr(zc, "fetch_public_bibtex", lambda _u: {})
    monkeypatch.setattr(zc, "fetch_orcid_works", lambda: {})
    monkeypatch.setattr(zc, "enrich_orcid_works", lambda w: w)
    monkeypatch.setattr(zc, "parse_orcid_works", lambda _p: [
        owork(doi="10.1/x", identifiers=[{"type": "doi", "value": "10.1/x",
                                          "relationship": "self"}])])

    monkeypatch.setattr(sys, "argv", ["sync_orcid.py", "--apply"])
    assert so.main() == 0, "nothing to do, so no browser"

    monkeypatch.setattr(sys, "argv", ["sync_orcid.py"])
    assert so.main() == 0, "dry-run never needs a browser"


def test_headless_fails_fast_when_the_session_has_lapsed(monkeypatch):
    """A signed-out headless run can never succeed — nobody can type a password
    into it — so it must say so at once rather than polling out the five-minute
    sign-in timeout."""
    launched = []

    class _Ctx:
        def __init__(self):
            self.request = _FakeRequest(logged_in=False)

        def add_cookies(self, _c):
            pass

        def cookies(self, *_a):
            return []

        def close(self):
            pass

    def fake_launch(_pw, _dir, headless):
        launched.append(headless)
        return _Ctx()

    _stub_playwright(monkeypatch)
    monkeypatch.setattr(so, "_launch", fake_launch)
    monkeypatch.setattr(so, "load_cookies", lambda *a, **k: True)
    monkeypatch.setattr(so, "_ensure_signed_in", lambda *a, **k:
                        pytest.fail("must not wait for a sign-in when headless"))

    with pytest.raises(RuntimeError, match="lapsed"):
        with so.session(pathlib.Path("/tmp/nope"), headless=True):
            pass
    assert launched == [True], "it must not open a visible window"


def test_auto_mode_starts_headless(monkeypatch):
    """The default opens no window while the saved session still works."""
    launched = []

    class _Ctx:
        def __init__(self):
            self.request = _FakeRequest(logged_in=True)

        def add_cookies(self, _c):
            pass

        def cookies(self, *_a):
            return [{"name": so.XSRF_COOKIE, "value": "t"}]

        def close(self):
            pass

    _stub_playwright(monkeypatch)
    monkeypatch.setattr(so, "_launch",
                        lambda _pw, _d, headless: launched.append(headless) or _Ctx())
    monkeypatch.setattr(so, "load_cookies", lambda *a, **k: True)
    monkeypatch.setattr(so, "save_cookies", lambda *a, **k: None)
    monkeypatch.setattr(so, "_csrf", lambda _c: "tok")

    with so.session(pathlib.Path("/tmp/nope")) as (_ctx, csrf):
        assert csrf == "tok"
    assert launched == [True]
