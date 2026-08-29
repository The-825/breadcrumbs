#!/usr/bin/env python3
"""Guard: no likely PII in test fixtures.

Test fixtures must be synthetic. This guard fails on PII-shaped tokens in
fixture files:
  * a real-looking institutional email address (addresses on EMAIL_DOMAIN are
    PII-shaped; use @example.com placeholders in fixtures instead), and
  * an ID-shaped number of exactly ID_DIGITS digits (set ID_DIGITS to the
    length of your institution's person identifiers).

It is pragmatic, not exhaustive: it scans the fixture surfaces where synthetic
data lives (DEFAULT_PATHS), not the whole repo, so real staff addresses in
docs are out of scope. Use @example.com and placeholder ids of a different
length in fixtures. A complete 40-character hexadecimal Git object id is a
public code pointer, so digit runs inside it are not treated as person ids.

Usage:
    guard_no_pii_in_fixtures.py [path ...]
No args -> CI mode: scans DEFAULT_PATHS with DEFAULT_EXCLUDE applied.
Explicit path -> self-test mode: exclusions are skipped, so the guard bites a
bad fixture handed to it directly.
    ... | guard_no_pii_in_fixtures.py --stdin -> outbound-payload mode: scans
    stdin instead of the filesystem, using the SAME detector. This is what
    lets a pre-push git guard and a PreToolUse hook on non-git outbound tool
    calls (email, cloud-drive uploads, publish-to-web) share this one guard
    instead of each growing its own copy of the regexes. See
    templates/hooks/outbound-pii-screen.md for the wiring.
Exit 1 on violation, 0 if clean.
"""
import os
import re
import sys

# ---- Configuration: edit for your institution and repo layout ----------------
EMAIL_DOMAIN = "example-institution.edu"  # your institutional email domain
ID_DIGITS = 9                             # length of your person-identifier numbers
DEFAULT_PATHS = ["backend/tests/fixtures", "tests"]  # fixture surfaces scanned in CI mode
DEFAULT_EXCLUDE = ("ci-kit/guards/tests/bad_fixtures/", "/.git/", "__pycache__", "/node_modules/")
# -------------------------------------------------------------------------------

EXTS = (".json", ".csv", ".ndjson", ".py", ".js", ".sql", ".txt", ".yaml", ".yml")

EMAIL_RE = re.compile(r"[A-Za-z0-9._%+-]+@" + re.escape(EMAIL_DOMAIN), re.IGNORECASE)
# A digit run embedded in a public handle or slug is not a person identifier.
# Requiring a non-alphanumeric boundary keeps the detector focused on
# standalone ID-shaped values without corrupting canonical repository names.
ID_RE = re.compile(r"(?<![A-Za-z0-9])\d{" + str(ID_DIGITS) + r"}(?![A-Za-z0-9])")
GIT_OBJECT_RE = re.compile(r"(?<![0-9A-Fa-f])[0-9A-Fa-f]{40}(?![0-9A-Fa-f])")


def _iter_files(paths, apply_exclude):
    for p in paths:
        if os.path.isfile(p):
            yield p
        elif os.path.isdir(p):
            for root, _dirs, files in os.walk(p):
                for name in files:
                    fp = os.path.join(root, name)
                    if not fp.endswith(EXTS):
                        continue
                    if apply_exclude and any(x in fp.replace("\\", "/") for x in DEFAULT_EXCLUDE):
                        continue
                    yield fp


def check_line(line):
    """The two PII checks on one line of text. Shared by file mode and
    --stdin mode, so a filesystem scan and an outbound-payload scan can
    never drift apart."""
    msgs = []
    for tok in EMAIL_RE.findall(line):
        msgs.append(f"PII-shaped institutional email '{tok}': use an @example.com placeholder")
    line_without_git_objects = GIT_OBJECT_RE.sub("", line)
    for tok in ID_RE.findall(line_without_git_objects):
        msgs.append(f"{ID_DIGITS}-digit ID-shaped number '{tok}': fixtures must be synthetic (use a different length)")
    return msgs


def check_file(fp):
    problems = []
    try:
        with open(fp, encoding="utf-8") as f:
            lines = f.readlines()
    except (UnicodeDecodeError, FileNotFoundError):
        return problems
    for i, line in enumerate(lines, 1):
        for msg in check_line(line):
            problems.append((fp, i, msg))
    return problems


def check_stdin(stream):
    problems = []
    for i, line in enumerate(stream, 1):
        for msg in check_line(line):
            problems.append(("<stdin>", i, msg))
    return problems


def main(argv):
    args = argv[1:]
    if args and args[0] == "--stdin":
        fail = 0
        for path, line, msg in check_stdin(sys.stdin):
            print(f"{path}:{line}: {msg}")
            fail = 1
        print("guard_no_pii_in_fixtures: " + ("FAILED" if fail else "clean"))
        return fail
    apply_exclude = not args
    paths = args if args else DEFAULT_PATHS
    fail = 0
    for fp in _iter_files(paths, apply_exclude):
        for path, line, msg in check_file(fp):
            print(f"{path}:{line}: {msg}")
            fail = 1
    print("guard_no_pii_in_fixtures: " + ("FAILED" if fail else "clean"))
    return fail


if __name__ == "__main__":
    sys.exit(main(sys.argv))
