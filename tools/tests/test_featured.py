"""Offline unit tests for the ORCID featured-works check (no network).

SPDX-FileCopyrightText: Copyright © 2026 Idiap Research Institute <contact@idiap.ch>

SPDX-License-Identifier: BSD-3-Clause
"""

import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

import check_featured as cf  # noqa: E402


# --------------------------------------------------------------------------- #
# Fixtures — trimmed to the fields the check reads.
# --------------------------------------------------------------------------- #
def _orcid_work(doi: str) -> dict:
    return {
        "putCode": {"value": "1"},
        "workExternalIdentifiers": [
            {
                "externalIdentifierId": {"value": doi},
                "externalIdentifierType": {"value": "doi"},
            }
        ],
    }


ENTRIES = {
    "entries": [
        {"title": "Retinal work", "doi": "10.1038/S41598-022-09675-Y", "key": "anjos_retina_2022"},
        {"title": "A dataset", "doi": None, "key": "anjos_data_2024"},
    ]
}


def _write_outputs(tmp_path, monkeypatch) -> None:
    f = tmp_path / "outputs.json"
    f.write_text(json.dumps(ENTRIES))
    monkeypatch.setattr(cf.zotero_common, "OUTPUT_FILE", f)


def test_orcid_payload_parsing(monkeypatch):
    """DOIs are lifted out of the endpoint's nested shape and normalised."""

    class _Response:
        @staticmethod
        def raise_for_status() -> None:
            pass

        @staticmethod
        def json() -> list[dict]:
            return [
                _orcid_work("https://doi.org/10.1038/s41598-022-09675-y"),
                _orcid_work("10.1016/J.COMPBIOMED.2020.103744"),
                {"putCode": {"value": "3"}, "workExternalIdentifiers": None},
            ]

    import requests

    monkeypatch.setattr(requests, "get", lambda *a, **k: _Response())
    assert cf._orcid_featured_dois() == {
        "10.1038/s41598-022-09675-y",
        "10.1016/j.compbiomed.2020.103744",
    }


def test_resolve_by_doi_and_key(tmp_path, monkeypatch):
    """A DOI and its citation key resolve to the same normalised DOI."""
    _write_outputs(tmp_path, monkeypatch)
    resolved, unresolved = cf._resolve(
        ["10.1038/s41598-022-09675-y", "anjos_retina_2022", "anjos_data_2024", "nope"]
    )
    assert resolved == {"10.1038/s41598-022-09675-y": "Retinal work"}
    # a DOI-less work and an unknown ref are both unusable here
    assert unresolved == ["anjos_data_2024", "nope"]


def test_main_fails_when_not_starred(tmp_path, monkeypatch, capsys):
    """A featured work missing from ORCID's stars breaks validation."""
    _write_outputs(tmp_path, monkeypatch)
    monkeypatch.setattr(cf, "_featured_refs", lambda: ["anjos_retina_2022"])
    monkeypatch.setattr(cf, "_orcid_featured_dois", lambda: {"10.5555/other"})
    assert cf.main() == 1
    assert "not starred on ORCID" in capsys.readouterr().err


def test_main_passes_when_orcid_stars_more(tmp_path, monkeypatch):
    """ORCID starring works the site does not feature is fine (subset check)."""
    _write_outputs(tmp_path, monkeypatch)
    monkeypatch.setattr(cf, "_featured_refs", lambda: ["anjos_retina_2022"])
    monkeypatch.setattr(
        cf, "_orcid_featured_dois", lambda: {"10.1038/s41598-022-09675-y", "10.5555/extra"}
    )
    assert cf.main() == 0


def test_main_warns_when_orcid_unreachable(tmp_path, monkeypatch, capsys):
    """The endpoint is undocumented: a failure warns, it never breaks the gate."""
    _write_outputs(tmp_path, monkeypatch)
    monkeypatch.setattr(cf, "_featured_refs", lambda: ["anjos_retina_2022"])

    def _boom() -> set[str]:
        raise RuntimeError("404")

    monkeypatch.setattr(cf, "_orcid_featured_dois", _boom)
    assert cf.main() == 0
    assert "WARN" in capsys.readouterr().err
