#!/usr/bin/env python3
"""Staleness auditor for a conclusions ledger (a CONCLUSIONS.jsonl file).

Reads a jsonl ledger (base line format: templates/CONCLUSIONS_TEMPLATE.md;
provenance fields: PROVENANCE.md next to this script) and classifies every
entry:

  STALE    the entry's `path` no longer exists in the repo (the file it keys
           on was moved, renamed, or retired; the conclusion needs re-keying
           or an obsoleted_by marker)
  AGING    no `verified` date inside the last AGING_DAYS days: the entry is
           older than the window with no `verified` field, or `verified`
           itself is older than the window
  SPECIAL  path is one of the special values (operations / domain / process);
           skipped, nothing on disk to check
  OK       path exists and the entry is fresh

Separately, every `obsoleted_by` pointer is cross-checked: it must resolve to
the `path` of another entry in the ledger, a special path, or a file that
exists in the repo. Unresolved pointers are reported as chain issues.

Usage:
  python3 conclusions_audit.py                     # audit ./CONCLUSIONS.jsonl
  python3 conclusions_audit.py <ledger.jsonl>      # audit a specific ledger
  ... --root <dir>            # repo root that entry paths resolve against
                              # (default: current directory)
  ... --write-report <path>   # also write the report text to a file
  ... --file-tasks            # print the follow-up tasks a task-filing
                              # integration would file (one per STALE entry,
                              # all AGING batched into one). This is a stub
                              # seam: see file_tasks() to wire your own issue
                              # tracker or task bus.
  ... --selftest              # run the offline fixture tests and exit

Stdlib only, no dependencies. Exit code 0 on a completed audit regardless of
findings (this is a report, not a gate); nonzero only when the ledger cannot
be read or a selftest check fails.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import sys
import tempfile

DEFAULT_LEDGER = "CONCLUSIONS.jsonl"
SPECIAL_PATHS = {"operations", "domain", "process"}
# Re-verification window. An entry with no verified/when date inside this
# many days is flagged AGING: not wrong, just unchecked long enough that a
# session should re-verify before relying on it.
AGING_DAYS = 180


def _parse_date(value):
    try:
        return dt.date.fromisoformat((value or "").strip())
    except (AttributeError, TypeError, ValueError):
        return None


def _verdict_for(path, entry, root, today):
    """Classify one parsed entry. Returns (verdict, note)."""
    if path in SPECIAL_PATHS:
        return "SPECIAL", "special path, skipped"
    if not path or not os.path.exists(os.path.join(root, path)):
        return "STALE", "path not found in repo"
    verified = _parse_date(entry.get("verified"))
    when = _parse_date(entry.get("when"))
    ref = verified or when
    if ref is None:
        return "AGING", "no parseable when/verified date"
    age = (today - ref).days
    if age > AGING_DAYS:
        label = "verified" if verified else "when"
        return "AGING", f"{label} {ref.isoformat()} is {age} days old"
    return "OK", ""


def _chain_issue(entry, known_paths, root):
    """Return a note when the entry's obsoleted_by pointer does not resolve."""
    target = (entry.get("obsoleted_by") or "").strip()
    if not target:
        return ""
    if target in known_paths or target in SPECIAL_PATHS:
        return ""
    if os.path.exists(os.path.join(root, target)):
        return ""
    return f"obsoleted_by does not resolve: {target}"


def classify_entries(lines, root, today):
    """Classify every ledger line.

    Returns (results, malformed): results is a list of dicts
    {line_no, entry, verdict, note, chain_issue}; malformed is a list of
    (line_no, snippet) for lines that are not valid JSON objects.
    """
    parsed = []
    malformed = []
    for line_no, raw in enumerate(lines, start=1):
        raw = raw.strip()
        if not raw:
            continue
        try:
            entry = json.loads(raw)
        except ValueError:
            malformed.append((line_no, raw[:80]))
            continue
        if not isinstance(entry, dict):
            malformed.append((line_no, raw[:80]))
            continue
        parsed.append((line_no, entry))

    known_paths = {(e.get("path") or "").strip() for _, e in parsed}
    results = []
    for line_no, entry in parsed:
        path = (entry.get("path") or "").strip()
        verdict, note = _verdict_for(path, entry, root, today)
        results.append({
            "line_no": line_no,
            "entry": entry,
            "verdict": verdict,
            "note": note,
            "chain_issue": _chain_issue(entry, known_paths, root),
        })
    return results, malformed


def _short_what(entry, limit=110):
    what = (entry.get("what") or "").strip()
    if len(what) > limit:
        what = what[: limit - 3] + "..."
    return what


def build_report(results, malformed, ledger_rel, today):
    groups = {"STALE": [], "AGING": [], "SPECIAL": [], "OK": []}
    for r in results:
        groups[r["verdict"]].append(r)
    chain_issues = [r for r in results if r["chain_issue"]]

    lines = []
    lines.append(f"Conclusions staleness audit ({today.isoformat()})")
    lines.append(
        f"Ledger: {ledger_rel}  entries={len(results)}  "
        f"malformed_lines={len(malformed)}"
    )
    lines.append(
        "Counts: OK={ok}  STALE={stale}  AGING={aging}  "
        "SPECIAL_skipped={special}  chain_issues={chain}".format(
            ok=len(groups["OK"]),
            stale=len(groups["STALE"]),
            aging=len(groups["AGING"]),
            special=len(groups["SPECIAL"]),
            chain=len(chain_issues),
        )
    )

    for verdict, legend in (
        ("STALE", "path no longer exists in the repo"),
        ("AGING", f"no verified date inside {AGING_DAYS} days"),
    ):
        rows = groups[verdict]
        lines.append("")
        lines.append(f"{verdict} ({len(rows)})  [{legend}]")
        if not rows:
            lines.append("  none")
        for r in rows:
            e = r["entry"]
            lines.append(
                f"  line {r['line_no']:>4}  {e.get('path', '?')}  [{r['note']}]"
            )
            lines.append(f"             {_short_what(e)}")

    lines.append("")
    lines.append(f"OBSOLETED_BY chain issues ({len(chain_issues)})")
    if not chain_issues:
        lines.append("  none")
    for r in chain_issues:
        lines.append(
            f"  line {r['line_no']:>4}  {r['entry'].get('path', '?')}  "
            f"[{r['chain_issue']}]"
        )

    lines.append("")
    lines.append(
        f"SPECIAL skipped ({len(groups['SPECIAL'])}) and OK "
        f"({len(groups['OK'])}) entries are not listed individually."
    )
    if malformed:
        lines.append("")
        lines.append(f"Malformed lines ({len(malformed)}):")
        for line_no, snippet in malformed:
            lines.append(f"  line {line_no}: {snippet}")
    return "\n".join(lines) + "\n"


def build_tasks(results):
    """One task per STALE entry; all AGING entries batched into one task."""
    tasks = []
    stale = [r for r in results if r["verdict"] == "STALE"]
    aging = [r for r in results if r["verdict"] == "AGING"]
    for r in stale:
        e = r["entry"]
        tasks.append({
            "task": (
                f"Stale conclusions entry (line {r['line_no']}): path "
                f"'{e.get('path', '')}' no longer exists in the repo"
            ),
            "context": (
                "conclusions_audit.py flagged this entry as STALE. Re-key the "
                "conclusion to the file's new home (append a corrected entry, "
                "mark the old one obsoleted_by) or confirm retirement. "
                f"when={e.get('when', '?')}; what: {_short_what(e, 200)}"
            ),
        })
    if aging:
        listing = "; ".join(
            f"line {r['line_no']} {r['entry'].get('path', '?')} ({r['note']})"
            for r in aging
        )
        tasks.append({
            "task": (
                f"Aging conclusions entries: {len(aging)} entries with no "
                f"verified date inside {AGING_DAYS} days"
            ),
            "context": (
                "conclusions_audit.py flagged these as AGING. Re-verify each "
                "claim against the code or live data and stamp a fresh "
                "'verified' date (see PROVENANCE.md): " + listing
            )[:1800],
        })
    return tasks


def file_tasks(tasks):
    """Stub seam for a task-filing integration.

    As shipped this only prints what would be filed. If your repo has an
    issue tracker CLI or an agent task bus, replace the print loop with the
    real call (one issue per STALE entry, one batched issue for AGING) and
    keep the empty-case early return.
    """
    if not tasks:
        print("file-tasks: nothing to file (no STALE or AGING entries).")
        return
    print(f"file-tasks: no integration wired; would file {len(tasks)} task(s):")
    for t in tasks:
        print(f"  - {t['task']}")


def selftest():
    """Offline fixture checks: stale / aging / ok / special, plus the
    verified-refresh, chain-resolution, and malformed-line paths."""
    today = dt.date(2026, 7, 21)
    with tempfile.TemporaryDirectory() as tmp:
        os.makedirs(os.path.join(tmp, "src"))
        existing = os.path.join("src", "example_module.py")
        with open(os.path.join(tmp, existing), "w", encoding="utf-8") as fh:
            fh.write("# selftest fixture\n")
        fixtures = [
            json.dumps({"path": existing, "when": "2026-07-01",
                        "what": "Fresh fact about an existing file.",
                        "evidence": "PR #1"}),
            json.dumps({"path": "src/retired_module.py",
                        "when": "2026-07-01",
                        "what": "Fact about a file that is gone.",
                        "evidence": "PR #2"}),
            json.dumps({"path": existing, "when": "2025-06-01",
                        "what": "Old fact never re-verified.",
                        "evidence": "PR #3"}),
            json.dumps({"path": "operations", "when": "2024-01-01",
                        "what": "Special-path entry, always skipped.",
                        "evidence": "session"}),
            json.dumps({"path": existing, "when": "2025-01-01",
                        "what": "Old fact re-verified recently.",
                        "evidence": "PR #4", "verified": "2026-07-20"}),
            json.dumps({"path": existing, "when": "2026-07-01",
                        "what": "Entry with a dangling obsoleted_by.",
                        "evidence": "PR #5",
                        "obsoleted_by": "docs/nonexistent_doc.md"}),
            json.dumps({"path": existing, "when": "2026-07-01",
                        "what": "Entry whose obsoleted_by resolves to a ledger path.",
                        "evidence": "PR #6", "obsoleted_by": existing}),
            "{not valid json",
        ]
        results, malformed = classify_entries(fixtures, tmp, today)
        checks = [
            ("ok entry classified OK", results[0]["verdict"] == "OK"),
            ("missing path classified STALE", results[1]["verdict"] == "STALE"),
            ("old unverified classified AGING", results[2]["verdict"] == "AGING"),
            ("special path skipped", results[3]["verdict"] == "SPECIAL"),
            ("verified refresh clears aging", results[4]["verdict"] == "OK"),
            ("dangling obsoleted_by flagged", bool(results[5]["chain_issue"])),
            ("resolvable obsoleted_by passes", not results[6]["chain_issue"]),
            ("malformed line counted", len(malformed) == 1),
        ]
        failed = [name for name, passed in checks if not passed]
        for name, passed in checks:
            print(f"  {'PASS' if passed else 'FAIL'}  {name}")
        if failed:
            print(f"selftest: {len(failed)} check(s) failed.")
            return 1
        print(f"selftest: all {len(checks)} checks passed.")
        return 0


def main(argv=None):
    ap = argparse.ArgumentParser(
        description="Staleness audit for a conclusions jsonl ledger"
    )
    ap.add_argument("ledger", nargs="?", default=DEFAULT_LEDGER,
                    help=f"path to the ledger (default: {DEFAULT_LEDGER})")
    ap.add_argument("--root", default=".", metavar="DIR",
                    help="repo root that entry paths resolve against "
                         "(default: current directory)")
    ap.add_argument("--write-report", metavar="PATH",
                    help="also write the report text to PATH")
    ap.add_argument("--file-tasks", action="store_true",
                    help="print the follow-up tasks a task-filing "
                         "integration would file (stub seam)")
    ap.add_argument("--selftest", action="store_true",
                    help="run offline fixture tests and exit")
    args = ap.parse_args(argv)

    if args.selftest:
        return selftest()

    if not os.path.exists(args.ledger):
        print(f"ERROR: ledger not found at {args.ledger}", file=sys.stderr)
        return 1
    with open(args.ledger, encoding="utf-8") as fh:
        lines = fh.readlines()

    today = dt.date.today()
    results, malformed = classify_entries(lines, args.root, today)
    report = build_report(results, malformed, args.ledger, today)
    sys.stdout.write(report)

    if args.write_report:
        with open(args.write_report, "w", encoding="utf-8") as fh:
            fh.write(report)
        print(f"Report written to {args.write_report}")
    if args.file_tasks:
        file_tasks(build_tasks(results))
    return 0


if __name__ == "__main__":
    sys.exit(main())
