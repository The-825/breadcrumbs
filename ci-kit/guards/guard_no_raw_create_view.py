#!/usr/bin/env python3
"""Guard: no raw CREATE VIEW in .sql.

Every view ships through your version-controlled view layer (for example,
Dataform .sqlx definitions with data-quality assertions wired into a real run
gate). A raw `CREATE VIEW` or `CREATE OR REPLACE VIEW` in a .sql file forks a
second, console-drifting view layer, so it fails this guard. .sqlx files are
the sanctioned layer and are not scanned.

Usage:
    guard_no_raw_create_view.py [path ...]
No args -> CI mode: scans DEFAULT_PATHS with DEFAULT_EXCLUDE applied.
Explicit path -> self-test mode: exclusions are skipped. Exit 1 on violation,
0 if clean.
"""
import os
import re
import sys

# ---- Configuration: edit for your repo layout --------------------------------
DEFAULT_PATHS = ["backend"]  # trees scanned in CI mode (no args)
DEFAULT_EXCLUDE = ("ci-kit/guards/tests/bad_fixtures/", "/.git/", "__pycache__")
# -------------------------------------------------------------------------------

CREATE_VIEW_RE = re.compile(r"\bCREATE\s+(?:OR\s+REPLACE\s+)?VIEW\b", re.IGNORECASE)


def _iter_files(paths, apply_exclude):
    for p in paths:
        if os.path.isfile(p):
            if p.endswith(".sql"):
                yield p
        elif os.path.isdir(p):
            for root, _dirs, files in os.walk(p):
                for name in files:
                    if not name.endswith(".sql"):
                        continue  # .sqlx (the managed view layer) is sanctioned
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
        if CREATE_VIEW_RE.search(line):
            problems.append((fp, i, "raw CREATE VIEW: define the view in the version-controlled view layer (.sqlx)"))
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
    print("guard_no_raw_create_view: " + ("FAILED" if fail else "clean"))
    return fail


if __name__ == "__main__":
    sys.exit(main(sys.argv))
