# Authority ledger template

> Part of the companion kit for *From Archivist to Architect* (The Architect's Blueprint, Book 1).

The authority ledger is the permissions sibling of the conclusions store ([CONCLUSIONS_TEMPLATE.md](CONCLUSIONS_TEMPLATE.md)): conclusions record what is TRUE, the ledger records what sessions are ALLOWED TO DO. One JSON line per standing grant the operator has issued (merge lanes, write envelopes, production toggles, build mandates), append-only, validated in CI. Full pattern, rationale, and the merge-authority extension: [docs/authority-ledger.md](../docs/authority-ledger.md). A young pattern, adopted mid-July 2026; published early with its guard.

Starter file to copy: [authority_ledger.jsonl](authority_ledger.jsonl). Capture command: [commands/grant.md](commands/grant.md). CI guard: [ci-kit/guards/guard_authority_citations.py](../ci-kit/guards/guard_authority_citations.py).

## The line format

```
{"id": "G-YYYYMMDD-NN", "date": "YYYY-MM-DD", "scope": "<what is permitted, checkable>", "wording": "<operator's verbatim words, or null>", "source": "<REQUIRED pointer: rules-file section, PR #, decisions entry, session + date>", "expiry": "YYYY-MM-DD or null", "status": "active | expired | revoked", "issued_to": "<who or what may act under it>", "notes": "<caveats, supersessions, provenance>"}
```

Rules that make the format trustworthy:

- **Id dated by issuance.** `G-YYYYMMDD-NN`; next `NN` for a date = highest existing plus one.
- **Wording is verbatim or null.** Never paraphrase-as-quote. No verbatim available means `wording: null` and `source` carries the pointer.
- **Source is required.** A grant with no pointer is a rumor.
- **Status flips, never deletions.** Revoking or expiring a grant flips `status` in place and appends a dated reason to `notes`. Lines are never deleted or reordered; the ledger is append-plus-flip only.
- **Supersede forward.** New grant line first, then `superseded by G-...` in the old line's `notes`, then flip the old status once it authorizes nothing.

Optional machine fields (`grant_type`, `applies_to`, `paths`, `until`) exist for merge-authority grants; they do nothing unless your merge gate reads them. See the Phase 2 section of [docs/authority-ledger.md](../docs/authority-ledger.md) before adding any.

## Two example lines

```
{"id": "G-20260105-01", "date": "2026-01-05", "scope": "EXAMPLE, delete: apply additive, idempotent DDL (ADD COLUMN IF NOT EXISTS, CREATE TABLE IF NOT EXISTS) to the analytics warehouse without a per-change ask", "wording": null, "source": "Operator ruling, session 2026-01-05", "expiry": null, "status": "active", "issued_to": "all agent sessions", "notes": "Destructive DDL still needs explicit confirmation."}
{"id": "G-20260112-01", "date": "2026-01-12", "scope": "EXAMPLE, delete: merge the migration-renumber PRs label-free while every changed file sits under migrations/", "wording": "the renumber lands without me, anything else waits", "source": "PR #41 discussion", "expiry": null, "status": "active", "issued_to": "merge gate", "notes": "Synthetic example of the merge-authority shape; inert unless your merge gate reads these fields.", "grant_type": "merge-authority", "applies_to": "migration-policy", "paths": ["migrations/**"]}
```

## When to add a line

Add one the same turn the operator issues a standing permission, per the capture rule in [docs/decision-capture.md](../docs/decision-capture.md). The test: would a future session either re-ask for this permission or wrongly assume it? Then it belongs here. Do not add facts (conclusions store), one-off approvals for a single PR (the approval label already records those), or permissions you inferred rather than were given: an inferred grant is not a grant.

## Citing a grant

A PR acting under a grant adds a body line `Authority: G-YYYYMMDD-NN`. Citations are optional, but a present citation must resolve to a known active grant; the CI guard fails unknown, expired, and revoked citations, and fails any ledger it cannot fully parse.

The conclusions store holds what you know. The decisions ledger holds what was ruled. This file holds what you may do.
