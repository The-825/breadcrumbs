#!/usr/bin/env python3
"""Preflight: catch the collision before you push, not after.

GitHub has no stacked pull requests. When several branches are open against the
same base at once, nothing tells you they are going to fight until one of them
merges and the rest go stale. By then the cost is already paid: conflicts to
resolve by hand, CI re-runs on every affected branch, and a review queue where
half the diffs no longer apply.

The whole problem is that the information needed to prevent it exists BEFORE
the push. Which files this branch touches is knowable. Which files the other
open branches touch is knowable. Whether this branch is already behind its base
is knowable. Nothing checks any of it at the moment it would be cheap to fix.

This runs at that moment. Five checks, exit 1 if any fails:

  1. behind_base      This branch is behind its base and will merge stale.
  2. overlap          Another open branch touches a file this one touches.
  3. commit_hygiene   A commit message is a placeholder, so history reads as noise.
  4. base_merges      Base has been merged in repeatedly, which usually means
                      the branch has been open too long.
  5. stale_state      A session-state handoff file has not been touched in over
                      a week. A crashed or abandoned session leaves its handoff
                      narrating a present that ended; the next session boots on
                      it as current, which is worse than no handoff at all.

Usage:
    python3 preflight.py --base main
    python3 preflight.py --base main --others others.json
    python3 preflight.py --selftest

`others.json` describes the other open branches, so this stays dependency free
and works with whatever tool you use to list them:

    [{"name": "feature-b", "files": ["src/a.py", "docs/x.md"]}, ...]

Without it, the overlap check reports SKIPPED rather than passing. A check that
cannot run must never look like a check that passed.
"""

import argparse
import json
import os
import re
import subprocess
import sys

# Commit subjects that carry no information. A branch whose history is made of
# these cannot be reviewed commit by commit, which is the thing that makes a
# batched branch readable rather than a dump.
PLACEHOLDER_SUBJECTS = re.compile(
    r"^(wip|fix|fixes|update|updates|changes|stuff|misc|temp|tmp|asdf|test|"
    r"more|cleanup|minor|tweak|tweaks|x|\.)$",
    re.I,
)

# Merging the base branch into a feature branch is normal once. Doing it
# repeatedly means the branch has been open long enough to keep going stale,
# which is the exact condition this tool exists to catch earlier.
BASE_MERGE_LIMIT = 2

# A session-state handoff file older than this many days is treated as an
# abandoned narration rather than a live handoff. Crashed and abandoned
# sessions leave these behind, and the next session boots on them as current.
STALE_STATE_DAYS = 7
# Files that carry the "where we are right now" handoff. Glob-matched from the
# repo root; extend for your own state-file convention.
STATE_FILE_PATTERNS = ("SESSION_STATE.md", "SESSION_STATE_*.md")


def git(*args, cwd=None):
    return subprocess.run(
        ["git", *args], cwd=cwd, capture_output=True, text=True, check=False
    ).stdout.strip()


# ---------------------------------------------------------------- pure checks
# Each takes plain data and returns (name, ok, message). No I/O, so each is
# directly testable and the self-tests need no repository.


def check_behind_base(behind_count, base):
    if behind_count is None:
        return ("behind_base", None, f"could not compare against {base}")
    if behind_count > 0:
        return (
            "behind_base",
            False,
            f"{behind_count} commit(s) behind {base}. Update before pushing, "
            f"or this merges stale and forces a re-run later.",
        )
    return ("behind_base", True, f"up to date with {base}")


def check_overlap(my_files, others):
    """others: [{"name": str, "files": [str]}]"""
    if others is None:
        return (
            "overlap",
            None,
            "no other-branch data supplied, overlap not checked. "
            "Pass --others to enable it.",
        )
    mine = set(my_files)
    hits = []
    for other in others:
        shared = sorted(mine & set(other.get("files", [])))
        if shared:
            hits.append((other.get("name", "?"), shared))
    if hits:
        lines = [
            f"{len(hits)} other open branch(es) touch files this one touches. "
            f"Whichever merges first makes the rest stale:"
        ]
        for name, shared in hits:
            shown = ", ".join(shared[:4])
            more = f" (+{len(shared) - 4} more)" if len(shared) > 4 else ""
            lines.append(f"    {name}: {shown}{more}")
        return ("overlap", False, "\n".join(lines))
    return ("overlap", True, f"no file overlap with {len(others)} other branch(es)")


def check_commit_hygiene(subjects):
    bad = [s for s in subjects if PLACEHOLDER_SUBJECTS.match(s.strip())]
    if bad:
        return (
            "commit_hygiene",
            False,
            f"{len(bad)} commit(s) with a placeholder subject: "
            f"{', '.join(repr(b) for b in bad[:3])}. "
            f"A batched branch is only reviewable if each commit says what it did.",
        )
    return ("commit_hygiene", True, f"{len(subjects)} commit subject(s) are specific")


def check_base_merges(merge_count, base):
    if merge_count > BASE_MERGE_LIMIT:
        return (
            "base_merges",
            False,
            f"{base} merged in {merge_count} times. The branch keeps going stale, "
            f"which usually means it should have shipped smaller or sooner.",
        )
    return ("base_merges", True, f"{merge_count} merge(s) from {base}")


def check_stale_state(state_ages, limit_days=STALE_STATE_DAYS):
    """state_ages: {path: age_in_days} for session-state handoff files, or None.

    A handoff file exists to describe RIGHT NOW. When a session crashes or a
    workstream is abandoned, its state file keeps narrating a present that
    ended weeks ago, and the next session boots on it as if it were current.
    That is worse than no handoff: no file prompts a fresh look, a stale one
    gets believed. This check does not delete anything (state files record
    real work); it names the rot so a human refreshes or retires the file.
    """
    if state_ages is None:
        return (
            "stale_state",
            None,
            "no session-state data supplied, staleness not checked.",
        )
    stale = {p: d for p, d in state_ages.items() if d > limit_days}
    if stale:
        listing = ", ".join(f"{p} ({d}d)" for p, d in sorted(stale.items()))
        return (
            "stale_state",
            False,
            f"{len(stale)} session-state file(s) untouched for over "
            f"{limit_days} days: {listing}. A handoff that describes a dead "
            f"present gets believed by the next session. Refresh it or retire "
            f"it; do not leave it narrating.",
        )
    return ("stale_state", True,
            f"{len(state_ages)} session-state file(s) fresh within {limit_days} days")


def run_checks(behind, base, my_files, others, subjects, merge_count,
               state_ages=None):
    return [
        check_behind_base(behind, base),
        check_overlap(my_files, others),
        check_commit_hygiene(subjects),
        check_base_merges(merge_count, base),
        check_stale_state(state_ages),
    ]


def report(results):
    failed = [r for r in results if r[1] is False]
    skipped = [r for r in results if r[1] is None]
    for name, ok, msg in results:
        mark = "ok  " if ok else ("SKIP" if ok is None else "FAIL")
        print(f"  {mark}  {name}: {msg}")
    print()
    if failed:
        print(f"preflight: {len(failed)} check(s) failed. Fix before pushing.")
        return 1
    if skipped:
        print(f"preflight: clean, but {len(skipped)} check(s) could not run.")
        return 0
    print("preflight: clean.")
    return 0


# ------------------------------------------------------------------ live mode


def gather(base):
    upstream = f"origin/{base}" if git("rev-parse", "--verify", f"origin/{base}") else base
    behind = git("rev-list", "--count", f"HEAD..{upstream}")
    behind = int(behind) if behind.isdigit() else None
    files = [f for f in git("diff", "--name-only", f"{upstream}...HEAD").splitlines() if f]
    subjects = [s for s in git("log", "--format=%s", f"{upstream}..HEAD").splitlines() if s]
    merges = git("log", "--merges", "--format=%s", f"{upstream}..HEAD").splitlines()
    # Match git's quoted merge-subject forms ("Merge branch 'main' ..." /
    # "Merge remote-tracking branch 'origin/main' ..."), not a bare substring:
    # base "main" must not count a merge of a branch named "maintenance".
    base_forms = (f"'{base}'", f"'origin/{base}'")
    merge_count = sum(1 for m in merges if any(f in m for f in base_forms))

    # Session-state staleness: age in days since the file's last commit. Uses
    # git history rather than mtime, because a fresh clone resets every mtime
    # and would report the whole repo as edited today.
    import glob as _glob
    import time as _time
    # Glob from the repo root, not the cwd: run from a subdirectory, a
    # cwd-relative glob finds nothing and the check would report "0 files
    # fresh" as a pass, which is the could-not-run-looking-green failure the
    # module header forbids. No resolvable root -> None -> the check SKIPs.
    toplevel = git("rev-parse", "--show-toplevel")
    if not toplevel:
        return behind, files, subjects, merge_count, None
    state_ages = {}
    for pattern in STATE_FILE_PATTERNS:
        for path in _glob.glob(os.path.join(toplevel, pattern)):
            rel = os.path.relpath(path, toplevel)
            ts = git("log", "-1", "--format=%ct", "--", rel, cwd=toplevel)
            if ts.isdigit():
                state_ages[rel] = int((_time.time() - int(ts)) // 86400)
    return behind, files, subjects, merge_count, state_ages


def selftest():
    checks = []

    def ok(name, cond):
        checks.append((name, cond))

    ok("behind base fails", check_behind_base(3, "main")[1] is False)
    ok("up to date passes", check_behind_base(0, "main")[1] is True)
    ok("uncomparable base SKIPS rather than passing",
       check_behind_base(None, "main")[1] is None)

    others = [{"name": "b", "files": ["a.py", "z.md"]}]
    ok("shared file fails", check_overlap(["a.py"], others)[1] is False)
    ok("disjoint files pass", check_overlap(["q.py"], others)[1] is True)
    ok("missing other-branch data SKIPS, never passes",
       check_overlap(["a.py"], None)[1] is None)
    ok("the failure names the branch",
       "b:" in check_overlap(["a.py"], others)[2])

    ok("placeholder subject fails", check_commit_hygiene(["wip"])[1] is False)
    ok("bare 'fix' fails", check_commit_hygiene(["fix"])[1] is False)
    ok("real subject passes",
       check_commit_hygiene(["fix: guard misses underscored names"])[1] is True)
    ok("case does not rescue a placeholder", check_commit_hygiene(["WIP"])[1] is False)

    ok("repeated base merges fail", check_base_merges(3, "main")[1] is False)
    ok("one base merge passes", check_base_merges(1, "main")[1] is True)

    ok("stale handoff fails", check_stale_state({"SESSION_STATE.md": 30})[1] is False)
    ok("fresh handoff passes", check_stale_state({"SESSION_STATE.md": 2})[1] is True)
    ok("missing state data SKIPS, never passes",
       check_stale_state(None)[1] is None)
    ok("the failure names the file",
       "SESSION_STATE.md" in check_stale_state({"SESSION_STATE.md": 30})[2])
    ok("mixed ages flag only the stale one",
       "OLD.md" in check_stale_state({"OLD.md": 30, "NEW.md": 1})[2]
       and "NEW.md" not in check_stale_state({"OLD.md": 30, "NEW.md": 1})[2])

    results = run_checks(0, "main", ["a.py"], [], ["feat: real"], 0,
                         {"SESSION_STATE.md": 1})
    ok("an all-clean run reports 0", report(results) == 0)

    failed = [n for n, c in checks if not c]
    for name, cond in checks:
        print(f"  {'ok  ' if cond else 'FAIL'} {name}")
    print(f"selftest: {len(checks) - len(failed)}/{len(checks)} passed")
    return 1 if failed else 0


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--base", default="main")
    ap.add_argument("--others", help="JSON file describing other open branches")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()

    if a.selftest:
        return selftest()

    others = None
    if a.others:
        with open(a.others, encoding="utf-8") as fh:
            others = json.load(fh)

    behind, files, subjects, merge_count, state_ages = gather(a.base)
    return report(run_checks(behind, a.base, files, others, subjects,
                             merge_count, state_ages))


if __name__ == "__main__":
    sys.exit(main())
