"""The static/-stays-small gate: only optimised covers live in the repo, every
other asset is served from Idiap. See AGENTS.md, "Large assets live on Idiap"."""

import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

import validate_content as vc  # noqa: E402


def test_check_static_accepts_covers_and_chrome(tmp_path, monkeypatch):
    monkeypatch.setattr(vc, "STATIC", tmp_path)
    (tmp_path / "images" / "covers").mkdir(parents=True)
    (tmp_path / "images" / "covers" / "ok.png").write_bytes(b"x" * 1024)
    (tmp_path / "images" / "favicon.ico").write_bytes(b"x")
    errors = []
    vc.check_static(errors)
    assert errors == []


def test_check_static_rejects_non_cover_and_oversized(tmp_path, monkeypatch):
    monkeypatch.setattr(vc, "STATIC", tmp_path)
    (tmp_path / "pdfs").mkdir()
    (tmp_path / "pdfs" / "talk.pdf").write_bytes(b"x")
    (tmp_path / "images" / "covers").mkdir(parents=True)
    (tmp_path / "images" / "covers" / "huge.jpg").write_bytes(
        b"x" * (vc.STATIC_MAX_BYTES + 1)
    )
    errors = []
    vc.check_static(errors)
    assert len(errors) == 2
    assert any("idiap-public/pdfs/talk.pdf" in e for e in errors)
    assert any("exceeds" in e and "huge.jpg" in e for e in errors)


def test_check_static_exempts_the_generated_cv(tmp_path, monkeypatch):
    """`pixi run cv` writes the CV into static/ so Hugo publishes it. It is a PDF,
    it is well over the cap, and it is git-ignored — none of which is an error."""
    monkeypatch.setattr(vc, "STATIC", tmp_path)
    (tmp_path / vc.STATIC_BUILD_PRODUCTS[0]).write_bytes(
        b"x" * (vc.STATIC_MAX_BYTES + 1)
    )
    errors = []
    vc.check_static(errors)
    assert errors == []


def test_check_idiap_refs_flags_missing_asset(tmp_path, monkeypatch):
    content, mirror = tmp_path / "content", tmp_path / "idiap-public"
    (content / "media").mkdir(parents=True)
    (mirror / "pdfs").mkdir(parents=True)
    (mirror / "pdfs" / "here.pdf").write_bytes(b"x")
    (content / "media" / "talk.md").write_text(
        f"[a]({vc.IDIAP_URL}pdfs/here.pdf) [b]({vc.IDIAP_URL}pdfs/gone.pdf)\n"
    )
    monkeypatch.setattr(vc, "CONTENT", content)
    monkeypatch.setattr(vc, "IDIAP_LOCAL", mirror)
    monkeypatch.setattr(vc, "ROOT", tmp_path)
    errors = []
    vc.check_idiap_refs(errors)
    assert len(errors) == 1
    assert "pdfs/gone.pdf" in errors[0]


def test_check_idiap_refs_skipped_without_mirror(tmp_path, monkeypatch):
    """CI has no local mirror; the check must stay quiet there."""
    monkeypatch.setattr(vc, "IDIAP_LOCAL", tmp_path / "absent")
    errors = []
    vc.check_idiap_refs(errors)
    assert errors == []
