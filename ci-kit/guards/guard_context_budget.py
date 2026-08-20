#!/usr/bin/env python3
"""Guard: every boot-set file stays inside the line budget its manifest declares.

The failure this prevents: the rules file, the handoff file, and the machine
index are attached to every session on every turn, so they are the one line item
no task can opt out of. They grow one well-meaning paragraph at a time, nobody
notices, and six months later sessions spend more of their window on boilerplate
than on work. A budget only stops that if something fails the build; a budget
table nobody parses is a wish.

Reads a markdown manifest table (the shape in docs/context-budget.md), counts
lines in each listed file, and fails when any file exceeds its budget. The table
is the single source of truth for the numbers, so nothing else in the repo
restates them.

Manifest shape. Any markdown table with a header row naming a path column and a
`budget_lines` column. Extra columns are ignored, so Class and Notes ride along:

    | File | Class | budget_lines | Notes |
    |---|---|---:|---|
    | `CLAUDE.md` | kernel | 500 | Binding rules only |

Backticks around the path are optional. A budget cell that is not a bare integer
is a manifest defect and fails the run: the guard fails closed on a table it
cannot fully parse, rather than silently skipping the row it could not read.

Modes
-----
default    Enforce. Every over-budget file fails the run, all reported in one
           pass. A file listed in the manifest but missing on disk also fails,
           since a budget pointing at nothing is stale.
--report   Report-only. Prints the same table with headroom per file and always
           exits 0. Use it to find the ratchet targets: a file well under its
           budget after a restructure is headroom that will get spent.
--selftest Offline fixtures in a temp dir: under budget, over budget, exactly at
           budget, missing file, unparseable budget cell, no table found.

Usage:
    guard_context_budget.py [--manifest PATH] [--root PATH] [--report | --selftest]

Manifest path resolution: --manifest, else the CONTEXT_BUDGET_MANIFEST env var,
else DEFAULT_MANIFEST_PATH below. Paths in the table resolve against --root
(default: the working directory, which in CI is the repo root).
Exit 1 on violation, 0 if clean.
"""
import argparse
import os
import re
import sys
import tempfile

# ---- Configuration: edit for your repo layout --------------------------------
DEFAULT_MANIFEST_PATH = "CONTEXT_BUDGET.md"    # the file holding the budget table
BUDGET_COLUMN = "budget_lines"                    # header cell naming the budget
PATH_COLUMN = "file"                              # header cell naming the path
# -------------------------------------------------------------------------------

ROW_RE = re.compile(r"^\s*\|(.+)\|\s*$")
SEPARATOR_RE = re.compile(r"^[\s|:-]+$")
INT_RE = re.compile(r"^\d+$")


def split_row(line):
    """Split a markdown table row into stripped cells."""
    m = ROW_RE.match(line)
    if not m:
        return None
    return [c.strip() for c in m.group(1).split("|")]


def parse_manifest(text):
    """Find the budget table and parse it.

    Returns (entries, defects). An entry is (path, budget, lineno). The first
    table carrying both a path column and a budget column wins; a repo with two
    budget tables has a source-of-truth problem the guard should not paper over,
    so the second one is reported as a defect.
    """
    entries, defects = [], []
    lines = text.splitlines()
    header_idx = None
    path_col = budget_col = None

    for i, line in enumerate(lines):
        cells = split_row(line)
        if not cells:
            continue
        lowered = [c.strip("`* ").lower() for c in cells]
        if BUDGET_COLUMN in lowered and PATH_COLUMN in lowered:
            if header_idx is not None:
                defects.append(
                    "line %d: a second budget table. The numbers live in exactly "
                    "one place or they are not a source of truth." % (i + 1)
                )
                continue
            header_idx = i
            path_col = lowered.index(PATH_COLUMN)
            budget_col = lowered.index(BUDGET_COLUMN)

    if header_idx is None:
        defects.append(
            "no budget table found: need a markdown table with '%s' and '%s' "
            "header cells" % (PATH_COLUMN, BUDGET_COLUMN)
        )
        return entries, defects

    for i in range(header_idx + 1, len(lines)):
        line = lines[i]
        cells = split_row(line)
        if not cells:
            if entries:
                break  # table ended
            continue
        if SEPARATOR_RE.match(line.replace("|", "")):
            continue
        if max(path_col, budget_col) >= len(cells):
            defects.append("line %d: row has fewer columns than the header" % (i + 1))
            continue
        path = cells[path_col].strip("`").strip()
        budget = cells[budget_col].strip("`").strip()
        if not path:
            continue
        if not INT_RE.match(budget):
            defects.append(
                "line %d: budget for %s is %r, not a bare integer. Commentary "
                "goes in the Notes column so the parse stays trivial."
                % (i + 1, path, budget)
            )
            continue
        entries.append((path, int(budget), i + 1))

    return entries, defects


def count_lines(path):
    """Line count, or None if the file is missing."""
    if not os.path.isfile(path):
        return None
    with open(path, "rb") as fh:
        return sum(1 for _ in fh)


def check(manifest_path, root, report_only=False):
    """Returns (violations, rows). rows is (path, budget, actual_or_None)."""
    if not os.path.isfile(manifest_path):
        return (["manifest file missing: %s" % manifest_path], [])
    with open(manifest_path, encoding="utf-8") as fh:
        entries, defects = parse_manifest(fh.read())

    violations = list(defects)
    rows = []
    for path, budget, lineno in entries:
        actual = count_lines(os.path.join(root, path))
        rows.append((path, budget, actual))
        if actual is None:
            violations.append(
                "%s:%d: %s is budgeted but not on disk. A budget pointing at "
                "nothing is stale; remove the row or fix the path."
                % (manifest_path, lineno, path)
            )
        elif actual > budget:
            violations.append(
                "%s: %d lines, budget %d, over by %d. Cut or relocate content, "
                "or raise the budget in this PR with a one-line reason."
                % (path, actual, budget, actual - budget)
            )
    return violations, rows


def print_report(rows):
    if not rows:
        print("No budgeted files found.")
        return
    width = max(len(r[0]) for r in rows)
    print("%-*s  %7s  %7s  %8s" % (width, "file", "lines", "budget", "headroom"))
    for path, budget, actual in rows:
        if actual is None:
            print("%-*s  %7s  %7d  %8s" % (width, path, "missing", budget, "-"))
            continue
        print("%-*s  %7d  %7d  %8d" % (width, path, actual, budget, budget - actual))


def selftest():
    """Offline fixtures. Each case builds a temp repo and asserts the verdict."""
    cases, failures = 0, []

    def run(name, manifest, files, expect_violations):
        nonlocal cases
        cases += 1
        with tempfile.TemporaryDirectory() as tmp:
            mpath = os.path.join(tmp, "manifest.md")
            with open(mpath, "w", encoding="utf-8") as fh:
                fh.write(manifest)
            for fname, nlines in files.items():
                target = os.path.join(tmp, fname)
                os.makedirs(os.path.dirname(target), exist_ok=True) if os.path.dirname(fname) else None
                with open(target, "w", encoding="utf-8") as fh:
                    fh.write("\n".join("x" for _ in range(nlines)) + "\n" if nlines else "")
            violations, _ = check(mpath, tmp)
            got = len(violations)
            if got != expect_violations:
                failures.append(
                    "%s: expected %d violation(s), got %d: %s"
                    % (name, expect_violations, got, violations)
                )

    table = (
        "| File | Class | budget_lines | Notes |\n"
        "|---|---|---:|---|\n"
        "| `A.md` | kernel | 10 | binding rules |\n"
    )

    run("under budget", table, {"A.md": 5}, 0)
    run("exactly at budget", table, {"A.md": 10}, 0)
    run("over budget", table, {"A.md": 11}, 1)
    run("missing file", table, {}, 1)
    run(
        "unparseable budget cell",
        "| File | budget_lines |\n|---|---|\n| `A.md` | 10 lines |\n",
        {"A.md": 5},
        1,
    )
    run("no table", "Just prose, no table here.\n", {"A.md": 5}, 1)
    run(
        "two tables is a source-of-truth defect",
        table + "\nprose\n\n" + table,
        {"A.md": 5},
        1,
    )
    run(
        "extra columns and a bare path ride along",
        "| File | budget_lines |\n|---|---|\n| A.md | 3 |\n",
        {"A.md": 9},
        1,
    )

    if failures:
        print("SELFTEST FAILED (%d/%d)" % (len(failures), cases))
        for f in failures:
            print("  " + f)
        return 1
    print("selftest: %d/%d passed" % (cases, cases))
    return 0


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--manifest", default=None)
    ap.add_argument("--root", default=".")
    ap.add_argument("--report", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args()

    if args.selftest:
        return selftest()

    manifest = (
        args.manifest
        or os.environ.get("CONTEXT_BUDGET_MANIFEST")
        or DEFAULT_MANIFEST_PATH
    )
    violations, rows = check(manifest, args.root, report_only=args.report)

    if args.report:
        print_report(rows)
        for v in violations:
            print("note: " + v)
        return 0

    if violations:
        print("Context budget guard failed on %d item(s):\n" % len(violations))
        for v in violations:
            print("  " + v)
        print("\nBudgets live in %s. Raising one is allowed in the same PR, with a reason." % manifest)
        return 1

    print("Context budget: %d file(s) inside budget." % len(rows))
    return 0


if __name__ == "__main__":
    sys.exit(main())
