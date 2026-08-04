#!/usr/bin/env python3
"""Migration runner: numbering integrity + applied-per-tenant ledger.

A tool, not a loose folder. Migrations are `NNN_name.sql` files in this
directory. The runner tracks which migrations have been applied per tenant in
a JSON ledger and REFUSES two failure classes before they reach a database:

  * duplicate numbers  - two files sharing the same NNN (born from a real
    incident where three migrations shared one number).
  * out-of-order apply  - a pending file numbered at or below the highest number
    already applied for a tenant (a migration inserted behind the frontier).

Scope: this validates and manages the ledger only. It does NOT execute SQL
against any database; the integrity layer and the apply layer are separable,
and a real apply step belongs to a later phase of your build.

The 3-digit prefix is a convention, not a law: widen MIGRATION_RE if your
project needs more than 999 migrations.

CLI:
    runner.py validate                     # numbering integrity across the folder
    runner.py status --tenant <t>          # applied vs pending for a tenant
    runner.py plan --tenant <t>            # pending in order; refuses out-of-order
    runner.py mark --tenant <t> --file <NNN_name.sql>   # record as applied

Exit 1 on any integrity problem, 0 if clean.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys

MIGRATIONS_DIR = os.path.dirname(os.path.abspath(__file__))
LEDGER_PATH = os.path.join(MIGRATIONS_DIR, "applied_ledger.json")
MIGRATION_RE = re.compile(r"^(\d{3})_.+\.sql$")


class DuplicateNumberError(Exception):
    pass


class OutOfOrderError(Exception):
    pass


def discover(migrations_dir: str = MIGRATIONS_DIR):
    """Return sorted [(num, filename)]. Raise DuplicateNumberError on a dup NNN."""
    by_num: dict = {}
    for name in os.listdir(migrations_dir):
        m = MIGRATION_RE.match(name)
        if not m:
            continue
        num = int(m.group(1))
        if num in by_num:
            raise DuplicateNumberError(
                f"duplicate migration number {num:03d}: {by_num[num]} and {name}"
            )
        by_num[num] = name
    return sorted((num, by_num[num]) for num in by_num)


def load_ledger(ledger_path: str = LEDGER_PATH) -> dict:
    if not os.path.exists(ledger_path):
        return {}
    with open(ledger_path, encoding="utf-8") as f:
        return json.load(f)


def save_ledger(ledger: dict, ledger_path: str = LEDGER_PATH) -> None:
    with open(ledger_path, "w", encoding="utf-8") as f:
        json.dump(ledger, f, indent=2, sort_keys=True)
        f.write("\n")


def applied_for(ledger: dict, tenant: str) -> list:
    return list(ledger.get(tenant, []))


def _num_of(filename: str) -> int:
    m = MIGRATION_RE.match(filename)
    if not m:
        raise ValueError(f"not a migration filename: {filename}")
    return int(m.group(1))


def pending(migrations_dir, ledger, tenant) -> list:
    applied = set(applied_for(ledger, tenant))
    return [name for _num, name in discover(migrations_dir) if name not in applied]


def check_apply_order(migrations_dir, ledger, tenant) -> None:
    """Raise OutOfOrderError if any pending file sits at/below the applied frontier."""
    applied = applied_for(ledger, tenant)
    max_applied = max((_num_of(n) for n in applied), default=-1)
    for name in pending(migrations_dir, ledger, tenant):
        if _num_of(name) <= max_applied:
            raise OutOfOrderError(
                f"{name} is numbered at/below the applied frontier "
                f"{max_applied:03d} for tenant {tenant!r} - migrations are forward-only"
            )


def validate(migrations_dir: str = MIGRATIONS_DIR) -> list:
    """Return a list of integrity problems (empty = clean)."""
    problems = []
    try:
        discover(migrations_dir)
    except DuplicateNumberError as e:
        problems.append(str(e))
    return problems


# ---- CLI --------------------------------------------------------------------

def _cmd_validate(args) -> int:
    problems = validate(args.dir)
    if problems:
        for p in problems:
            print(f"ERROR: {p}")
        print("validate: FAILED")
        return 1
    print("validate: numbering integrity clean")
    return 0


def _cmd_status(args) -> int:
    if validate(args.dir):
        return _cmd_validate(args)
    ledger = load_ledger(args.ledger)
    applied = applied_for(ledger, args.tenant)
    pend = pending(args.dir, ledger, args.tenant)
    print(f"tenant: {args.tenant}")
    print(f"applied ({len(applied)}): {applied}")
    print(f"pending ({len(pend)}): {pend}")
    return 0


def _cmd_plan(args) -> int:
    if validate(args.dir):
        return _cmd_validate(args)
    ledger = load_ledger(args.ledger)
    try:
        check_apply_order(args.dir, ledger, args.tenant)
    except OutOfOrderError as e:
        print(f"ERROR: {e}")
        print("plan: FAILED")
        return 1
    pend = pending(args.dir, ledger, args.tenant)
    print(f"plan for {args.tenant}: {pend}")
    return 0


def _cmd_mark(args) -> int:
    if validate(args.dir):
        return _cmd_validate(args)
    if not MIGRATION_RE.match(args.file):
        print(f"ERROR: {args.file} is not a NNN_name.sql migration")
        return 1
    ledger = load_ledger(args.ledger)
    ledger.setdefault(args.tenant, [])
    if args.file not in ledger[args.tenant]:
        ledger[args.tenant].append(args.file)
        ledger[args.tenant].sort()
    save_ledger(ledger, args.ledger)
    print(f"marked {args.file} applied for {args.tenant}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Migration runner (validate + ledger).")
    p.add_argument("--dir", default=MIGRATIONS_DIR, help="migrations directory")
    p.add_argument("--ledger", default=LEDGER_PATH, help="applied-ledger JSON path")
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("validate")
    s = sub.add_parser("status"); s.add_argument("--tenant", required=True)
    s = sub.add_parser("plan"); s.add_argument("--tenant", required=True)
    s = sub.add_parser("mark"); s.add_argument("--tenant", required=True); s.add_argument("--file", required=True)
    return p


def main(argv=None) -> int:
    args = build_parser().parse_args(argv)
    return {
        "validate": _cmd_validate,
        "status": _cmd_status,
        "plan": _cmd_plan,
        "mark": _cmd_mark,
    }[args.cmd](args)


if __name__ == "__main__":
    sys.exit(main())
