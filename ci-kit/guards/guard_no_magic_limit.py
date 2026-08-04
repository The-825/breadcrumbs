#!/usr/bin/env python3
"""Guard: no hardcoded numeric SQL LIMIT (enforces your no-magic-numbers rule).

A literal `LIMIT 100` in a query is a magic number. Row limits live in the
central config registry (CONFIG.<row_limit_key> style keys) and are bound as
query parameters. This guard fails on `LIMIT <digits>` in .py and .sql files.

Usage:
    guard_no_magic_limit.py [path ...]
No args -> CI mode: scans DEFAULT_PATHS with DEFAULT_EXCLUDE applied.
Explicit path -> self-test mode: exclusions are skipped, so the guard bites a
bad fixture handed to it directly. Exit 1 on violation, 0 if clean.
"""
import os
import re
import sys

# ---- Configuration: edit for your repo layout --------------------------------
DEFAULT_PATHS = ["backend"]  # trees scanned in CI mode (no args)
DEFAULT_EXCLUDE = ("ci-kit/guards/tests/bad_fixtures/", "/.git/", "__pycache__")
# -------------------------------------------------------------------------------

EXTS = (".py", ".sql")
LIMIT_RE = re.compile(r"\bLIMIT\s+\d+", re.IGNORECASE)


def _iter_files(paths, apply_exclude):
    for p in paths:
        if os.path.isfile(p):
            if p.endswith(EXTS):
                yield p
        elif os.path.isdir(p):
            for root, _dirs, files in os.walk(p):
                for name in files:
                    if not name.endswith(EXTS):
                        continue
                    fp = os.path.join(root, name)
                    if apply_exclude and any(x in fp.replace("\\", "/") for x in DEFAULT_EXCLUDE):
                        continue
                    yield fp


def check_file(fp):
    problems = []
    try:
        with open(fp, encoding="utf-8") as f:
            lines = f.readlines()
    except (UnicodeDecodeError, FileNotFoundError):
        return problems
    for i, line in enumerate(lines, 1):
        if LIMIT_RE.search(line):
            problems.append((fp, i, "hardcoded SQL LIMIT: use a CONFIG.<row_limit_key> value as a bound query parameter"))
    return problems


def main(argv):
    args = argv[1:]
    apply_exclude = not args
    paths = args if args else DEFAULT_PATHS
    fail = 0
    for fp in _iter_files(paths, apply_exclude):
        for path, line, msg in check_file(fp):
            print(f"{path}:{line}: {msg}")
            fail = 1
    print("guard_no_magic_limit: " + ("FAILED" if fail else "clean"))
    return fail


if __name__ == "__main__":
    sys.exit(main(sys.argv))
