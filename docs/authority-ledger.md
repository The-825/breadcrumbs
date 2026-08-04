# The authority ledger: a durable record of what you may do

> Part of the companion kit for *From Archivist to Architect* (The Architect's Blueprint, Book 1).

An agent session runs on two kinds of settled knowledge. The first kind is facts: what is true about the code, the data, the domain. The conclusions store carries those ([templates/CONCLUSIONS_TEMPLATE.md](../templates/CONCLUSIONS_TEMPLATE.md)), and the decisions ledger carries the operator rulings behind them ([decision-capture.md](decision-capture.md)). The second kind is permissions: what the operator has authorized sessions to DO. Merge lanes, write envelopes, production toggles, build mandates. Without a durable record, every session re-asks for the same permission, or worse, assumes it. The authority ledger is that record: one JSON line per standing grant, append-only, machine-checkable.

The split is the whole idea. A ruling that says "the discount floor is 12 percent" is a fact and goes to the conclusions store. A ruling that says "you may apply forward-only DDL without asking" is a grant and goes here. When one statement carries both, capture both, each in its own file. Facts answer "what is true"; grants answer "what are we allowed to do"; conflating them is how a session quotes a fact as if it were permission.

**Age, plainly:** this is a young pattern. The ledger practice was adopted mid-July 2026 and had about a week of production use behind it when this kit was published. The Phase 2 merge-authority extension below is newer still, days old at publication. It ships early, with its guard, because the shape is simple and the guard proves itself against fixtures; treat the base ledger as settled-enough-to-copy; Phase 2's gate code ships in this kit now that its upstream wiring has production mileage behind it.

## What ships in this kit

| Piece | Path |
|---|---|
| This pattern doc | `docs/authority-ledger.md` |
| Schema quick reference | [templates/AUTHORITY_LEDGER_TEMPLATE.md](../templates/AUTHORITY_LEDGER_TEMPLATE.md) |
| Synthetic starter ledger | [templates/authority_ledger.jsonl](../templates/authority_ledger.jsonl) |
| CI citation guard | [ci-kit/guards/guard_authority_citations.py](../ci-kit/guards/guard_authority_citations.py) |
| Same-turn capture command | [templates/commands/grant.md](../templates/commands/grant.md) |
| Phase 2 gate wiring | authority-ledger block in [ci-kit/workflows/decision_script.py](../ci-kit/workflows/decision_script.py), tested in `ci-kit/workflows/tests/` |

## Schema (one JSON object per line)

| Field | Type | Meaning |
|---|---|---|
| `id` | string | `G-YYYYMMDD-NN`. The date part is the date the grant was ISSUED; `NN` is a two-digit sequence within that date (01, 02, ...). |
| `date` | string | Same date as the id, `YYYY-MM-DD`. |
| `scope` | string | What the grant permits, specific enough that a guard or a reviewer can tell whether an action falls inside it. |
| `wording` | string or null | The operator's VERBATIM words, only when the cited source contains a true verbatim quote. Never invent a quote and never paraphrase-as-quote; when no verbatim exists, this is `null` and `source` carries the pointer. |
| `source` | string | REQUIRED pointer to where the grant is recorded: a rules-file section, a PR number, a decisions-ledger entry, a session plus date. |
| `expiry` | string or null | `YYYY-MM-DD` end date, or `null` for a standing grant. |
| `status` | string | `active`, `expired`, or `revoked`. |
| `issued_to` | string | Who or what may act under the grant (all sessions, a named workflow, one build session). |
| `notes` | string | Caveats, supersessions, backfill provenance. |

The verbatim-or-null rule on `wording` deserves its own sentence. A paraphrase presented as a quote is a fabricated quote, and a fabricated quote in a permissions record is exactly the failure the ledger exists to prevent. When you have the operator's words, keep them exactly; when you do not, say so with `null` and let `source` do the work.

## ID convention

`G-YYYYMMDD-NN`, dated by issuance. The next `NN` for a date is the highest existing `NN` for that date plus one. A backfilled grant whose exact issue date is not recoverable anchors its id to a dated event in the cited source and says so in `notes`; the pointer chain in `source` is the real provenance.

## Lifecycle

- **Issue.** The `/grant` command appends a validated line the same turn the grant lands, per the same-turn capture rule ([decision-capture.md](decision-capture.md)). It computes the next id, requires a source, and refuses non-verbatim wording.
- **Revoke or expire.** A status flip in place (`active` to `revoked` or `expired`), with a dated reason appended to `notes`. **Lines are never deleted.** The ledger is append-plus-flip only. A deleted grant line is a hole in the audit trail; a flipped one is a record of the permission AND its end.
- **Supersede.** Issue the new grant, then note the forward pointer on the old one (`superseded by G-...` in `notes`) and, once the old grant no longer authorizes anything, flip its status.

## Citing a grant

A PR acting under a grant cites it in the PR body with a line of the form:

```
Authority: G-20260105-01
```

One citation per line; multiple `Authority:` lines are allowed. Citations are optional in v1 (the guard is non-breaking by design), but a citation that IS present must resolve to a known, active grant. The citation line is cheap to write and it turns "was this authorized?" from an archaeology project into a grep.

## What the guard enforces

[ci-kit/guards/guard_authority_citations.py](../ci-kit/guards/guard_authority_citations.py) runs three ways:

- **CI mode (default).** Reads the PR body from the GitHub event payload. Every `Authority: G-...` citation must resolve to a known, non-expired, non-revoked grant; an unknown, expired, or revoked citation fails the run. Zero citations pass (v1 is non-breaking), and events without a PR body (push, manual dispatch) pass the citation check. Every run also checks ledger integrity: each line must parse as JSON with the required fields, a well-formed id, a known status, and no duplicate ids. Any integrity error fails the run, citations or not: a ledger you cannot parse is a ledger you cannot trust, so the guard fails closed on it.
- **`--sweep`.** Report-only: lists grants already expired or expiring within 14 days, for a periodic review. Always exits 0.
- **`--selftest`.** Offline fixtures covering valid, unknown, expired, revoked, no-citation, and malformed-ledger cases. No network, no repo state.

Wiring is one step in any PR workflow:

```yaml
- name: Authority citations valid
  run: python3 ci-kit/guards/guard_authority_citations.py
```

In this repo the guard's tests ride the existing `Kit self-tests` job (unittest discovery over `ci-kit/guards/tests/`), so the guard proves it bites its bad fixtures on every PR here without any workflow edit.

## Relationship to the approval label

The ledger records durable grants; the operator's approval label (the `<approval-label>` in [ci-kit/workflows/decision_script.py](../ci-kit/workflows/decision_script.py)) stays the per-PR release mechanism. The two are complements, not rivals: the label says "merge this one", a grant says "this class of action is pre-authorized". In the base pattern the ledger never touches merging at all; it is documentation with a validity check. Phase 2, below, is the contract for the day you want a grant to stand in for the label at narrow, named points.

## Phase 2: merge-authority grants (contract + gate code)

**Status: shipped.** The production system this kit is extracted from wired these fields into its merge gate first; this kit held the contract doc-only until that wiring had production mileage, and now carries the gate code as an extension of the decision script ([ci-kit/workflows/decision_script.py](../ci-kit/workflows/decision_script.py), the authority-ledger block, unit-tested in `tests/test_decision_script.py`; read [ci-kit/workflows/AUTOMERGE_GOTCHAS.md](../ci-kit/workflows/AUTOMERGE_GOTCHAS.md) first). Grants are inert until you configure them: set `LEDGER_REL_PATH` to your ledger, name `PROMOTION_HEADS` if you run a promotion lane, and pass the PR body via `--pr-body-file`.

### Machine fields (optional, on top of the base schema)

| Field | Type | Meaning |
|---|---|---|
| `grant_type` | string | Only `"merge-authority"` affects merging. Absent or anything else: the grant is documentation, cited or not. |
| `applies_to` | string | Names the ONE wait site the grant can clear: `"content-policy"` (a path-scoped clear of a content-policy wait; a migrations lane is the worked example) or `"promotion"` (a dated window for a promotion head branch). |
| `paths` | list of globs | Required for path-scoped grants: EVERY changed file in the citing PR must match at least one glob, or the grant does not apply. |
| `until` | `YYYY-MM-DD` | Required for window grants: the grant is a dated window, `date`..`until` inclusive, evaluated in the operator's timezone. Optional end-bound otherwise. |

### The contract

- **A grant clears a WAIT, never a failing check.** Green CI, non-draft, clean mergeable state, and every other gate apply unchanged. The gate's `wait` verdict at a named site is the only thing a citation can convert; a `fail` is never negotiable by citation.
- **The gate reads the ledger from the BASE branch, never the PR head.** A PR cannot mint or edit the grant that merges it.
- **Citations are read from the frozen event payload, same as labels.** A citation added by editing the PR body takes effect on the PR's next event (new commit, label toggle, ready-for-review).
- **The machinery set is never grant-overridable.** A PR whose diff touches the merge gate's own moving parts (the decision script, the automerge and labeler workflows, the settings file that scopes tokens) waits for the operator's label regardless of any citation, hardcoded in gate logic, not just documented. An agent PR must never merge its own merge gate under a grant.
- **Fail-closed ledger handling.** An unreadable ledger, a non-JSON line, a malformed or duplicate id, a missing required machine field, or an unparseable date all evaluate as no-grant: the wait stands. The gate never crashes into a merge.
- **Audit chain.** When the gate clears a wait under a grant it posts one deduplicated PR comment, `Merged under Authority: G-... (scope: ...)`. The comment is audit, not gate: a failed post is logged and the merge proceeds.

### Worked examples (shape only, synthetic)

A path-scoped grant:

```json
{"id": "G-20260801-01", "date": "2026-08-01", "scope": "renumber migrations 300-310 per the documented exception", "wording": null, "source": "example", "expiry": null, "status": "active", "issued_to": "merge gate", "notes": "", "grant_type": "merge-authority", "applies_to": "migration-policy", "paths": ["migrations/**"]}
```

A PR whose migration renumber trips the migration-policy wait cites `Authority: G-20260801-01` in its body and merges label-free on green, provided every changed file sits under `migrations/`.

A window grant:

```json
{"id": "G-20260801-02", "date": "2026-08-01", "scope": "auto-promote staging to main during the operator's travel week", "wording": null, "source": "example", "expiry": null, "status": "active", "issued_to": "merge gate", "notes": "", "grant_type": "merge-authority", "applies_to": "promotion", "until": "2026-08-08"}
```

While 2026-08-01 through 2026-08-08, the staging-to-main promotion PR cites `Authority: G-20260801-02` and merges on green without the label, unless the batch touches a protected path (then the label is required as always).

## Generalizing the pattern

You may already have one grant family formalized somewhere: a flag-activation schedule with dates and conditions, a standing "auto-apply additive DDL" note in your rules file, a "this workflow may commit directly" carve-out. The ledger is the same idea for every other kind of standing permission, in one place, with one schema and one guard. Leave an existing well-working grant family where it lives; route everything new here rather than growing a third and fourth format.

## Adopting

1. Copy [templates/authority_ledger.jsonl](../templates/authority_ledger.jsonl) to your repo (conventionally the repo root or your engineering docs directory), delete the self-labeled example lines as your first real grants land.
2. Copy [ci-kit/guards/guard_authority_citations.py](../ci-kit/guards/guard_authority_citations.py), set its ledger path (configuration block at the top, or the `AUTHORITY_LEDGER_PATH` env var), and add the one workflow step above.
3. Install [templates/commands/grant.md](../templates/commands/grant.md) as `/grant` so capture is same-turn instead of aspirational.
4. Add the citation convention to your rules file: PRs acting under a grant cite it with an `Authority:` line.

Skip Phase 2 until the base habit sticks. A ledger nobody cites is still useful documentation; a merge gate reading a ledger nobody curates is a hazard.
