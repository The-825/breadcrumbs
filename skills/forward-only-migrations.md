# Forward-only migrations

> Part of the companion kit for *From Archivist to Architect* (The Architect's Blueprint, Book 1).

Rolling a schema back sounds tidy until you meet the row that was written after the migration ran: drop the column and that data is gone, with no incident report, just a quiet hole someone finds months later. Forward-only migration discipline removes the whole category. Schema changes only move forward, history is append-only, and the migration folder becomes an audit trail you can trust. Paste the rules below into your agent rules file or data-engineering handbook.

```markdown
## Migration rules

1. Migrations are forward-only. Never roll back schema. To undo a
   change, ship a new forward migration that supersedes it.
2. Add columns, never repurpose or drop in place. A retired column
   stays, carrying a deprecation note ("retired 2026-03: replaced by
   X, do not wire new consumers"), so old rows stay interpretable.
3. Migration files are numbered and immutable. No renumbering, and no
   editing a migration after it has been applied anywhere. A superseded
   migration gets a successor file (`014_fix_order_totals_v2.sql`); the
   original stays in place.
4. Migration files are never deleted. The folder is the audit trail for
   every write it performed, and the rebuild script for any fresh copy
   of the database.
5. Applied-state lives in a runner, not in your memory. The runner
   tracks which migrations ran in which environment and refuses
   out-of-order application. A tool, not a folder.
6. Verify against the live schema before authoring. A 30-second
   information-schema check prevents assuming a table's shape wrong,
   including assuming a table does not exist when it is already
   populated.
7. Every migration file carries a provenance header: why it exists, how
   it was applied, and the date. The header is the source of truth for
   that migration; when in doubt, open the file.
8. Records a process depends on get soft-delete markers, never row
   deletes: a dated marker column plus a who-did-it audit column, with
   default queries excluding marked rows and an audit path that can
   still see them.
9. Verified-safe deletion is allowed for regenerable data. Derived
   tables, redundant copies, and genuinely unused artifacts may be
   dropped once you have verified against the live store that nothing
   downstream depends on them. If you cannot verify, archive instead.
10. Write mutating migrations so a re-run against an already-migrated
    database is harmless: target the pre-migration state in the WHERE
    clause, use add-if-not-exists and merge-when-not-matched forms.
```

## Adoption notes

The deprecation note in rule 2 is doing more work than it looks like. An orders table that gained `total_cents` and kept a retired `total` column, note attached, remains readable at every point in its history; the same table with `total` dropped has rows nobody can fully interpret anymore.

Rule 5 is the difference between a migration system and a folder of SQL. Without tracked applied-state per environment, "did staging get 017?" is answered by archaeology. With it, the runner answers, and refuses to apply 019 before 018.

Rules 6 and 10 pair up as the safety habit: check reality before you write, and write so that a double-apply cannot hurt. Together they make the folder something you can hand to a new environment and replay start to finish.

One caveat on rule 3's "numbered" as you scale. Sequential integers collide the moment two branches both claim the next one, and a busy repo hits that weekly. The immutability is the load-bearing part, not the integer: swap the number for a timestamp or a short slug key (`2026_03_14_add_order_totals`) and parallel branches stop racing for the same filename. The runner still orders by the key and still refuses out-of-order application; the file is still immutable and still never deleted. The CI kit's migration policy ships this slug-keyed form for exactly this reason.

Schema history you cannot rewrite is schema history you can trust.
