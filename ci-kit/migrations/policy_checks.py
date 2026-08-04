#!/usr/bin/env python3
"""Merge-time content lints for a migrations folder: policy replaces the label.

TEMPLATE. The pattern this file exists to teach: a path family graduates
off the merge gate's protected list (see ci-kit/workflows/decision_script.py,
PROTECTED_PATHS) only when automated content lints replace the judgment the
operator's approval label was buying. Until these checks exist, migration
PRs keep the human gate. Once they exist, a clean migration PR merges
label-free and a dirty one waits for the label, which stays the explicit
override for legitimately destructive work.

Three lints, each answering one question the operator used to answer by eye:

  1. FORWARD-ONLY. No DROP TABLE, DROP COLUMN, or TRUNCATE, and no DELETE
     FROM against a protected table (your canonical, archive-do-not-lose
     stores). Verified-safe row deletes on ordinary operational tables stay
     allowed; the lint bounds blast radius, it does not ban cleanup.
  2. RISKY DEFAULTS SHIP OFF. A numbered migration that seeds the flag
     table with an enabled/true default is blocked, unless the file header
     carries the override marker followed by the operator's quoted
     instruction. The escape hatch is deliberate and auditable: the
     approval travels IN the file, greppable forever, instead of living in
     a chat message.
  3. DUPLICATE-NUMBER GUARD. A new numbered migration is blocked when its
     number already exists on the base branch under another name, repeats
     within the same PR, or was never claimed in the folder README's
     next-free ledger (claim first, author second; see README.md here).
     Deleting or renaming an existing migration file is also blocked: the
     applied history is an audit trail.
  4. NAMESPACE GUARD (off until you enact it). Numbering is generation
     one; when the counter itself becomes the thing agents race for, close
     the numbered era and switch new files to timestamp-slug keys
     (YYYYMMDD_HHMM_<slug>.sql; README, "Ending the number race"). With
     SLUG_ERA_ENACTED, any NEW serial-numbered file is a violation and
     slug files skip the numbering checks entirely, because a mint-dated
     key has nothing to claim. Content lints 1 and 2 apply to both eras.

Fail-closed floor: a missing base tree, a missing head tree, or an
unparseable next-free ledger is a violation, never a pass. If the check
cannot see the thing it gates, the PR waits for the label.

Wiring: the merge gate calls `policy_violations(scoped_paths, head_root,
base_root)` with the PR's changed paths under MIGRATIONS_DIR, a checkout
of the PR head (the contents that would merge), and a checkout of the base
branch (the trusted tree plus the existing numbers). In
decision_script.py:

    from policy_checks import policy_violations
    CONTENT_POLICIES = (("migrations/", policy_violations),)

Relationship to runner.py (same folder): the runner guards REPO STATE (a
duplicate number anywhere in the folder, an out-of-order apply) and runs
in your checks workflow on every PR; this module guards the PR DIFF at
merge time with the base/head context only the gate has. They overlap on
duplicate numbers on purpose: lowest-layer catch plus merge-time catch.

Pure functions, no side effects at import; unit tests in
tests/test_policy_checks.py exercise them directly against throwaway
base/head trees.
"""
from __future__ import annotations

import os
import re

# ---------------------------------------------------------------------------
# Configuration. EDIT ME: every constant here is a convention to adapt.
# ---------------------------------------------------------------------------

# Repo-relative folder the policy covers, trailing slash. Keep identical to
# the prefix you register in decision_script.py CONTENT_POLICIES.
MIGRATIONS_DIR = "migrations/"

# Substrings identifying tables a migration must never DELETE from: your
# canonical, archive-do-not-lose stores. Empty tuple = the DELETE lint is
# off until you name them (the DROP/TRUNCATE lints stay on regardless).
PROTECTED_TABLE_TOKENS = ()

# The table your feature-flag seeds insert into.
FLAG_TABLE = "feature_flags"

# A flag seed may ship enabled/true label-free ONLY when the file header
# carries this marker followed by the operator's verbatim instruction, e.g.
#   -- APPROVED-DEFAULT-ON: <operator> <date>: "turn it on for everyone"
SEED_OVERRIDE_MARKER = "APPROVED-DEFAULT-ON:"

# Numbered migration files, matching runner.py's convention (NNN_name.sql).
# Unnumbered files (for example dated snapshot re-dumps of live state,
# which legitimately carry true values) are exempt from lints 2 and 3 by
# construction: regenerable re-dump files are records, not migrations.
NUMBERED_MIGRATION_RE = re.compile(r"^(\d{3})_.+\.sql$")

# Parsed from the folder README's single ledger line (see README.md here):
# a number is claimed only when it is BELOW the next-free number.
NEXT_FREE_RE = re.compile(r"next-free number is `(\d+)`")

# The timestamp-slug era switch (lint 4). EDIT ME when you enact the slug
# convention: flip the switch and record the last number you ever minted,
# so the violation message teaches the boundary. Until then the guard is
# inert and the numbered convention above is the only one.
SLUG_ERA_ENACTED = False
NUMBERED_ERA_CLOSED_AT = None  # e.g. 311, the last minted number

# Timestamp-slug migration files: YYYYMMDD_HHMM_<slug>.sql, UTC mint time.
# The prefix is a mint date, not a claimable serial, so no duplicate-number
# guard and no next-free ledger apply: the only true collision is a
# byte-identical filename, which git itself rejects as a same-path add
# conflict. (NUMBERED_MIGRATION_RE cannot reach into the 8-digit prefix:
# after exactly three digits it requires an underscore.)
SLUG_MIGRATION_RE = re.compile(r"^\d{8}_\d{4}_.+\.sql$")

DESTRUCTIVE_SQL = [
    (re.compile(r"\bDROP\s+TABLE\b", re.IGNORECASE), "DROP TABLE"),
    (re.compile(r"\bDROP\s+COLUMN\b", re.IGNORECASE), "DROP COLUMN"),
    (re.compile(r"\bTRUNCATE\b", re.IGNORECASE), "TRUNCATE"),
]
INSERT_FLAGS_RE = re.compile(
    r"\bINSERT\s+INTO\s+" + re.escape(FLAG_TABLE) + r"\b", re.IGNORECASE)


def _strip_sql(sql, strip_strings=True):
    """Remove comments (-- and /* */) and, optionally, single-quoted string
    literals, so prose in headers and quoted filenames cannot false-positive
    the statement-level regexes."""
    sql = re.sub(r"--[^\n]*", "", sql)
    sql = re.sub(r"/\*.*?\*/", "", sql, flags=re.DOTALL)
    if strip_strings:
        sql = re.sub(r"'(?:[^']|'')*'", "''", sql)
    return sql


def sql_policy_violations(path, raw_sql, protected_tables=None):
    """Content lint for one migration file's SQL. Returns a list of
    violation strings (empty = clean)."""
    protected_tables = (PROTECTED_TABLE_TOKENS if protected_tables is None
                        else protected_tables)
    out = []
    stripped = _strip_sql(raw_sql)                            # no comments, no strings
    with_strings = _strip_sql(raw_sql, strip_strings=False)   # no comments only

    # Lint 1: forward-only.
    for rx, label in DESTRUCTIVE_SQL:
        if rx.search(stripped):
            out.append(f"{path}: {label} (schema history is forward-only)")
    if protected_tables:
        delete_rx = re.compile(
            r"\bDELETE\s+FROM\s+\S*(?:%s)" % "|".join(
                re.escape(t) for t in protected_tables),
            re.IGNORECASE)
        if delete_rx.search(stripped):
            out.append(f"{path}: DELETE targeting a protected table "
                       "(archive, do not lose)")

    # Lint 2: flag seeds ship default OFF. Scoped to numbered and slug
    # migrations; unnumbered re-dump files are exempt by construction.
    name = path.rsplit("/", 1)[-1]
    if (NUMBERED_MIGRATION_RE.match(name) or SLUG_MIGRATION_RE.match(name)) \
            and INSERT_FLAGS_RE.search(stripped):
        if SEED_OVERRIDE_MARKER not in raw_sql:
            for stmt in with_strings.split(";"):
                if not INSERT_FLAGS_RE.search(stmt):
                    continue
                # Catch both the bare boolean and a quoted 'true' literal.
                if re.search(r"\bTRUE\b", _strip_sql(stmt)) or \
                        re.search(r"'true'", stmt, re.IGNORECASE):
                    out.append(
                        f"{path}: flag seed with an enabled/true default; ship "
                        f"it OFF, or add a {SEED_OVERRIDE_MARKER} header quoting "
                        "the operator's instruction")
                    break
    return out


def policy_violations(changed, head_root, base_root,
                      migrations_dir=None, protected_tables=None,
                      slug_era_enacted=None, numbered_era_closed_at=None):
    """Policy checks for the PR-changed files under the migrations folder.

    changed:   changed paths under migrations_dir (renames contribute BOTH
               paths, same as everywhere else in the gate).
    head_root: filesystem checkout of the PR head (contents that would merge).
    base_root: filesystem checkout of the base branch (the trusted tree and
               the existing migration numbers).
    Returns a list of violation strings (empty = clean). Any inability to
    inspect is itself a violation: fail closed.
    """
    migrations_dir = MIGRATIONS_DIR if migrations_dir is None else migrations_dir
    slug_era_enacted = (SLUG_ERA_ENACTED if slug_era_enacted is None
                        else slug_era_enacted)
    numbered_era_closed_at = (NUMBERED_ERA_CLOSED_AT if numbered_era_closed_at is None
                              else numbered_era_closed_at)
    if head_root is None or base_root is None:
        return ["no head/base checkout to inspect; failing closed"]
    base_dir = os.path.join(base_root, migrations_dir)
    if not os.path.isdir(base_dir):
        return [f"{migrations_dir} missing from the base checkout; failing closed"]
    base_names = set(os.listdir(base_dir))

    # Next-free ledger from the HEAD README: the claiming edit rides the
    # same PR or an earlier merged one; either way the head shows it.
    next_free = None
    readme_path = os.path.join(head_root, migrations_dir, "README.md")
    if os.path.exists(readme_path):
        with open(readme_path, "r", encoding="utf-8") as fh:
            m = NEXT_FREE_RE.search(fh.read())
        if m:
            next_free = int(m.group(1))

    out = []
    seen_numbers = {}
    for path in sorted(set(changed)):
        name = path.rsplit("/", 1)[-1]
        if not name.endswith(".sql"):
            continue  # README edits and the like carry no SQL policy
        head_file = os.path.join(head_root, path)
        in_base = name in base_names

        if not os.path.exists(head_file):
            # Present in the change set, absent from head = deleted or
            # renamed away. The applied history is an audit trail; both
            # keep the human gate.
            if in_base:
                out.append(f"{path}: migration file deleted or renamed (the "
                           "applied history is an audit trail); needs the "
                           "operator's label")
            continue

        with open(head_file, "r", encoding="utf-8", errors="replace") as fh:
            out.extend(sql_policy_violations(path, fh.read(), protected_tables))

        if SLUG_MIGRATION_RE.match(name):
            # Mint-dated key: nothing to claim, nothing to collide with
            # short of a same-path git conflict. Content lints already ran.
            continue

        m = NUMBERED_MIGRATION_RE.match(name)
        if m and not in_base and slug_era_enacted:
            closed = (f" (closed at {numbered_era_closed_at})"
                      if numbered_era_closed_at is not None else "")
            out.append(f"{path}: new serial-numbered migration; the numbered "
                       f"era is closed{closed}. Name it YYYYMMDD_HHMM_<slug>"
                       ".sql, UTC mint time")
            continue
        if m and not in_base:  # a NEW numbered file: duplicate-number guard
            num = int(m.group(1))
            for existing in base_names:
                em = NUMBERED_MIGRATION_RE.match(existing)
                if em and int(em.group(1)) == num and existing != name:
                    out.append(f"{path}: number {num} already taken on the "
                               f"base branch by {existing}")
            if num in seen_numbers:
                out.append(f"{path}: number {num} also used by "
                           f"{seen_numbers[num]} in this same PR")
            seen_numbers.setdefault(num, path)
            if next_free is None:
                out.append(f"{path}: could not read the next-free ledger from "
                           "the folder README; failing closed (claim first, "
                           "author second)")
            elif num >= next_free:
                out.append(f"{path}: number {num} is not claimed (the README "
                           f"next-free ledger says {next_free}); claim first, "
                           "author second")
    return out
