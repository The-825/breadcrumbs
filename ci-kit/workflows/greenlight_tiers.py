#!/usr/bin/env python3
"""greenlight_tiers.py: which PRs still need the human, decided by diff.

ASSUMES the fail-closed automerge in this directory (automerge.yml) and a
GitHub-shaped changed-files list. Adapt SAFE_PREFIXES to your own repo before
copying; the safe set below is this repo's.

The failure this prevents: a blanket approval-label gate scales the operator,
not the system. Past a few PRs a day the label becomes a rubber stamp applied
in batches, which is worse than no gate, because it still LOOKS like review.
Tiering keeps the human decision where a miss actually costs something and
lets CI-proven low-risk changes merge on green alone.

Policy (fail closed, gated unless proven safe):
- AUTO (merge on green, no label): every changed file is additive or a
  modification inside the safe set: pattern essays (docs/), checklists/,
  the top-level README, the decisions ledger, and the SESSION_STATE handoff.
- GATED (label required): everything else. Explicitly always gated: any
  deletion or rename anywhere; workflows; guards; the manifest (kit.json)
  and agent map (llms.txt); CLAUDE.md; templates/ and skills/ (in this repo
  the .md files ARE behavior-bearing product, not prose); any path outside
  the safe set.

The approval label always works as an override in both directions of intent:
applying it merges a gated PR; nothing here merges a draft or a red check.
The gate runs the BASE branch's copy of this file, so a PR editing the
policy cannot loosen the gate on itself.

Usage:
    python3 greenlight_tiers.py --files-json changed_files.json
        exit 0 = AUTO, exit 1 = GATED (reason on stdout)
    python3 greenlight_tiers.py --selftest
"""
import json
import sys

SAFE_PREFIXES = ("docs/", "checklists/")
SAFE_EXACT = ("README.md", "planning/DECISIONS.md", "SESSION_STATE.md")
SAFE_STATUSES = ("added", "modified")


def classify(files):
    """files: list of {filename, status}. Returns (verdict, reason)."""
    if not files:
        return "GATED", "empty changed-files list; fail closed"
    for f in files:
        name = f.get("filename", "")
        status = f.get("status", "")
        if status not in SAFE_STATUSES:
            return "GATED", f"{name}: status {status!r} (deletions and renames always gate)"
        if name in SAFE_EXACT or name.startswith(SAFE_PREFIXES):
            continue
        return "GATED", f"{name}: outside the safe set"
    return "AUTO", f"all {len(files)} changed file(s) in the safe set"


def selftest() -> int:
    cases = [
        ("docs-only modification is AUTO",
         [{"filename": "docs/memory-desk.md", "status": "modified"}], "AUTO"),
        ("checklist addition is AUTO",
         [{"filename": "checklists/new-list.md", "status": "added"}], "AUTO"),
        ("README + decisions ledger is AUTO",
         [{"filename": "README.md", "status": "modified"},
          {"filename": "planning/DECISIONS.md", "status": "modified"}], "AUTO"),
        ("a SESSION_STATE refresh is AUTO",
         [{"filename": "SESSION_STATE.md", "status": "modified"}], "AUTO"),
        ("deleting SESSION_STATE still gates",
         [{"filename": "SESSION_STATE.md", "status": "removed"}], "GATED"),
        ("a doc deletion gates",
         [{"filename": "docs/memory-desk.md", "status": "removed"}], "GATED"),
        ("a doc rename gates",
         [{"filename": "docs/renamed.md", "status": "renamed"}], "GATED"),
        ("a workflow change gates",
         [{"filename": ".github/workflows/automerge.yml", "status": "modified"}], "GATED"),
        ("a template change gates (behavior-bearing md)",
         [{"filename": "templates/CLAUDE_TEMPLATE.md", "status": "modified"}], "GATED"),
        ("kit.json gates",
         [{"filename": "kit.json", "status": "modified"}], "GATED"),
        ("one gated file gates the whole PR",
         [{"filename": "docs/a.md", "status": "modified"},
          {"filename": "ci-kit/guards/g.py", "status": "modified"}], "GATED"),
        ("an empty list fails closed",
         [], "GATED"),
    ]
    failed = 0
    for name, files, want in cases:
        got, _ = classify(files)
        ok = got == want
        failed += 0 if ok else 1
        print(f"  {'ok  ' if ok else 'FAIL'}  {name}")
    print(f"selftest: {len(cases) - failed}/{len(cases)} passed")
    return 1 if failed else 0


def main() -> int:
    if "--selftest" in sys.argv:
        return selftest()
    try:
        i = sys.argv.index("--files-json")
        files = json.loads(open(sys.argv[i + 1], encoding="utf-8").read())
    except (ValueError, IndexError, OSError, json.JSONDecodeError) as exc:
        print(f"GATED: unreadable changed-files input ({exc}); fail closed")
        return 1
    verdict, reason = classify(files)
    print(f"{verdict}: {reason}")
    return 0 if verdict == "AUTO" else 1


if __name__ == "__main__":
    sys.exit(main())
