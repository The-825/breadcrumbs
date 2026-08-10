#!/usr/bin/env python3
"""budget_loans.py: a context-budget raise is a loan, not a ratchet.

ASSUMES a budget manifest somewhere in your repo (a table of always-loaded
files and their line caps; see docs/context-budget.md) and a CI hook that can
run this script with two budget maps. Stdlib only.

The failure this prevents: budgets only ever go up. Each raise is reasonable
in isolation ("this one section will not fit"), nobody ever lowers one, and
two years later the boot surface every session pays for has doubled with no
single decision anyone can point to. The fix is to make a raise cost
something durable: it must file a LOAN record naming why, the trim target it
promises to return to, the trigger that will unblock the trim, and a
reassess date. The loan comes due; it does not expire silently.

Ledger: one JSON object per line in BUDGET_RAISES.jsonl, fields:
  file          the budgeted file's repo path
  baseline      the cap before the raise
  raised_to     the new cap
  when          ISO date of the raise
  why           one sentence; what could not fit and why nothing was evictable
  trim_target   the cap this loan promises to return to (below raised_to)
  trim_trigger  the condition that unblocks the trim
  reassess_on   ISO date the loan must be re-argued or honored by
  status        "open" | "honored" | "re-argued"

Usage:
    python3 budget_loans.py check LEDGER.jsonl [--today YYYY-MM-DD]
        Reports open loans; exit 1 if any is past reassess_on (a due loan
        is a red check, not a reminder).
    python3 budget_loans.py gate LEDGER.jsonl OLD.json NEW.json
        OLD/NEW are {path: cap} maps (base branch vs PR). Exit 1 if any cap
        rose without an OPEN loan record for that file at that raised cap.
    python3 budget_loans.py --selftest
"""
import datetime
import json
import sys


def load_ledger(path):
    rows = []
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            if line.strip():
                rows.append(json.loads(line))
    return rows


def due_loans(rows, today):
    """Open loans whose reassess_on is on or before today."""
    out = []
    for r in rows:
        if r.get("status") != "open":
            continue
        try:
            due = datetime.date.fromisoformat(r.get("reassess_on", ""))
        except ValueError:
            out.append(r)  # unparseable date fails closed: treat as due
            continue
        if due <= today:
            out.append(r)
    return out


def unjustified_raises(rows, old, new):
    """Caps that rose in NEW vs OLD without an open loan covering them."""
    open_by_file = {r["file"]: r for r in rows if r.get("status") == "open"}
    bad = []
    for path, cap in new.items():
        prior = old.get(path)
        if prior is None or cap <= prior:
            continue
        loan = open_by_file.get(path)
        if loan is None or loan.get("raised_to") != cap:
            bad.append(f"{path}: {prior} -> {cap} with no open loan at that cap")
    return bad


def selftest() -> int:
    today = datetime.date(2026, 8, 10)
    rows = [
        {"file": "RULES.md", "baseline": 300, "raised_to": 320,
         "when": "2026-08-01", "why": "w", "trim_target": 300,
         "trim_trigger": "t", "reassess_on": "2026-11-01", "status": "open"},
        {"file": "HANDOFF.md", "baseline": 90, "raised_to": 120,
         "when": "2026-05-01", "why": "w", "trim_target": 90,
         "trim_trigger": "t", "reassess_on": "2026-08-01", "status": "open"},
        {"file": "OLD.md", "baseline": 10, "raised_to": 20,
         "when": "2026-01-01", "why": "w", "trim_target": 10,
         "trim_trigger": "t", "reassess_on": "2026-02-01", "status": "honored"},
    ]
    checks = [
        ("a due open loan is flagged",
         [r["file"] for r in due_loans(rows, today)] == ["HANDOFF.md"]),
        ("an honored loan never comes due",
         all(r["file"] != "OLD.md" for r in due_loans(rows, today))),
        ("an unparseable reassess date fails closed",
         due_loans([{"status": "open", "reassess_on": "soon", "file": "x"}],
                   today) != []),
        ("a covered raise passes the gate",
         unjustified_raises(rows, {"RULES.md": 300}, {"RULES.md": 320}) == []),
        ("an uncovered raise fails the gate",
         unjustified_raises(rows, {"NEW.md": 50}, {"NEW.md": 60}) != []),
        ("a raise past the loaned cap fails the gate",
         unjustified_raises(rows, {"RULES.md": 300}, {"RULES.md": 340}) != []),
        ("a lowered or unchanged cap never needs a loan",
         unjustified_raises([], {"A.md": 100, "B.md": 50},
                            {"A.md": 90, "B.md": 50}) == []),
        ("a brand-new budgeted file needs no loan",
         unjustified_raises([], {}, {"C.md": 40}) == []),
    ]
    failed = [n for n, ok in checks if not ok]
    for n, ok in checks:
        print(f"  {'ok  ' if ok else 'FAIL'}  {n}")
    print(f"selftest: {len(checks) - len(failed)}/{len(checks)} passed")
    return 1 if failed else 0


def main() -> int:
    if "--selftest" in sys.argv:
        return selftest()
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    today = datetime.date.today()
    for a in sys.argv[1:]:
        if a.startswith("--today"):
            today = datetime.date.fromisoformat(a.split("=", 1)[1])
    if not args:
        print(__doc__)
        return 1
    cmd, rest = args[0], args[1:]
    rows = load_ledger(rest[0])
    if cmd == "check":
        due = due_loans(rows, today)
        for r in due:
            print(f"LOAN DUE: {r.get('file')} raised to {r.get('raised_to')} "
                  f"on {r.get('when')}, promised {r.get('trim_target')} by "
                  f"{r.get('reassess_on')}; trigger was: {r.get('trim_trigger')}. "
                  "Trim and mark honored, or re-argue with a new date.")
        n_open = len([r for r in rows if r.get("status") == "open"])
        print(f"budget loans: {n_open} open, {len(due)} due")
        return 1 if due else 0
    if cmd == "gate":
        old = json.loads(open(rest[1], encoding="utf-8").read())
        new = json.loads(open(rest[2], encoding="utf-8").read())
        bad = unjustified_raises(rows, old, new)
        for b in bad:
            print(f"UNJUSTIFIED RAISE: {b}")
        print("budget gate: " + ("FAIL" if bad else "clean"))
        return 1 if bad else 0
    print(f"unknown command {cmd!r}")
    return 1


if __name__ == "__main__":
    sys.exit(main())
