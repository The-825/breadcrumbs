#!/usr/bin/env python3
"""Guard: authority-ledger citations resolve, and the ledger stays parseable.

Validates the authority ledger (one JSON grant per line; schema and lifecycle
in docs/authority-ledger.md, quick reference in
templates/AUTHORITY_LEDGER_TEMPLATE.md) and any `Authority: G-YYYYMMDD-NN`
citations in a PR body against it.

Modes
-----
default    CI mode. Reads the GitHub event payload from GITHUB_EVENT_PATH,
           extracts the PR body, and validates every `Authority:` citation
           against the ledger. A citation to an unknown, expired, or revoked
           grant FAILS the run. Zero citations pass (v1 is non-breaking), and
           events without a PR body (push, workflow_dispatch) pass the
           citation check. Every run ALSO checks ledger integrity: each line
           must parse as JSON with the required fields, a well-formed id, a
           known status, and no duplicate ids. Any integrity error fails the
           run: the guard fails closed on a ledger it cannot fully trust.
--sweep    Report-only: list grants already expired or expiring within
           SWEEP_WINDOW_DAYS. Always exits 0.
--selftest Offline fixtures (no network, no repo state beyond a temp dir)
           covering: valid citation, unknown id, expired, revoked, no
           citations, malformed ledger line.

Usage:
    guard_authority_citations.py [--ledger PATH] [--sweep | --selftest]
Ledger path resolution: --ledger flag, else the AUTHORITY_LEDGER_PATH env
var, else DEFAULT_LEDGER_PATH below (relative to the working directory,
which in CI is the repo root). Exit 1 on violation, 0 if clean.
"""
import argparse
import datetime
import json
import os
import re
import sys

# ---- Configuration: edit for your repo layout --------------------------------
DEFAULT_LEDGER_PATH = "AUTHORITY_LEDGER.jsonl"  # where your ledger lives
SWEEP_WINDOW_DAYS = 14                          # --sweep look-ahead for expiring grants
# -------------------------------------------------------------------------------

CITATION_RE = re.compile(r"Authority:\s*(G-\d{8}-\d{2})")
ID_RE = re.compile(r"^G-\d{8}-\d{2}$")
REQUIRED_FIELDS = ("id", "date", "scope", "source", "status", "issued_to")
VALID_STATUSES = ("active", "expired", "revoked")


def load_ledger(path):
    """Parse the ledger. Returns (grants_by_id, error_strings)."""
    grants, errors = {}, []
    if not os.path.exists(path):
        errors.append("ledger file missing: %s" % path)
        return grants, errors
    with open(path, encoding="utf-8") as fh:
        for lineno, raw in enumerate(fh, 1):
            line = raw.strip()
            if not line:
                continue
            try:
                entry = json.loads(line)
            except json.JSONDecodeError as exc:
                errors.append("line %d: not valid JSON (%s)" % (lineno, exc))
                continue
            if not isinstance(entry, dict):
                errors.append("line %d: not a JSON object" % lineno)
                continue
            missing = [f for f in REQUIRED_FIELDS if not entry.get(f)]
            if missing:
                errors.append(
                    "line %d: missing required fields %s" % (lineno, missing)
                )
                continue
            gid = entry["id"]
            if not ID_RE.match(gid):
                errors.append("line %d: bad id format %r" % (lineno, gid))
                continue
            if entry["status"] not in VALID_STATUSES:
                errors.append(
                    "line %d: bad status %r (must be one of %s)"
                    % (lineno, entry["status"], "/".join(VALID_STATUSES))
                )
                continue
            if gid in grants:
                errors.append("line %d: duplicate id %s" % (lineno, gid))
                continue
            grants[gid] = entry
    return grants, errors


def effective_status(entry, today):
    """Grant status with expiry applied: active past expiry counts expired."""
    status = entry["status"]
    expiry = entry.get("expiry")
    if status == "active" and expiry:
        try:
            if datetime.date.fromisoformat(expiry) < today:
                return "expired"
        except ValueError:
            return "expired"  # unparseable expiry fails safe
    return status


def check_citations(body, grants, today):
    """Returns (cited_ids, failure_strings) for a PR body."""
    failures = []
    cited = CITATION_RE.findall(body or "")
    for gid in cited:
        entry = grants.get(gid)
        if entry is None:
            failures.append("cited grant %s not found in the ledger" % gid)
            continue
        status = effective_status(entry, today)
        if status != "active":
            failures.append("cited grant %s is %s" % (gid, status))
    return cited, failures


def evaluate(ledger_path, body, today):
    """Core check, testable offline.

    body None means "no PR body in this event" (citation check skipped).
    Returns (ok, cited_ids, message_strings). Ledger integrity errors always
    make ok False; citation failures make ok False when a body is present.
    """
    grants, errors = load_ledger(ledger_path)
    messages = ["ledger integrity: %s" % e for e in errors]
    cited = []
    if body is not None:
        cited, failures = check_citations(body, grants, today)
        messages.extend("citation: %s" % f for f in failures)
    ok = not messages
    return ok, cited, messages


def pr_body_from_event():
    """PR body from GITHUB_EVENT_PATH, or None when the event has none."""
    event_path = os.environ.get("GITHUB_EVENT_PATH")
    if not event_path or not os.path.exists(event_path):
        return None
    try:
        with open(event_path, encoding="utf-8") as fh:
            event = json.load(fh)
    except (OSError, json.JSONDecodeError):
        return None
    pull_request = event.get("pull_request")
    if not isinstance(pull_request, dict):
        return None
    return pull_request.get("body")


def run_ci(ledger_path):
    today = datetime.date.today()
    body = pr_body_from_event()
    ok, cited, messages = evaluate(ledger_path, body, today)
    for msg in messages:
        print("::error::%s" % msg)
    if body is None:
        print("No PR body in this event; citation check skipped.")
    elif not cited:
        print("No Authority citations in the PR body; pass (v1 non-breaking).")
    elif ok:
        print("All %d Authority citation(s) valid: %s" % (len(cited), ", ".join(cited)))
    if ok:
        grants, _ = load_ledger(ledger_path)
        print("Ledger integrity OK (%d grants)." % len(grants))
    return 0 if ok else 1


def run_sweep(ledger_path):
    today = datetime.date.today()
    grants, errors = load_ledger(ledger_path)
    for err in errors:
        print("ledger integrity: %s" % err)
    horizon = today + datetime.timedelta(days=SWEEP_WINDOW_DAYS)
    flagged = 0
    for gid in sorted(grants):
        entry = grants[gid]
        status = effective_status(entry, today)
        expiry = entry.get("expiry")
        if status == "expired":
            print("EXPIRED   %s (expiry %s) %s" % (gid, expiry, entry["scope"][:80]))
            flagged += 1
        elif status == "active" and expiry:
            try:
                exp_date = datetime.date.fromisoformat(expiry)
            except ValueError:
                continue  # already reported as expired by effective_status
            if today <= exp_date <= horizon:
                print("EXPIRING  %s on %s %s" % (gid, expiry, entry["scope"][:80]))
                flagged += 1
    if not flagged:
        print(
            "No grants expired or expiring within %d days (%d grants checked)."
            % (SWEEP_WINDOW_DAYS, len(grants))
        )
    return 0


def run_selftest():
    import tempfile

    today = datetime.date(2026, 7, 21)
    good_ledger = "\n".join(
        [
            json.dumps(
                {
                    "id": "G-20260101-01",
                    "date": "2026-01-01",
                    "scope": "active standing grant",
                    "wording": None,
                    "source": "selftest fixture",
                    "expiry": None,
                    "status": "active",
                    "issued_to": "selftest",
                    "notes": "",
                }
            ),
            json.dumps(
                {
                    "id": "G-20250101-01",
                    "date": "2025-01-01",
                    "scope": "active grant whose expiry has passed",
                    "wording": None,
                    "source": "selftest fixture",
                    "expiry": "2025-06-01",
                    "status": "active",
                    "issued_to": "selftest",
                    "notes": "",
                }
            ),
            json.dumps(
                {
                    "id": "G-20240101-01",
                    "date": "2024-01-01",
                    "scope": "revoked grant",
                    "wording": None,
                    "source": "selftest fixture",
                    "expiry": None,
                    "status": "revoked",
                    "issued_to": "selftest",
                    "notes": "",
                }
            ),
        ]
    ) + "\n"

    failures = []

    def case(name, ledger_text, body, expect_ok):
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "ledger.jsonl")
            with open(path, "w", encoding="utf-8") as fh:
                fh.write(ledger_text)
            ok, _, messages = evaluate(path, body, today)
        verdict = "PASS" if ok == expect_ok else "FAIL"
        if ok != expect_ok:
            failures.append(name)
        print(
            "%s %-28s ok=%-5s expected ok=%-5s %s"
            % (verdict, name, ok, expect_ok, "; ".join(messages) or "-")
        )

    case("valid citation", good_ledger, "Body\nAuthority: G-20260101-01\n", True)
    case("unknown id", good_ledger, "Authority: G-19990101-99", False)
    case("expired citation", good_ledger, "Authority: G-20250101-01", False)
    case("revoked citation", good_ledger, "Authority: G-20240101-01", False)
    case("no citations", good_ledger, "A PR body with no citations.", True)
    case(
        "malformed ledger line",
        good_ledger + "{not json}\n",
        None,
        False,
    )

    if failures:
        print("SELFTEST FAILED: %s" % ", ".join(failures))
        return 1
    print("SELFTEST OK (6 cases).")
    return 0


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--ledger",
        default=None,
        help="ledger path (default: $AUTHORITY_LEDGER_PATH, else %s)"
        % DEFAULT_LEDGER_PATH,
    )
    parser.add_argument(
        "--sweep",
        action="store_true",
        help="report grants expired or expiring within %d days (exit 0)"
        % SWEEP_WINDOW_DAYS,
    )
    parser.add_argument(
        "--selftest", action="store_true", help="run offline fixture checks"
    )
    args = parser.parse_args()
    ledger_path = args.ledger or os.environ.get(
        "AUTHORITY_LEDGER_PATH", DEFAULT_LEDGER_PATH
    )
    if args.selftest:
        return run_selftest()
    if args.sweep:
        return run_sweep(ledger_path)
    return run_ci(ledger_path)


if __name__ == "__main__":
    sys.exit(main())
