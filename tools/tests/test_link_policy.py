"""Verify that temporary Idiap warnings preserve strict checks elsewhere.

SPDX-FileCopyrightText: Copyright © 2026 Idiap Research Institute <contact@idiap.ch>

SPDX-License-Identifier: BSD-3-Clause
"""

import os
import pathlib
import re
import subprocess
import tomllib

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[2]


@pytest.mark.parametrize("url,idiap", [
    ("https://idiap.ch/", True),
    ("https://www.idiap.ch/en/projects/fedars", True),
    ("http://lab.idiap.ch:8080/path", True),
    ("https://gitlab.idiap.ch/group/project", True),
    ("https://nested.lab.idiap.ch/path", True),
    ("https://idiap.ch.example.org/path", False),
    ("https://notidiap.ch/path", False),
    ("https://example.org/idiap.ch/path", False),
])
def test_idiap_warning_scope(url, idiap):
    """Both runs must partition hostnames without excluding unrelated domains."""
    strict = tomllib.loads((ROOT / "lychee.toml").read_text())
    warnings = tomllib.loads((ROOT / "lychee-idiap.toml").read_text())
    assert "exclude" not in warnings
    assert any(re.search(pattern, url) for pattern in strict["exclude"]) == idiap
    assert any(re.search(pattern, url) for pattern in warnings["include"]) == idiap


@pytest.mark.parametrize("ci", ["", "true"])
def test_idiap_failures_warn_locally_and_in_ci(tmp_path, ci):
    """A failed Idiap check must report a warning and let validation continue."""
    lychee = tmp_path / "lychee"
    lychee.write_text("#!/bin/sh\nexit 2\n")
    lychee.chmod(0o755)
    environment = dict(os.environ, PATH=f"{tmp_path}:{os.environ['PATH']}", CI=ci)
    result = subprocess.run(
        ["sh", str(ROOT / "tools/check-links-idiap.sh")],
        env=environment, capture_output=True, text=True, check=False,
    )
    assert result.returncode == 0
    assert "WARN: idiap.ch link checks failed" in result.stderr
