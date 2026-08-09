"""WCAG AA contrast for the theme palette.

Colour regressions are invisible until someone cannot read the text, and they
have happened twice: ramping the CV button's gradient toward white put its label
at 3.95:1 in light and 1.80:1 in dark, and an accent-tinted pill nearly vanished
against the dark hero.

The palette is parsed out of ``assets/css/main.css`` rather than duplicated here,
so changing ``--accent`` cannot leave this test asserting the old value. Only the
flat hex custom properties are read; everything built with ``color-mix()`` is
derived by the browser and is checked by eye.
"""

import pathlib
import re

import pytest

CSS = pathlib.Path(__file__).resolve().parents[2] / "assets" / "css" / "main.css"

# (foreground, background, minimum ratio, what it is)
PAIRS = (
    ("text", "bg", 4.5, "body text"),
    ("text", "surface", 4.5, "body text on cards and panels"),
    ("muted", "bg", 4.5, "meta text"),
    ("muted", "surface", 4.5, "meta text on cards and panels"),
    ("accent", "bg", 4.5, "links"),
    ("accent", "surface", 4.5, "links on cards and panels"),
    ("accent-hover", "bg", 4.5, "hovered links"),
    # The CV button is a gradient from --accent to --accent-2; its label must
    # clear both stops, which is what forces the hue-shift-at-constant-lightness
    # rule documented in AGENTS.md.
    ("on-accent", "accent", 4.5, "button label on the gradient start"),
    ("on-accent", "accent-2", 4.5, "button label on the gradient end"),
    ("accent-2", "bg", 4.5, "the teal wherever it is used as text"),
)


def _relative_luminance(hex_colour):
    channels = [int(hex_colour[i : i + 2], 16) / 255 for i in (1, 3, 5)]
    linear = [
        c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4 for c in channels
    ]
    return 0.2126 * linear[0] + 0.7152 * linear[1] + 0.0722 * linear[2]


def contrast(foreground, background):
    """Contrast ratio of two ``#rrggbb`` colours, per WCAG 2.1."""
    a, b = _relative_luminance(foreground), _relative_luminance(background)
    lighter, darker = max(a, b), min(a, b)
    return (lighter + 0.05) / (darker + 0.05)


def _themes():
    """Parse the light and dark palettes out of main.css.

    Light is the ``:root`` block; dark is ``:root[data-theme="dark"]``. The
    ``prefers-color-scheme`` block declares the same values and is skipped.
    """
    css = CSS.read_text(encoding="utf-8")

    def block(pattern):
        match = re.search(pattern + r"\s*\{(.*?)\n\}", css, re.S)
        assert match, f"no block matching {pattern!r} in {CSS}"
        return dict(re.findall(r"--([a-z0-9-]+):\s*(#[0-9a-fA-F]{6})", match.group(1)))

    light = block(r"(?<!\])\n:root")
    dark = dict(light)
    dark.update(block(r':root\[data-theme="dark"\]'))
    return {"light": light, "dark": dark}


@pytest.mark.parametrize("theme", ("light", "dark"))
@pytest.mark.parametrize("fg,bg,minimum,what", PAIRS)
def test_pair_meets_aa(theme, fg, bg, minimum, what):
    palette = _themes()[theme]
    for name in (fg, bg):
        assert name in palette, f"--{name} missing from the {theme} palette"
    ratio = contrast(palette[fg], palette[bg])
    assert ratio >= minimum, (
        f"{theme}: --{fg} on --{bg} ({what}) is {ratio:.2f}:1, "
        f"below the {minimum}:1 minimum. Hold the two colours at the same "
        f"lightness and shift hue instead of lightening one of them."
    )


def test_both_themes_define_the_same_keys():
    """A colour defined in one theme but not the other renders as an inherited
    surprise rather than a visible error."""
    light, dark = _themes()["light"], _themes()["dark"]
    used = {name for pair in PAIRS for name in pair[:2]}
    assert used <= set(light), f"light palette missing {used - set(light)}"
    assert used <= set(dark), f"dark palette missing {used - set(dark)}"
