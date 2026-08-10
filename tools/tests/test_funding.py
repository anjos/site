"""Offline unit tests for the ORCID-sourced funding tooling (no network).

Fixtures reproduce the two ORCID shapes the tool consumes: the `/fundings`
summary payload, where one grant may be asserted by several sources, and the
`/funding/{put-code}` detail payload, which is the only place the amount, the
abstract, and the funding instrument live.

SPDX-FileCopyrightText: Copyright © 2026 Idiap Research Institute <contact@idiap.ch>

SPDX-License-Identifier: BSD-3-Clause
"""

import importlib.util
import json
import pathlib
import sys

TOOLS = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(TOOLS))

import zotero_common as zc  # noqa: E402

# The script has a dash in its name, so it cannot be imported by name.
_spec = importlib.util.spec_from_file_location("uf", TOOLS / "update-funding.py")
uf = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(uf)


# --------------------------------------------------------------------------- #
# Fixtures — trimmed to the fields the tool reads.
# --------------------------------------------------------------------------- #
def _date(year, month=None):
    return {"year": {"value": year}, "month": {"value": month} if month else None,
            "day": None}


def _summary(put_code, self_asserted=True):
    """One `funding-summary`, asserted either by André or by a third party."""
    source = ({"source-orcid": {"path": zc.ORCID_ID}} if self_asserted
              else {"source-orcid": None,
                    "source-client-id": {"path": "0000-0003-2174-0924"}})
    return {"put-code": put_code, "source": source}


def _detail(put_code, title, start, end, *, amount="200000.0", url=None,
            grant_number=None, instrument=None, description="Why it matters."):
    """One `/funding/{put-code}` payload."""
    eid = []
    if grant_number:
        eid = [{"external-id-type": "grant_number",
                "external-id-value": grant_number,
                "external-id-url": {"value": f"https://data.snf.ch/grants/grant/{grant_number}"},
                "external-id-relationship": "self"}]
    return {
        "put-code": put_code,
        "title": {"title": {"value": title}},
        "type": "grant",
        "organization-defined-type": {"value": instrument} if instrument else None,
        "organization": {"name": "SNSF"},
        "start-date": start,
        "end-date": end,
        "amount": {"value": amount, "currency-code": "CHF"} if amount else None,
        "url": {"value": url} if url else None,
        "external-ids": {"external-id": eid},
        "short-description": description,
    }


DETAILS = {
    1: _detail(1, "ALLIES", _date("2018", "01"), _date("2021", "09"),
               grant_number="174239", instrument="CHIST-ERA"),
    2: _detail(2, "FairMI", _date("2024", "03"), _date("2028", "02"),
               url="https://example.org/fairmi"),
    3: _detail(3, "SECure", _date("2022", "02"), None,
               amount=None, description=""),
}


def _payload(*groups):
    return {"group": [{"funding-summary": list(g)} for g in groups]}


def _fetch(put_code):
    return DETAILS[put_code]


# --------------------------------------------------------------------------- #
# Deduplication
# --------------------------------------------------------------------------- #
def test_self_asserted_summary_wins_within_a_group():
    """ORCID groups every assertion of one grant; André's own must be kept."""
    group = {"funding-summary": [_summary(9, self_asserted=False), _summary(1)]}
    assert uf.pick_summary(group)["put-code"] == 1


def test_group_without_a_self_assertion_falls_back_to_the_first():
    group = {"funding-summary": [_summary(9, self_asserted=False)]}
    assert uf.pick_summary(group)["put-code"] == 9


def test_duplicated_grant_yields_one_entry():
    payload = _payload([_summary(1), _summary(9, self_asserted=False)])
    entries = uf.build_entries(payload, fetch=_fetch)
    assert [e["put_code"] for e in entries] == [1]


# --------------------------------------------------------------------------- #
# Ordering
# --------------------------------------------------------------------------- #
def test_sorted_by_closing_date_descending():
    payload = _payload([_summary(1)], [_summary(2)])
    assert [e["title"] for e in uf.build_entries(payload, fetch=_fetch)] == [
        "FairMI", "ALLIES"]


def test_missing_end_date_falls_back_to_the_start_date():
    """SECure has no end date, so its 2022 start is what places it — between
    FairMI (ends 2028) and ALLIES (ends 2021)."""
    payload = _payload([_summary(1)], [_summary(2)], [_summary(3)])
    assert [e["title"] for e in uf.build_entries(payload, fetch=_fetch)] == [
        "FairMI", "SECure", "ALLIES"]


def test_undated_grant_sorts_last():
    entries = uf.sort_entries([
        {"title": "undated", "start": None, "end": None},
        {"title": "dated", "start": "2019-01", "end": "2020-05"},
    ])
    assert [e["title"] for e in entries] == ["dated", "undated"]


# --------------------------------------------------------------------------- #
# Field extraction
# --------------------------------------------------------------------------- #
def test_year_month():
    assert uf.year_month(_date("2028", "02")) == "2028-02"
    assert uf.year_month(_date("2028")) == "2028"
    assert uf.year_month(None) is None


def test_entry_fields():
    e = uf.build_entry(DETAILS[1])
    assert e["title"] == "ALLIES"
    assert e["instrument"] == "CHIST-ERA"
    assert e["amount"] == 200000.0 and e["currency"] == "CHF"
    assert e["start"] == "2018-01" and e["end"] == "2021-09"
    assert e["grant_number"] == "174239"


def test_funder_name_is_canonicalised():
    """One agency, several names across assertions — the page must not show
    both "SNSF" and "Swiss National Science Foundation"."""
    assert uf.build_entry(DETAILS[1])["funder"] == "Swiss National Science Foundation"


def test_unmapped_funder_is_left_alone():
    detail = dict(DETAILS[1], organization={"name": "TheArk"})
    assert uf.build_entry(detail)["funder"] == "TheArk"


def test_missing_optional_fields_become_none():
    """A grant with no amount, no link and no abstract must build, not crash —
    the template hides each of those independently."""
    e = uf.build_entry(DETAILS[3])
    assert (e["amount"], e["currency"]) == (None, None)
    assert (e["url"], e["grant_number"], e["instrument"]) == (None, None, None)
    assert e["description"] is None
    assert e["end"] is None


def test_url_falls_back_to_the_identifier_resolver():
    """Most SNSF grants carry no `url`; their official page is the grant
    identifier's resolver, and that is the link the site shows."""
    assert uf.build_entry(DETAILS[1])["url"] == "https://data.snf.ch/grants/grant/174239"
    assert uf.build_entry(DETAILS[2])["url"] == "https://example.org/fairmi"


# --------------------------------------------------------------------------- #
# Check mode
# --------------------------------------------------------------------------- #
def _commit(tmp_path, monkeypatch, entries):
    path = tmp_path / "funding.json"
    path.write_text(json.dumps({"count": len(entries), "entries": entries}))
    monkeypatch.setattr(zc, "FUNDING_FILE", path)
    monkeypatch.setattr(zc, "ROOT", tmp_path)


def test_check_passes_when_in_sync(tmp_path, monkeypatch, capsys):
    fresh = uf.build_entries(_payload([_summary(1)], [_summary(2)]), fetch=_fetch)
    _commit(tmp_path, monkeypatch, fresh)
    assert uf.do_check(fresh, verbose=False) == 0
    assert "up to date" in capsys.readouterr().out


def test_check_reports_a_changed_field(tmp_path, monkeypatch, capsys):
    fresh = uf.build_entries(_payload([_summary(1)]), fetch=_fetch)
    stale = [dict(fresh[0], amount=1.0)]
    _commit(tmp_path, monkeypatch, stale)
    assert uf.do_check(fresh, verbose=False) == 1
    assert "amount" in capsys.readouterr().err


def test_check_reports_a_new_grant(tmp_path, monkeypatch, capsys):
    fresh = uf.build_entries(_payload([_summary(1)], [_summary(2)]), fetch=_fetch)
    _commit(tmp_path, monkeypatch, [e for e in fresh if e["put_code"] == 1])
    assert uf.do_check(fresh, verbose=False) == 1
    assert "+ 2" in capsys.readouterr().err


def test_check_notices_a_pure_reordering(tmp_path, monkeypatch, capsys):
    """Order is the page's content, so a file whose entries are all present but
    misordered is stale too."""
    fresh = uf.build_entries(_payload([_summary(1)], [_summary(2)]), fetch=_fetch)
    _commit(tmp_path, monkeypatch, list(reversed(fresh)))
    assert uf.do_check(fresh, verbose=False) == 1
    assert "order changed" in capsys.readouterr().err


def test_unreachable_orcid_warns_but_passes(tmp_path, monkeypatch, capsys):
    """An ORCID outage proves nothing about freshness and must not break a
    deploy — the same contract as check-outputs and check-featured."""
    _commit(tmp_path, monkeypatch, uf.build_entries(_payload([_summary(1)]), fetch=_fetch))
    assert uf.offline(OSError("no route to host")) == 0
    assert "cannot verify freshness" in capsys.readouterr().err


def test_missing_file_fails_the_check(tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(zc, "FUNDING_FILE", tmp_path / "absent.json")
    monkeypatch.setattr(zc, "ROOT", tmp_path)
    assert uf.do_check([], verbose=False) == 1
    assert "is missing" in capsys.readouterr().err
