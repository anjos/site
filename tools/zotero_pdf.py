#!/usr/bin/env python3
"""Download the PDF attached to a Zotero "My Publications" item — public OR private.

The site's public feed only exposes *public* PDF attachments; this reads the file
through the *authenticated* API, so it also fetches PDFs that were kept private. Use it
to read a research output's full text (for grounding project/thesis prose) before ever
falling back to a web search.

Needs a read key in ~/.config/pyzotero.toml (api_key + user_id).

    python tools/zotero_pdf.py --doi 10.1038/s41598-026-46069-w -o /tmp/paper.pdf
    python tools/zotero_pdf.py --key ABCD1234 -o /tmp/paper.pdf
"""

from __future__ import annotations

import argparse
import sys

import zotero_common as zc


def resolve_key(uid: str, doi: str | None, key: str | None) -> str | None:
    """Parent item key from a DOI (items are in My Publications, so the public feed
    resolves them even when their PDF is private) or the key itself."""
    if key:
        return key
    nd = zc.normalize_doi(doi)
    for it in zc.fetch_public_items(uid):
        if zc.normalize_doi(it["data"].get("DOI")) == nd:
            return it["key"]
    return None


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--doi")
    g.add_argument("--key", help="Zotero item key")
    ap.add_argument("-o", "--out", required=True, help="output .pdf path")
    a = ap.parse_args()

    from pyzotero import zotero
    uid, key = zc.read_credentials()
    zot = zotero.Zotero(uid, "user", key)

    pk = resolve_key(uid, a.doi, a.key)
    if not pk:
        sys.exit(f"item not found ({a.doi or a.key})")
    pdfs = [c for c in zot.children(pk)
            if c["data"].get("contentType") == "application/pdf"
            or c["data"].get("filename", "").lower().endswith(".pdf")]
    if not pdfs:
        sys.exit(f"no PDF attachment on item {pk} (nothing to read; try the web as a last resort)")
    att = pdfs[0]
    content = zot.file(att["key"])
    with open(a.out, "wb") as fh:
        fh.write(content)
    vis = "public" if att["data"].get("inPublications") else "private"
    print(f"wrote {a.out} ({len(content)} bytes) from {vis} attachment {att['key']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
