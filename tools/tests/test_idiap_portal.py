"""Offline unit tests for the Idiap publication-portal check (no network).

SPDX-FileCopyrightText: Copyright © 2026 Idiap Research Institute <contact@idiap.ch>

SPDX-License-Identifier: BSD-3-Clause
"""

import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

import idiap_portal  # noqa: E402

# Trimmed from a real export: HTML-wrapped, entity-escaped, LaTeX accents, an
# abstract over two lines, a DOI written as a URL, and an Idiap-RR twin.
EXPORT = """<html><body><pre>
%Aigaion2 BibTeX export from Idiap Publications
@ARTICLE{Amiot_CBM_2025,
                      author = {Amiot, Victor and Anjos, Andr{\\'{e}}},
                    projects = {CAD4IED, FAIRMI},
         mainresearchprogram = {AI for Life},
                       title = {Automatic grading &amp; more},
                        year = {2025},
                         doi = {https://doi.org/10.1016/J.X.2025.1},
                    abstract = {Line one,
with a comma.}
}

@TECHREPORT{Ozbulak_Idiap-RR-01-2026,
                       title = {Loss-Conditioned Boundary},
                        year = {2026}
}
</pre></body></html>"""


def _entry(title, doi=None, year=2026, type_="Conference Paper", key="k"):
    return {"title": title, "doi": doi, "year": year, "type": type_, "key": key}


def test_parse_export():
    """Fields survive HTML escaping, multi-line values and URL-form DOIs."""
    cbm, rr = idiap_portal.parse_bibtex(EXPORT)
    assert (cbm["_type"], cbm["_key"]) == ("article", "Amiot_CBM_2025")
    assert cbm["title"] == "Automatic grading & more"
    assert cbm["projects"] == "CAD4IED, FAIRMI"
    assert cbm["abstract"].endswith("with a comma.")
    assert rr["_type"] == "techreport"


def test_check_matches_and_reports():
    """DOI or title matches; a report never stands in; old papers are exempt."""
    records = idiap_portal.parse_bibtex(EXPORT)
    entries = [
        _entry("Different title", doi="10.1016/j.x.2025.1", type_="Journal Article"),
        _entry("Loss-Conditioned  Boundary", key="ozbulak"),  # only the RR has it
        _entry("Old paper", year=2019, key="old"),
        _entry("Some dataset", type_="Dataset", key="data"),
    ]
    errors = idiap_portal.check(entries, records, since=2022)
    fatal = [e for e in errors if not e.startswith("WARN:")]
    assert len(fatal) == 1 and fatal[0].startswith("ozbulak ")
    # Amiot has projects and a main program; the RR is not attribution-checked.
    assert [e for e in errors if e.startswith("WARN:")] == []
