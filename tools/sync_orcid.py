#!/usr/bin/env python3
"""Apply the Zotero -> ORCID difference to the ORCID record, via the web session.

Zotero "My Publications" is the source of truth. This tool computes exactly what
ORCID is missing or has wrong, and either shows it or applies it:

  DRY-RUN (default)  Print the adds and edits it would perform. Writes nothing.
  REPORT  (--report) Write that same difference to Markdown. Writes nothing.
  APPLY   (--apply)  Perform them, paced by --delay, printing each as it goes.

Why the web session and not the API
-----------------------------------
ORCID enforces strict source-matching: **only the source that created an item
may edit or delete it**. Practically every work on this record was self-asserted
through the website, so a Member API client — a different source — could never
edit them; it could only stack a second assertion onto each and fork the record
into two sources. Acting as the record holder is the only mechanism that can fix
what is already there.

The login is never automated. Playwright opens a *headed, persistent* profile;
you sign in by hand once and the session is reused for weeks. That keeps the
Cloudflare bot-management on /signin, two-factor auth and stored credentials all
out of this script entirely — it only ever acts inside a session a human opened,
on that human's own record.

These are ORCID's internal frontend endpoints, not a public API, so they carry
no compatibility promise. --report and the dry-run never open a browser, so they
keep working as the fallback if those endpoints change.

    python tools/sync_orcid.py                     # dry-run
    python tools/sync_orcid.py --apply             # apply, 1s between writes
    python tools/sync_orcid.py --apply --limit 1   # one work, for a first test

SPDX-FileCopyrightText: Copyright © 2026 Idiap Research Institute <contact@idiap.ch>

SPDX-License-Identifier: BSD-3-Clause
"""

from __future__ import annotations

import argparse
import contextlib
import copy
import json
import pathlib
import sys
import time

import zotero_common as zc

BASE = "https://orcid.org"
WORK_ENDPOINT = f"{BASE}/works/work.json"
WORK_INFO_ENDPOINT = f"{BASE}/works/getWorkInfo.json"
CSRF_ENDPOINT = f"{BASE}/csrf.json"
#: Answers {"loggedIn": bool} whether signed in or not — the authority on session
#: state. The page URL is not: see :func:`signed_in`.
STATUS_ENDPOINT = f"{BASE}/userStatus.json?logUserOut=false"

#: Where the signed-in browser profile lives, beside the Zotero credentials.
PROFILE_DIR = pathlib.Path.home() / ".config" / "orcid-sync-profile"

#: The signed-in session, saved between runs. ORCID authenticates with a *session*
#: cookie, and Chrome discards those when the browser closes — so a persistent
#: profile alone still means signing in on every run. Holds a live credential:
#: created 0600, and never inside the repository.
COOKIE_FILE = pathlib.Path.home() / ".config" / "orcid-sync-cookies.json"

#: Where --report writes when given no path. Git-ignored: it is a scratch view.
DEFAULT_REPORT = zc.ROOT / "orcid-sync-report.md"

#: ORCID's Angular frontend reads this cookie and echoes it in this header.
XSRF_COOKIE = "XSRF-TOKEN"
XSRF_HEADER = "x-xsrf-token"


# --------------------------------------------------------------------------
# Form building (pure — everything below this line is unit-testable offline)
# --------------------------------------------------------------------------

def _text(value: object) -> dict:
    """Wrap a scalar in ORCID's ``Text`` form shape.

    Nearly every WorkForm field is a ``{"value": ..., "errors": []}`` object
    rather than a bare scalar; sending a bare scalar is silently rejected.

    Parameters
    ----------
    value
        The scalar to wrap. ``None`` is preserved as a null value, which is how
        ORCID represents an unset field.

    Returns
    -------
    dict
        The wrapped value.
    """
    return {"value": value, "errors": []}


def _current_ids(form: dict) -> list[dict]:
    """A form's existing identifiers in zotero_common's comparison shape."""
    return [
        {"type": ((e.get("externalIdentifierType") or {}).get("value") or "").lower(),
         "value": (e.get("externalIdentifierId") or {}).get("value") or "",
         "relationship": (e.get("relationship") or {}).get("value") or "self"}
        for e in _external_ids(form)
    ]


def _external_ids(form: dict) -> list:
    """The work's external-identifier list, tolerating a null from ORCID."""
    return form.get("workExternalIdentifiers") or []


def add_external_id(form: dict, id_type: str, value: str,
                    relationship: str = "self") -> None:
    """Add a work identifier to a form, in place, unless it is already there.

    Comparison goes through :func:`zotero_common.normalize_identifier`, because
    the same arXiv id lives on this record as ``2009.01907``, ``abs/2408.16130``
    and ``arXiv:1709.00962``; matching raw strings would leave a work carrying
    two spellings of one identifier.

    Parameters
    ----------
    form
        The WorkForm to modify.
    id_type
        ORCID's identifier type, e.g. ``"doi"``.
    value
        The identifier itself.
    relationship
        ``"self"`` when the id names this work, ``"part-of"`` when it names its
        container. **ISSN and ISBN must be part-of**: ORCID groups works by
        their `self` ids, so a journal's ISSN marked `self` collapses every
        article in that journal into one group and later ones are refused as
        duplicates.
    """
    wanted = zc.normalize_identifier(id_type, value)
    existing = _external_ids(form)
    for eid in existing:
        same_type = ((eid.get("externalIdentifierType") or {}).get("value") or "").lower()
        same_value = (eid.get("externalIdentifierId") or {}).get("value")
        if same_type == id_type.lower() and \
                zc.normalize_identifier(id_type, same_value) == wanted:
            return
    form["workExternalIdentifiers"] = existing + [{
        "externalIdentifierId": _text(value),
        "externalIdentifierType": _text(id_type),
        "relationship": _text(relationship),
        "url": _text(""),
    }]


def set_date(form: dict, z: dict) -> None:
    """Write the publication date Zotero knows, keeping what it does not.

    Only components Zotero actually holds are written. Zotero records a bare
    year for most of this library while ORCID often carries a full Crossref
    date, so overwriting wholesale would delete a known month and day from most
    of the record — a loss, not a sync.

    ORCID's ``Date`` form object holds plain zero-padded strings, not wrapped
    values: the one exception to :func:`_text` in a WorkForm.

    Parameters
    ----------
    form
        The WorkForm to modify, in place.
    z
        One record from :func:`zotero_common.zotero_records`.
    """
    date = dict(form.get("publicationDate") or {})
    date.setdefault("year", None)
    date.setdefault("month", None)
    date.setdefault("day", None)
    if z.get("year"):
        date["year"] = str(z["year"])
    if z.get("month"):
        date["month"] = f"{z['month']:02d}"
    if z.get("day"):
        date["day"] = f"{z['day']:02d}"
    form["publicationDate"] = date


def is_self(name: str) -> bool:
    """Whether a credit name is the record holder's own.

    Zotero spells it several ways ("A. Anjos", "A.R. Anjos", "Andre Anjos");
    :func:`zotero_common.normalize_author_name` folds them all to one form, so
    comparing against that form catches every variant.

    Parameters
    ----------
    name
        A credit name.

    Returns
    -------
    bool
        True when this contributor is the owner of the ORCID record.
    """
    return zc.normalize_author_name(name) == zc.SELF_NAME


def contributor(name: str) -> dict:
    """One ORCID work contributor, from a Zotero creator's name.

    ``contributorSequence`` is deliberately omitted: it is optional, the list's
    own order already carries authorship order, and leaving it out avoids
    guessing a second enum value on ORCID's undocumented frontend endpoint.
    The role is lowercase, which is what ORCID's own frontend sends.

    Parameters
    ----------
    name
        The credit name, already folded by
        :func:`zotero_common.normalize_author_name`.

    Returns
    -------
    dict
        The contributor in WorkForm shape.
    """
    form = {
        "creditName": _text(name),
        "contributorRole": _text("author"),
    }
    if is_self(name):
        form["orcid"] = _text(zc.ORCID_ID)
        form["uri"] = _text(f"{BASE}/{zc.ORCID_ID}")
    return form


def contributor_grouped(name: str) -> dict:
    """One contributor in ORCID's *grouped* shape — the one the UI renders.

    ORCID keeps two contributor representations on a WorkForm and they are not
    interchangeable. ``contributors`` is what the public v3.0 API serves;
    ``contributorsGroupedByOrcid`` is what the record page displays, and what
    ``toWork()`` applies last and therefore lets win. Writing only the flat list
    stores names the API reports but the Contributors panel leaves blank.

    Note the credit name is ``{"content": ...}`` here, not the ``{"value": ...}``
    of :func:`_text` — a different model class, not a Text wrapper.

    Parameters
    ----------
    name
        The credit name.

    Returns
    -------
    dict
        The contributor in grouped shape, matching what ORCID itself emits.
    """
    if is_self(name):
        # What ORCID's "Add yourself as a contributor" button produces: the
        # contributor is linked to the profile rather than being a loose name.
        # Copied from a real linked entry on this record, `host` included.
        orcid = {"uri": f"{BASE}/{zc.ORCID_ID}", "path": zc.ORCID_ID, "host": None}
    else:
        orcid = {"uri": None, "path": None, "host": None}
    return {
        "contributorOrcid": orcid,
        "creditName": {"content": name},
        "contributorEmail": None,
        "contributorAttributes": None,
        "rolesAndSequences": [
            {"contributorSequence": None, "contributorRole": "author"},
        ],
    }


def set_contributors(form: dict, names: list[str]) -> None:
    """Write an author list into *both* of a WorkForm's contributor fields.

    Setting one and not the other is what made updates appear to work over the
    API while the record page stayed empty. Both are written from the same
    names, so whichever the server applies last gives the same result.

    Parameters
    ----------
    form
        The WorkForm to modify, in place.
    names
        Credit names, in order.
    """
    form["contributors"] = [contributor(n) for n in names]
    form["contributorsGroupedByOrcid"] = [contributor_grouped(n) for n in names]
    form["numberOfContributors"] = len(names)


def set_citation(form: dict, bibtex: str | None) -> None:
    """Put a BibTeX citation on a WorkForm, in place.

    ORCID's Citation is two Text fields, and the type is the lowercase
    ``"bibtex"`` of its controlled vocabulary. This is the field grant systems
    read to ingest a publication, which is why it carries Zotero's own export
    rather than anything reconstructed here.

    Parameters
    ----------
    form
        The WorkForm to modify.
    bibtex
        The cleaned entry, or None to leave the citation untouched.
    """
    if not bibtex:
        return
    form["citation"] = {
        "citation": _text(bibtex),
        "citationType": _text("bibtex"),
    }


#: The only contributor roles `POST /works/work.json` accepts. ORCID also stores
#: CRediT roles ("writing - original draft", "conceptualization", …) from a
#: separate vocabulary, and the save endpoint answers HTTP 500 — an HTML error
#: page, not a field error — when one comes back in a form it is given.
LEGACY_CONTRIBUTOR_ROLES = frozenset((
    "assignee", "author", "chair-or-translator", "co-inventor",
    "co-investigator", "editor", "graduate-student", "other-inventor",
    "postdoctoral-researcher", "principal-investigator", "support-staff",
))


def sanitize_contributors(form: dict) -> bool:
    """Bring a fetched form's contributor roles back into postable range.

    Read-modify-write means ORCID's own stored contributors travel back to it
    untouched — and a work carrying a CRediT role then cannot be saved at all,
    whatever the edit was actually about. Names, order and profile links are
    kept; only out-of-range roles become ``author``, which is what this record's
    Zotero-sourced authorship says anyway.

    Parameters
    ----------
    form
        The WorkForm to modify, in place.

    Returns
    -------
    bool
        True when something was rewritten, so callers can mention it.
    """
    grouped = form.get("contributorsGroupedByOrcid") or []
    changed = False
    for entry in grouped:
        for role in entry.get("rolesAndSequences") or []:
            current = (role.get("contributorRole") or "").strip().lower()
            if current and current not in LEGACY_CONTRIBUTOR_ROLES:
                role["contributorRole"] = "author"
                changed = True
    return changed


def new_form(z: dict) -> dict:
    """A WorkForm for a Zotero record that ORCID does not have yet.

    Carries what Zotero knows: title, type, venue, year, URL, DOI and the author
    list. The names are credit names only — Zotero does not hold co-authors'
    ORCID iDs, so ORCID matches them by name as it does for any manual entry.

    Parameters
    ----------
    z
        One record from :func:`zotero_common.zotero_records`.

    Returns
    -------
    dict
        A WorkForm ready to POST, with no put-code (which is what makes it a
        create rather than an update).
    """
    form: dict = {
        "putCode": None,
        "title": _text(z["title"]),
        "subtitle": _text(None),
        "journalTitle": _text(z["container"]),
        "workType": _text(z["orcid_type"]),
        "workExternalIdentifiers": [],
        "url": _text(z["pdf"] or z["url"]),
        "shortDescription": _text(None),
        "languageCode": _text(z.get("language")),
        "visibility": {"visibility": "PUBLIC"},
    }
    set_contributors(form, z.get("authors") or [])
    set_date(form, z)
    set_citation(form, z.get("bibtex"))
    for ident in z.get("identifiers") or []:
        add_external_id(form, ident["type"], ident["value"], ident["relationship"])
    return form


def patch_form(current: dict, z: dict, diffs: list[tuple[str, str, str]]) -> dict:
    """Apply only the flagged differences to a work's *current* ORCID form.

    Read-modify-write is the whole point: ``POST /works/work.json`` replaces the
    work outright, so building a fresh form for an update would silently discard
    the contributors, abstract and identifiers that the diff does not model.

    Parameters
    ----------
    current
        The work's existing WorkForm, as fetched from ORCID.
    z
        The Zotero record it matched.
    diffs
        Rows from :func:`zotero_common.field_diffs`.

    Returns
    -------
    dict
        A copy of *current* with the flagged fields updated.

    Raises
    ------
    ValueError
        If a diff names a field with no patch rule. That means
        :func:`zotero_common.field_diffs` grew a row this tool cannot apply, and
        failing loudly is the point — a silent skip would report success while
        leaving ORCID stale.
    """
    form = copy.deepcopy(current)
    # Do this before anything else: an unpostable role anywhere in the fetched
    # form makes the whole save fail, however unrelated the actual edit is.
    sanitize_contributors(form)
    for field, _has, _want in diffs:
        if field == "identifier":
            for ident in zc.missing_identifiers(z, {"identifiers": _current_ids(form)}):
                add_external_id(form, ident["type"], ident["value"],
                                ident["relationship"])
        elif field == "URL (public PDF)":
            form["url"] = _text(z["pdf"])
        elif field == "work-type":
            form["workType"] = _text(z["orcid_type"])
        elif field == "venue":
            form["journalTitle"] = _text(z["container"])
        elif field == "date":
            set_date(form, z)
        elif field == "authors":
            # Replaced wholesale, not merged: Zotero is ground truth for both
            # the names and their order, and a merge could not express a
            # reordering or a removal.
            set_contributors(form, z["authors"])
        elif field == "profile link":
            set_contributors(form, z["authors"])
        elif field == "citation":
            set_citation(form, z["bibtex"])
        elif field == "language":
            form["languageCode"] = _text(z["language"])
        else:
            raise ValueError(
                f"no patch rule for diff field {field!r} — add one here when "
                "zotero_common.field_diffs grows a row"
            )
    return form


def plan_actions(diff: dict) -> tuple[list[dict], list[str]]:
    """Turn a difference into an ordered list of writes, plus what was skipped.

    Parameters
    ----------
    diff
        The mapping from :func:`zotero_common.diff_against_orcid`.

    Returns
    -------
    tuple
        ``(actions, skipped)``. Each action is ``{"kind", "label", "zrec"}``
        plus ``"putcode"`` and ``"diffs"`` for an edit. *skipped* holds
        human-readable reasons for works that cannot be written.
    """
    actions: list[dict] = []
    skipped: list[str] = []

    for z in sorted(diff["missing"], key=lambda x: (x["year"] or 0), reverse=True):
        actions.append({"kind": "add", "label": z["title"], "zrec": z})

    for z, o, diffs in sorted(diff["outdated"], key=lambda x: (x[0]["year"] or 0), reverse=True):
        if not o.get("ours"):
            fields = ", ".join(f for f, _h, _w in diffs)
            skipped.append(
                f"{z['title'][:60]} — asserted by another source, not editable "
                f"by you ({fields})"
            )
            continue
        actions.append({
            "kind": "edit",
            "label": z["title"],
            "zrec": z,
            "putcode": o["putcode"],
            "diffs": diffs,
        })

    return actions, skipped


# --------------------------------------------------------------------------
# The browser session
# --------------------------------------------------------------------------

def _launch(pw, profile_dir: pathlib.Path, headless: bool):
    """Open the persistent profile, preferring an installed Chrome.

    Using the system Chrome channel avoids Playwright's ~400 MB bundled-browser
    download; the bundled Chromium is the fallback when Chrome is absent.

    ``chromium_sandbox=True`` is not the Playwright default — it passes
    ``--no-sandbox``, which makes Chrome show its "unsupported command-line
    flag" warning bar. That default suits throwaway CI containers; here a human
    types real credentials into this window, so the OS sandbox stays on.
    """
    profile_dir.mkdir(parents=True, exist_ok=True)
    for channel in ("chrome", None):
        try:
            return pw.chromium.launch_persistent_context(
                str(profile_dir), headless=headless, channel=channel,
                chromium_sandbox=True,
            )
        except Exception:  # noqa: BLE001 — missing channel; try the bundled build
            continue
    raise RuntimeError(
        "could not launch a browser. Install Google Chrome, or run "
        "`playwright install chromium`."
    )


def load_cookies(ctx, path: pathlib.Path = COOKIE_FILE) -> bool:
    """Restore a previously saved session into a fresh browser context.

    Parameters
    ----------
    ctx
        A browser context.
    path
        The saved cookie jar.

    Returns
    -------
    bool
        True when cookies were restored; False when there were none to restore
        or the file was unreadable, which is not an error — it just means
        signing in again.
    """
    if not path.exists():
        return False
    try:
        ctx.add_cookies(json.loads(path.read_text()))
        return True
    except Exception:  # noqa: BLE001 — a corrupt jar just means a fresh login
        return False


def save_cookies(ctx, path: pathlib.Path = COOKIE_FILE) -> None:
    """Persist the current session so the next run does not need a fresh login.

    The file is created 0600 *before* anything is written to it: it holds a live
    ORCID session, which is as good as the password for the duration.

    Parameters
    ----------
    ctx
        A signed-in browser context.
    path
        Where to write the cookie jar.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    path.touch(mode=0o600, exist_ok=True)
    path.chmod(0o600)
    path.write_text(json.dumps(ctx.cookies(), indent=1))


def signed_in(ctx) -> bool:
    """Whether this browser context holds a signed-in ORCID session.

    Asks the server. The obvious alternative — navigate to /my-orcid and look at
    the URL — is a race: ORCID is an Angular app that decides authentication
    client-side, so the URL still reads ``/my-orcid`` for seconds after
    ``domcontentloaded`` and only then becomes ``/signin``. Reading it too early
    reports a signed-out session as signed in, and the run then fails on its
    first write with a misleading "session has lapsed".

    This also probes the same cookie jar the writes use, rather than a proxy for
    it.

    Parameters
    ----------
    ctx
        A browser context.

    Returns
    -------
    bool
        True only when ORCID reports an authenticated session.
    """
    try:
        r = ctx.request.get(STATUS_ENDPOINT)
        return bool(r.ok and r.json().get("loggedIn"))
    except Exception:  # noqa: BLE001 — an unreadable probe is not a session
        return False


def _ensure_signed_in(ctx, timeout: float = 300.0) -> None:
    """Block until the context holds a signed-in ORCID session.

    Never types credentials: it opens the sign-in page and polls until the human
    has finished, which also covers two-factor auth and any Cloudflare challenge
    without knowing anything about either.

    Parameters
    ----------
    ctx
        A browser context.
    timeout
        Seconds to wait for the sign-in to complete.

    Raises
    ------
    RuntimeError
        If no session appears within *timeout*.
    """
    if signed_in(ctx):
        return

    page = ctx.pages[0] if ctx.pages else ctx.new_page()
    page.goto(f"{BASE}/signin", wait_until="domcontentloaded")
    print("→ Not signed in. Sign in to ORCID in the browser window that just "
          "opened; this continues by itself once you are through.", file=sys.stderr)

    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        page.wait_for_timeout(2000)
        if signed_in(ctx):
            print("→ Signed in.", file=sys.stderr)
            return
    raise RuntimeError(f"no ORCID session after {timeout:.0f}s waiting for sign-in")


def _csrf(ctx) -> str:
    """Fetch and return the XSRF token the frontend echoes on every write."""
    ctx.request.get(CSRF_ENDPOINT)
    for cookie in ctx.cookies(BASE):
        if cookie["name"] == XSRF_COOKIE:
            return cookie["value"]
    raise RuntimeError(f"no {XSRF_COOKIE} cookie after calling {CSRF_ENDPOINT}")


@contextlib.contextmanager
def session(profile_dir: pathlib.Path, headless: bool | None = None):
    """A signed-in ORCID browser context, as a context manager.

    Parameters
    ----------
    profile_dir
        The persistent Playwright profile directory holding the session.
    headless
        ``None`` (the default) decides: it starts headless, and only opens a
        visible window if the saved session has lapsed and a human has to sign
        in. ``True`` forbids that window and fails instead — a signed-out
        headless run can never succeed, so it says so at once rather than
        waiting out the sign-in timeout. ``False`` always shows the window.

    Yields
    ------
    tuple
        ``(context, csrf_token)`` ready for :func:`post_work`.

    Raises
    ------
    RuntimeError
        If *headless* is True and the saved session is no longer valid.
    """
    try:
        from playwright.sync_api import sync_playwright
    except ImportError as exc:  # pragma: no cover - dependency guard
        raise RuntimeError(
            "playwright is not installed; run `pixi install`"
        ) from exc

    with sync_playwright() as pw:
        ctx = _launch(pw, profile_dir, headless is not False)
        try:
            load_cookies(ctx)
            if not signed_in(ctx):
                if headless:
                    raise RuntimeError(
                        "the saved ORCID session has lapsed, and signing in needs "
                        "a visible browser. Re-run without --headless once; the "
                        "session is then reused for weeks."
                    )
                # Playwright cannot un-hide a running context, so swap it for a
                # visible one purely to let the human sign in.
                ctx.close()
                ctx = _launch(pw, profile_dir, headless=False)
                load_cookies(ctx)
                _ensure_signed_in(ctx)
            save_cookies(ctx)
            yield ctx, _csrf(ctx)
        finally:
            with contextlib.suppress(Exception):
                ctx.close()


def _json_or_lapsed(response, what: str) -> dict:
    """Decode a JSON response, naming a lapsed session for what it is.

    ORCID answers an unauthenticated request by redirecting to the sign-in page,
    which arrives as HTTP 200 carrying HTML. Decoding that as JSON fails with an
    error that says nothing about the real cause, so check for it explicitly.

    Parameters
    ----------
    response
        A Playwright ``APIResponse``.
    what
        What was being requested, for the error message.

    Returns
    -------
    dict
        The decoded body.

    Raises
    ------
    RuntimeError
        If the response is the sign-in page rather than JSON.
    """
    content_type = response.headers.get("content-type", "")
    if "/signin" in response.url or "json" not in content_type:
        raise RuntimeError(
            f"{what}: the ORCID session has lapsed — re-run and sign in again"
        )
    return response.json()


def fetch_work_form(ctx, putcode: int | str) -> dict:
    """The current WorkForm for one work, for read-modify-write.

    Parameters
    ----------
    ctx
        A signed-in browser context.
    putcode
        The work's ORCID put-code.

    Returns
    -------
    dict
        The work's full current form.

    Raises
    ------
    RuntimeError
        If ORCID does not return the work.
    """
    r = ctx.request.get(f"{WORK_INFO_ENDPOINT}?workId={putcode}")
    if not r.ok:
        raise RuntimeError(f"GET work {putcode} failed: HTTP {r.status}")
    return _json_or_lapsed(r, f"fetching work {putcode}")


def post_work(ctx, csrf: str, form: dict) -> dict:
    """Create or update one work, and raise on ORCID's field-level errors.

    ORCID answers a rejected write with HTTP 200 and a populated ``errors``
    list rather than an error status, so the body has to be inspected.

    Parameters
    ----------
    ctx
        A signed-in browser context.
    csrf
        The token from :func:`_csrf`.
    form
        The WorkForm to send. A null ``putCode`` creates; a set one updates.

    Returns
    -------
    dict
        The saved work as ORCID echoes it back.

    Raises
    ------
    RuntimeError
        On an HTTP failure or any validation error in the response.
    """
    r = ctx.request.post(
        WORK_ENDPOINT,
        data=form,
        headers={XSRF_HEADER: csrf, "Content-Type": "application/json"},
    )
    if not r.ok:
        raise RuntimeError(f"POST failed: HTTP {r.status} {r.text()[:200]}")
    saved = _json_or_lapsed(r, "saving work")
    errors = collect_errors(saved)
    if errors:
        raise RuntimeError("; ".join(errors))
    return saved


def collect_errors(form: dict) -> list[str]:
    """Every validation error in a returned WorkForm, at any nesting depth.

    ORCID reports errors per field, so a top-level ``errors`` check alone would
    miss a rejected DOI or an invalid date.

    Parameters
    ----------
    form
        A WorkForm as returned by ORCID.

    Returns
    -------
    list of str
        All error messages found, in traversal order.
    """
    found: list[str] = []

    def walk(node: object) -> None:
        if isinstance(node, dict):
            errs = node.get("errors")
            if isinstance(errs, list):
                found.extend(str(e) for e in errs)
            for key, value in node.items():
                if key != "errors":
                    walk(value)
        elif isinstance(node, list):
            for value in node:
                walk(value)

    walk(form)
    return found


# --------------------------------------------------------------------------
# Driver
# --------------------------------------------------------------------------

def render_report(zrecs: list[dict], orcid: list[dict], diff: dict) -> str:
    """The difference as a Markdown to-do list, for reading rather than applying.

    The same three sections this tool has always written, kept because 90-odd
    field-level rows read better in a file than scrolled past in a terminal.

    Parameters
    ----------
    zrecs
        Records from :func:`zotero_common.zotero_records`.
    orcid
        Works from :func:`zotero_common.parse_orcid_works`.
    diff
        The mapping from :func:`zotero_common.diff_against_orcid`.

    Returns
    -------
    str
        The rendered Markdown document.
    """
    missing, outdated, orphan = diff["missing"], diff["outdated"], diff["orphan"]
    lines = ["# ORCID sync report", "",
             f"Zotero works: {len(zrecs)} · ORCID works: {len(orcid)} · "
             f"generated {time.strftime('%Y-%m-%d %H:%M UTC', time.gmtime())}",
             "",
             "Zotero is the source of truth. Apply the items below with "
             "`pixi run orcid-sync --apply`, or by hand on your ORCID record. "
             "Nothing here deletes anything.", ""]

    lines += [f"## 1. Missing on ORCID ({len(missing)})", ""]
    if missing:
        lines += ["| Year | Type | Title | DOI | Public PDF |",
                  "|---|---|---|---|---|"]
        for z in sorted(missing, key=lambda x: (x["year"] or 0), reverse=True):
            lines.append(f"| {z['year'] or '—'} | {z['orcid_type']} | {z['title'][:70]} "
                         f"| {z['doi'] or '—'} | {z['pdf'] or '—'} |")
    else:
        lines.append("_Nothing missing — every Zotero work is on ORCID._")
    lines.append("")

    lines += [f"## 2. Outdated / incomplete on ORCID ({len(outdated)})", ""]
    if outdated:
        lines += ["| Work | Field | ORCID has | Zotero has | Yours? |",
                  "|---|---|---|---|---|"]
        for z, o, diffs in sorted(outdated, key=lambda x: (x[0]["year"] or 0), reverse=True):
            for i, (field, has, want) in enumerate(diffs):
                title = z["title"][:50] if i == 0 else ""
                mine = ("yes" if o.get("ours") else "**no**") if i == 0 else ""
                lines.append(f"| {title} | {field} | {has} | {want} | {mine} |")
        lines += ["", "_A **no** in the last column means another source asserted that "
                      "work; ORCID only lets the creating source edit an item, so the "
                      "sync skips it._"]
    else:
        lines.append("_All matched ORCID works already carry the Zotero metadata._")
    lines.append("")

    lines += [f"## 3. On ORCID, not in Zotero ({len(orphan)}) — review only", ""]
    if orphan:
        lines += ["_Reported, never deleted. Add to Zotero if they belong, or leave as-is._", "",
                  "| Year | Title | DOI |", "|---|---|---|"]
        for o in sorted(orphan, key=lambda x: (x["year"] or 0), reverse=True):
            lines.append(f"| {o['year'] or '—'} | {(o['title'] or '')[:70]} | {o['doi'] or '—'} |")
    else:
        lines.append("_Every ORCID work matches a Zotero work._")
    lines.append("")
    return "\n".join(lines)


def change_details(action: dict) -> list[str]:
    """The field-level lines to print under a work as it is written.

    An update says which fields move and to what, so the log records the change
    rather than only that something changed. An add says what is being sent,
    since there is no prior state to compare against.

    Parameters
    ----------
    action
        One entry from :func:`plan_actions`.

    Returns
    -------
    list of str
        One line per field, already trimmed for terminal width.
    """
    z = action["zrec"]
    if action["kind"] == "edit":
        return [f"{field}: {has} → {want}" for field, has, want in action["diffs"]]

    lines = [f"type: {z['orcid_type']}"]
    for ident in z.get("identifiers") or []:
        lines.append(f"{ident['type']}: {ident['value']} ({ident['relationship']})")
    for label, value in (("venue", z["container"]),
                         ("URL", z["pdf"] or z["url"]),
                         ("date", zc.format_date(z.get("year"), z.get("month"),
                                                 z.get("day"))),
                         ("language", z.get("language")),
                         ("citation", "bibtex" if z.get("bibtex") else None)):
        if value:
            lines.append(f"{label}: {str(value)[:70]}")
    if z.get("authors"):
        lines.append(f"authors: {zc.authors_summary(z['authors'])}")
    return lines


def describe(action: dict) -> str:
    """A one-line human description of a planned write."""
    z = action["zrec"]
    year = z["year"] or "—"
    if action["kind"] == "add":
        return f"  + [{year}] {z['title'][:64]}  ({z['orcid_type']})"
    fields = ", ".join(f"{f}: {w}" for f, _h, w in action["diffs"])
    return f"  ~ [{year}] {z['title'][:64]}\n      {fields}"


def apply_actions(actions: list[dict], delay: float,
                  headless: bool | None = None) -> int:
    """Perform the planned writes against ORCID, paced by *delay*.

    Each work is announced *before* its write, and flushed, so a run that stalls
    on one shows which one rather than going quiet. Failures are reported under
    their line and the run continues — one rejected work must not abandon the
    other ninety.

    Parameters
    ----------
    actions
        The plan from :func:`plan_actions`.
    delay
        Seconds to wait between consecutive writes.
    headless
        Passed straight to :func:`session`.

    Returns
    -------
    int
        A process exit code: 0 when every write succeeded, 1 otherwise.
    """
    total = len(actions)
    width = len(str(total))
    failures = 0
    with session(PROFILE_DIR, headless) as (ctx, csrf):
        for i, action in enumerate(actions):
            if i:
                time.sleep(delay)
            z = action["zrec"]
            verb = "add" if action["kind"] == "add" else "update"
            indent = " " * (width * 2 + 4)
            print(f"[{i + 1:>{width}}/{total}] {verb:<6} [{z['year'] or '—'}] "
                  f"{z['title'][:60]}", flush=True)
            for detail in change_details(action):
                print(f"{indent}{detail}", flush=True)
            try:
                if action["kind"] == "add":
                    post_work(ctx, csrf, new_form(z))
                else:
                    current = fetch_work_form(ctx, action["putcode"])
                    post_work(ctx, csrf, patch_form(current, z, action["diffs"]))
            except Exception as exc:  # noqa: BLE001 — one bad work must not stop the run
                failures += 1
                print(f"{' ' * (width * 2 + 4)}! failed: {exc}", flush=True)

    done = total - failures
    # flush before touching stderr: piped stdout is block-buffered, so without
    # this the failure summary overtakes the line it refers to in a log.
    print(f"\nApplied {done}/{total} change(s).", flush=True)
    if failures:
        print(f"{failures} failed — see above.", file=sys.stderr)
    return 1 if failures else 0


def main() -> int:
    """Parse arguments, compute the difference, and print or apply it."""
    p = argparse.ArgumentParser(
        prog="sync-orcid",
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    mode = p.add_mutually_exclusive_group()
    mode.add_argument("--apply", action="store_true",
                      help="perform the writes (default is a dry-run that writes nothing)")
    mode.add_argument("--report", nargs="?", const=str(DEFAULT_REPORT), metavar="PATH",
                      help=f"write the difference as Markdown instead of listing it "
                           f"(default: {DEFAULT_REPORT.name}). Touches no browser")
    p.add_argument("--limit", type=int, metavar="N",
                   help="apply at most N changes; use --limit 1 for a first live test")
    p.add_argument("--headless", action="store_true",
                   help="never open a browser window; fail if the saved session has "
                        "lapsed. Without it the run is headless anyway and only "
                        "shows a window when you actually need to sign in")
    p.add_argument("--only", choices=("add", "edit"),
                   help="restrict to additions or to updates. Adds are planned first, "
                        "so `--only edit --limit 1` is how to test the riskier "
                        "read-modify-write path on its own")
    p.add_argument("--delay", type=float, default=1.0, metavar="SECONDS",
                   help="pause between consecutive writes (default: 1.0). Writes are "
                        "always serialised; raise this if ORCID starts challenging")
    args = p.parse_args()

    if args.delay < 0:
        p.error("--delay must not be negative")

    user_id = zc.read_user_id()
    try:
        zrecs = zc.zotero_records(user_id)
        zc.attach_bibtex(zrecs, zc.fetch_public_bibtex(user_id))
        orcid = zc.parse_orcid_works(zc.fetch_orcid_works())
        # Contributors and language are absent from the summary feed; without
        # this the diff cannot see them and would never sync either.
        zc.enrich_orcid_works(orcid)
    except Exception as exc:  # noqa: BLE001
        print(f"! fetch failed: {exc}", file=sys.stderr)
        return 1

    diff = zc.diff_against_orcid(zrecs, orcid)

    if args.report:
        path = pathlib.Path(args.report)
        path.write_text(render_report(zrecs, orcid, diff))
        rel = path.relative_to(zc.ROOT) if path.is_relative_to(zc.ROOT) else path
        print(f"Wrote {rel}")
        print(f"  missing on ORCID:      {len(diff['missing'])}")
        print(f"  outdated/incomplete:   {len(diff['outdated'])}")
        print(f"  on ORCID not in Zotero:{len(diff['orphan'])}")
        return 0

    actions, skipped = plan_actions(diff)

    print(f"Zotero works: {len(zrecs)} · ORCID works: {len(orcid)}")
    if args.only:
        actions = [a for a in actions if a["kind"] == args.only]
    if args.limit is not None:
        actions = actions[:args.limit]

    adds = [a for a in actions if a["kind"] == "add"]
    edits = [a for a in actions if a["kind"] == "edit"]
    print(f"\nTo add ({len(adds)}):")
    for a in adds:
        print(describe(a))
    print(f"\nTo update ({len(edits)}):")
    for a in edits:
        print(describe(a))

    no_citation = [z for z in zrecs if z.get("bibtex_skipped")]
    if no_citation:
        print(f"\nNo BibTeX citation ({len(no_citation)}) — these keep whatever "
              "citation ORCID already holds:")
        for z in no_citation:
            print(f"  · {z['title'][:52]}")
            print(f"      skipped because {z['bibtex_skipped']}")

    if skipped:
        print(f"\nSkipped ({len(skipped)}) — not yours to edit:")
        for s in skipped:
            print(f"  ! {s}")
    if diff["orphan"]:
        print(f"\nOn ORCID, not in Zotero ({len(diff['orphan'])}) — never deleted, "
              "review by hand.")

    if not actions:
        print("\nNothing to do — ORCID matches Zotero.")
        return 0

    if not args.apply:
        print(f"\nDry-run: nothing written. Re-run with --apply to perform "
              f"{len(actions)} change(s).")
        return 0

    print(f"\nApplying {len(actions)} change(s), {args.delay}s apart…")
    return apply_actions(actions, args.delay, args.headless or None)


if __name__ == "__main__":
    raise SystemExit(main())
