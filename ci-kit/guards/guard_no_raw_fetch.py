#!/usr/bin/env python3
"""Guard: no raw fetch() in frontend JS.

Every backend call goes through your approved API wrapper functions (for
example fetchAPI / fetchAPIWrite in one api module). A bare fetch( bypasses
auth-redirect handling, error handling, and the fallback UI state, so it fails
this guard. Wrapper calls like fetchAPI( never match (the regex requires that
'fetch' is not part of a longer identifier and is followed by an open paren),
and the wrapper module itself is exempt because it is the one sanctioned call
site of the platform fetch.

Usage:
    guard_no_raw_fetch.py [path ...]
No args -> CI mode: scans DEFAULT_PATHS with DEFAULT_EXCLUDE applied. A repo
with no static JS yet passes vacuously; the guard still bites its bad fixture.
Explicit path -> self-test mode: exclusions are skipped. Exit 1 on violation,
0 if clean.
"""
import os
import re
import sys

# ---- Configuration: edit for your repo layout --------------------------------
DEFAULT_PATHS = ["backend/static", "static"]  # JS surfaces scanned in CI mode
DEFAULT_EXCLUDE = ("ci-kit/guards/tests/bad_fixtures/", "/.git/", "__pycache__", "/vendor/")
APPROVED_WRAPPER = "api.js"  # the one file allowed to call the platform fetch
# -------------------------------------------------------------------------------

# fetch( not immediately preceded by a word char, so wrapper names that end in
# a suffix (fetchAPI( / fetchAPIWrite() never match: there the '(' follows the
# suffix, not 'fetch'.
FETCH_RE = re.compile(r"(?<![\w$])fetch\s*\(")


def _iter_files(paths, apply_exclude):
    for p in paths:
        if os.path.isfile(p):
            if p.endswith(".js"):
                yield p
        elif os.path.isdir(p):
            for root, _dirs, files in os.walk(p):
                for name in files:
                    if not name.endswith(".js"):
                        continue
                    fp = os.path.join(root, name)
                    if apply_exclude and any(x in fp.replace("\\", "/") for x in DEFAULT_EXCLUDE):
                        continue
                    yield fp


def check_file(fp):
    problems = []
    if os.path.basename(fp) == APPROVED_WRAPPER:
        return problems  # the wrapper is the sanctioned fetch site
    try:
        with open(fp, encoding="utf-8") as f:
            lines = f.readlines()
    except (UnicodeDecodeError, FileNotFoundError):
        return problems
    for i, line in enumerate(lines, 1):
        if FETCH_RE.search(line):
            problems.append((fp, i, f"raw fetch(): use the approved wrappers from {APPROVED_WRAPPER}"))
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
    print("guard_no_raw_fetch: " + ("FAILED" if fail else "clean"))
    return fail


if __name__ == "__main__":
    sys.exit(main(sys.argv))
