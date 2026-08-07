#!/usr/bin/env python3
"""Add ONE work to Zotero "My Publications" (the write path of the
add-zotero-output skill). Enriches from Crossref by DOI, creates the item
with inPublications=True, and optionally attaches a PDF (public or private).

Needs a read-write key in ~/.config/pyzotero.toml (api_key + user_id).

    # dry-run: show what would be created from a DOI
    python tools/add_zotero_output.py --doi 10.1109/foo --dry-run

    # create it, attach a public PDF
    python tools/add_zotero_output.py --doi 10.1109/foo --pdf paper.pdf --public

    # no DOI: supply the essentials yourself
    python tools/add_zotero_output.py --type conferencePaper \\
        --title "…" --venue "…" --year 2026 --authors "Jane Doe;André Anjos"

    # relate it to an existing item (its preprint, or a dataset it uses) — by
    # Zotero item key or DOI; the link is created bidirectionally
    python tools/add_zotero_output.py --doi 10.1109/foo --related 10.48550/arXiv.1234;ABCD1234

    # software (computerProgram): license + typed links + docs abstract
    python tools/add_zotero_output.py --type computerProgram --title mytool --year 2025 \\
        --abstract "…" --license GPL-3.0 \\
        --links "docs=…;pypi=…;conda=…;repo=…" [--archived]

Overrides (--title/--type/--venue/--year/--authors) win over Crossref.
"""

from __future__ import annotations

import argparse
import pathlib
import sys
import tempfile

import zotero_common as zc

# Crossref work type -> Zotero item type.
CR2Z = {
    "journal-article": "journalArticle",
    "proceedings-article": "conferencePaper",
    "posted-content": "preprint",
    "book-chapter": "bookSection",
    "book": "book",
    "report": "report",
    "dissertation": "thesis",
    "monograph": "book",
    "reference-entry": "bookSection",
}


def creators(names: list[str]) -> list[dict]:
    out = []
    for n in names:
        n = n.strip()
        if not n:
            continue
        first, _, last = n.rpartition(" ")
        out.append({"creatorType": "author", "firstName": first, "lastName": last})
    return out


def from_crossref(doi: str) -> dict:
    m = zc.fetch_crossref(doi) or {}
    if not m:
        print(f"! Crossref had nothing for {doi}; supply metadata via flags.", file=sys.stderr)
    names = [" ".join(p for p in (a.get("given", ""), a.get("family", "")) if p).strip()
             or a.get("name", "") for a in (m.get("author") or [])]
    issued = ((m.get("issued") or {}).get("date-parts") or [[None]])[0]
    date = "-".join(str(x) for x in issued if x is not None) if issued and issued[0] else None
    return {
        "itemType": CR2Z.get((m.get("type") or "").lower(), "journalArticle"),
        "title": (m.get("title") or [None])[0],
        "authors": [n for n in names if n],
        "venue": (m.get("container-title") or [None])[0],
        "date": date,
        "url": m.get("URL"),
    }


def venue_field(item_type: str) -> str:
    return {"conferencePaper": "proceedingsTitle", "bookSection": "bookTitle"}.get(
        item_type, "publicationTitle")


def resolve_related(user_id: str, values: list[str]) -> list[tuple[str, str]]:
    """Map each --related value (a Zotero item key or a DOI) to (key, title),
    looked up against My Publications. Unknown values are reported and skipped."""
    items = zc.fetch_public_items(user_id)
    by_key = {it["key"]: it["data"].get("title", "") for it in items}
    by_doi = {zc.normalize_doi(it["data"].get("DOI")): it["key"]
              for it in items if it["data"].get("DOI")}
    out = []
    for v in (s.strip() for s in values):
        if not v:
            continue
        if v in by_key:
            out.append((v, by_key[v]))
        elif zc.normalize_doi(v) in by_doi:
            k = by_doi[zc.normalize_doi(v)]
            out.append((k, by_key.get(k, "")))
        else:
            print(f"  ! related target not found (skipped): {v}", file=sys.stderr)
    return out


def add_relation(zot, user_id: str, a_key: str, b_key: str) -> None:
    """Merge-safe: add b to a's dc:relation without clobbering existing links."""
    uri = f"http://zotero.org/users/{user_id}/items/{b_key}"
    it = zot.item(a_key)
    rel = it["data"].setdefault("relations", {})
    cur = rel.get("dc:relation")
    cur = [cur] if isinstance(cur, str) else (cur or [])
    if uri not in cur:
        rel["dc:relation"] = cur + [uri]
        zot.update_item(it["data"])


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--doi")
    ap.add_argument("--pdf")
    vis = ap.add_mutually_exclusive_group()
    vis.add_argument("--public", action="store_true", help="serve the PDF publicly")
    vis.add_argument("--private", action="store_true", help="store the PDF, don't serve it")
    ap.add_argument("--type", dest="itype", help="Zotero item type override")
    ap.add_argument("--title")
    ap.add_argument("--venue")
    ap.add_argument("--year")
    ap.add_argument("--authors", help='"First Last;First Last" (semicolon-separated)')
    ap.add_argument("--related", help='relate to existing item(s): Zotero item key(s) '
                    'or DOI(s), ";"-separated (e.g. a preprint, or a dataset it uses)')
    ap.add_argument("--abstract", help="abstract / description (-> abstractNote)")
    ap.add_argument("--paper-page", dest="paper_page",
                    help="URL of the article's paper page (-> url field): a one-pager with "
                    "more about the work. Overrides the DOI resolver Crossref would set.")
    ap.add_argument("--software", help="companion-code repo URL for THIS publication "
                    "(paper-specific validation code etc.) -> a 'Software' link beside its DOI/PDF")
    ap.add_argument("--license", help="software: SPDX license (-> rights)")
    ap.add_argument("--links", help='software links "docs=…;pypi=…;conda=…;repo=…" '
                    "(repo -> url; the rest -> extra)")
    ap.add_argument("--archived", action="store_true", help="software: mark as archived")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()

    meta = from_crossref(a.doi) if a.doi else {"itemType": "journalArticle"}
    if a.itype:
        meta["itemType"] = a.itype
    if a.title:
        meta["title"] = a.title
    if a.venue:
        meta["venue"] = a.venue
    if a.year:
        meta["date"] = a.year
    if a.authors:
        meta["authors"] = a.authors.split(";")
    if not meta.get("title"):
        sys.exit("No title (Crossref empty and no --title). Aborting.")
    if a.pdf and not (a.public or a.private):
        sys.exit("Attaching a PDF requires --public or --private.")

    itype = meta["itemType"]
    data = {
        "itemType": itype,
        "title": meta["title"].strip(),
        "creators": creators(meta.get("authors") or []),
        "date": meta.get("date") or "",
        "DOI": zc.normalize_doi(a.doi) or "",
        "url": "",   # deprecated: the paper page lives in extra `Homepage:` (below);
                     # software overrides this with its repo further down
        "inPublications": True,
        venue_field(itype): meta.get("venue") or "",
    }
    if a.abstract:
        data["abstractNote"] = a.abstract

    if itype == "computerProgram":  # software: programmer + license + typed links
        for c in data["creators"]:
            c["creatorType"] = "programmer"
        if a.license:
            data["rights"] = a.license
        links = dict(kv.split("=", 1) for kv in (a.links or "").split(";") if "=" in kv)
        if links.get("repo"):
            data["url"] = links["repo"]
        extra = [f"{lbl}: {links[k]}" for lbl, k in
                 (("Docs", "docs"), ("PyPI", "pypi"), ("conda-forge", "conda")) if links.get(k)]
        if a.archived:
            extra.append("Archived: true")
        if extra:
            data["extra"] = "\n".join(extra)
    else:  # publication: paper page + companion code are labeled lines in extra
        extra = []
        if a.paper_page:
            extra.append(f"Homepage: {a.paper_page}")
        if a.software:
            extra.append(f"Software: {a.software}")
        if extra:
            data["extra"] = "\n".join(extra)

    related = resolve_related(zc.read_user_id(), a.related.split(";")) if a.related else []

    print(f"[{'DRY-RUN' if a.dry_run else 'CREATE'}] {itype}: {data['title'][:70]}")
    print(f"  authors: {', '.join(c['lastName'] for c in data['creators']) or '—'}")
    if itype == "computerProgram":
        print(f"  license: {data.get('rights') or '—'}  url: {data.get('url') or '—'}")
        print(f"  extra:   {(data.get('extra') or '—').replace(chr(10), ' | ')}")
    else:
        print(f"  venue:   {meta.get('venue') or '—'}  date: {data['date'] or '—'}  doi: {data['DOI'] or '—'}")
        if a.paper_page:
            print(f"  paper page: {a.paper_page}")
        if a.software:
            print(f"  software: {a.software}")
    if a.pdf:
        print(f"  pdf:     {a.pdf}  ({'PUBLIC' if a.public else 'private'})")
    for k, t in related:
        print(f"  related: {k}  {t[:55]}")
    if a.dry_run:
        return 0

    from pyzotero import zotero
    uid, key = zc.read_credentials()
    zot = zotero.Zotero(uid, "user", key)
    created = zot.create_items([data])
    if not created.get("success"):
        sys.exit(f"create failed: {created.get('failed')}")
    item_key = created["success"]["0"]
    print(f"  -> created {item_key}")

    if a.pdf:
        src = pathlib.Path(a.pdf)
        tmp = pathlib.Path(tempfile.mkdtemp())
        (tmp / src.name).write_bytes(src.read_bytes())
        att = zot.create_items([{
            "itemType": "attachment", "linkMode": "imported_file",
            "title": src.name, "filename": src.name, "contentType": "application/pdf",
            "parentItem": item_key, "inPublications": bool(a.public),
        }])
        if not att.get("success"):
            sys.exit(f"attachment create failed: {att.get('failed')}")
        up = zot.upload_attachments([att["successful"]["0"]["data"]], basedir=str(tmp))
        if up.get("failure"):
            sys.exit(f"upload failed: {up['failure']}")
        print(f"  -> attached {att['success']['0']} ({'public' if a.public else 'private'})")

    for k, t in related:  # bidirectional dc:relation (merge-safe)
        add_relation(zot, uid, item_key, k)
        add_relation(zot, uid, k, item_key)
        print(f"  -> related to {k} ({t[:40]})")

    print("\nDone. Run `pixi run outputs` to refresh the site, then `pixi run orcid-report`.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
