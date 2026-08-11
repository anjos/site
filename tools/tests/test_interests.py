"""Offline unit tests for tools/update-interests.py (no network).

The ORCID `/keywords` payload is small, so the tool's whole job is ordering and
drift reporting: keywords come back sorted by `display-index` descending, which
is the order ORCID itself lists them in, and the check must fail on a reorder as
loudly as on an add or a remove — the hero pills and the CV both render the list
in file order.

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
_spec = importlib.util.spec_from_file_location(
    "update_interests", TOOLS / "update-interests.py"
)
ui = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(ui)


def payload(*pairs):
    """An ORCID /keywords payload from (display-index, content) pairs."""
    return {"keyword": [{"display-index": i, "content": c} for i, c in pairs]}


def commit(tmp_path, monkeypatch, entries):
    """Write a committed data/interests.json into a temporary root."""
    path = tmp_path / "interests.json"
    path.write_text(json.dumps({"count": len(entries), "entries": entries}))
    monkeypatch.setattr(zc, "INTERESTS_FILE", path)
    monkeypatch.setattr(zc, "ROOT", tmp_path)
    return path


def test_highest_display_index_comes_first():
    got = ui.build_entries(payload((1, "Medical AI"), (7, "Pattern Recognition")))
    assert got == ["Pattern Recognition", "Medical AI"]


def test_blanks_and_whitespace_are_cleaned_up():
    got = ui.build_entries(payload((3, "  Computer Vision  "), (2, "   "), (1, "")))
    assert got == ["Computer Vision"]


def test_missing_display_index_sorts_last():
    got = ui.build_entries({"keyword": [{"content": "A"}, {"display-index": 2,
                                                           "content": "B"}]})
    assert got == ["B", "A"]


def test_check_passes_when_current(tmp_path, monkeypatch, capsys):
    commit(tmp_path, monkeypatch, ["Medical AI", "Computer Vision"])
    assert ui.do_check(["Medical AI", "Computer Vision"]) == 0
    assert "up to date" in capsys.readouterr().out


def test_check_reports_adds_and_removes(tmp_path, monkeypatch, capsys):
    commit(tmp_path, monkeypatch, ["Medical AI", "Biometrics"])
    assert ui.do_check(["Medical AI", "Computer Vision"]) == 1
    err = capsys.readouterr().err
    assert "+ Computer Vision" in err and "- Biometrics" in err


def test_check_fails_on_a_pure_reorder(tmp_path, monkeypatch, capsys):
    """Order is content here: it is the order the pills and the CV print."""
    commit(tmp_path, monkeypatch, ["Medical AI", "Computer Vision"])
    assert ui.do_check(["Computer Vision", "Medical AI"]) == 1
    assert "order changed" in capsys.readouterr().err


def test_missing_file_fails_the_check(tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(zc, "INTERESTS_FILE", tmp_path / "absent.json")
    monkeypatch.setattr(zc, "ROOT", tmp_path)
    assert ui.do_check(["Medical AI"]) == 1
    assert "is missing" in capsys.readouterr().err


def test_unreachable_orcid_warns_but_passes(tmp_path, monkeypatch, capsys):
    """An outage elsewhere must never break a deploy."""
    commit(tmp_path, monkeypatch, ["Medical AI"])
    assert ui.offline(RuntimeError("boom")) == 0
    assert "cannot verify freshness" in capsys.readouterr().err
