# Conclusions store template

> Part of the companion kit for *From Archivist to Architect* (The Architect's Blueprint, Book 1).

Every session that re-derives a known fact pays for it twice: once in tokens, once in the risk of deriving it differently this time. The worst case is a session that contradicts a settled ruling because it never saw it. The conclusions store is a machine-readable file of settled knowledge (`CONCLUSIONS.jsonl`, one JSON object per line, keyed to the file or domain it concerns) that gets read or injected at session start, so future sessions inherit what this one proved. It is distinct from the decisions ledger: decisions are operator rulings; conclusions are anything a session discovered that would take real time to re-derive.

## The line format

```
{"path": "<repo-relative path, or 'domain' | 'operations' | 'process'>", "when": "<ISO date the conclusion was reached>", "what": "<one sentence, the durable fact, specific over general>", "evidence": "<PR #, commit SHA, or doc pointer so a reader can verify>"}
```

Optional fields: `tags` (array of strings) and `obsoleted_by` (pointer to the superseding entry; wrong entries get superseded, the store stays additive).

Three example lines:

```
{"path": "src/sync/orders_sync.py", "when": "2026-02-14", "what": "The orders API DateUpdated field is unreliable for incremental pulls; the watermark must use DateCreated.", "evidence": "PR #23"}
{"path": "domain", "when": "2026-03-01", "what": "A blank plan_type on the membership table means the default plan, not missing data; never count blanks as a coverage gap.", "evidence": "Operator ruling, session 2026-03-01"}
{"path": "dashboards/revenue.sql", "when": "2026-03-19", "what": "The revenue dashboard nets out refunds at query time; reconciling against the raw orders table without netting will always read high.", "evidence": "commit 8f2c1d0"}
```

## Extended fields: relations, observation typing, dated supersession

Three more optional fields. All additive, same discipline as the base fields: every
existing line stays valid untouched, and adding these is index maintenance, not a
rewrite of history.

**`relates_to`**: an array of path keys this entry is meaningfully connected to but
does NOT supersede. Distinct from `obsoleted_by`, which means "this fact replaced
that one." `relates_to` means the entry reads better next to that other one, for
example a bug-class entry pointing at the ruling that created the behavior it broke.
Add it only when the connection is worth recording, not as a general-purpose
cross-tagging field; if every entry in a topic area would end up listing every other
one, that is a plain path grep's job, not a relation.

**`tags` read as observation typing**: the field already exists for free-form labels;
reading it as a small typed vocabulary catches most of the value with no new field.
Prefer these values when an entry fits one:

| Tag | Meaning |
|---|---|
| `ruling` | An operator decision |
| `gotcha` | A trap a session fell into |
| `bug-fix` | A bug class plus its fix |
| `threshold` | A numeric constant and its rationale |
| `deferred` | Scoped out, intentionally not done yet |
| `design` | An architectural choice |

This is a preference list, not a closed enum. Free-form tags stay allowed for
anything that doesn't fit, and existing free-form tags are not retrofitted to the
vocabulary above.

**Dated supersession** (`obsoleted_by` becomes entry-precise and dated): so "what did
we believe as of date X" is a field filter instead of git archaeology.

- Pointer grammar for `obsoleted_by`: `path`, `path@date`, or `path@date#n`.
  - `path` (the original form): the knowledge was absorbed by a document; still
    valid, but carries no date.
  - `path@date`: resolves to the entry keyed `(path, when=date)` when exactly one
    exists, otherwise to the document at `path` with `date` as the effective
    supersession date.
  - `path@date#n`: the nth entry (1-based, file order) among same-path-same-date
    entries, for the collision case, since the store is append-only and file order
    is therefore stable.
- **`supersedes`** (new, optional, on the NEWER entry only): a pointer, same
  grammar, to the entry it replaces. The back half of the pair; `obsoleted_by` on
  the old line is the forward half. Recording both keeps grep-locality, finding
  either line reveals the supersession, and lets a curation pass check symmetry: a
  `supersedes` pointer whose target lacks a matching `obsoleted_by` is a flag.
- **Believed-as-of-X** becomes a per-entry filter once both halves are recorded:
  believed at X iff `when <= X` and (no `obsoleted_by`, or its date is absent or
  later than X). No query tooling is required to get this; it is a one-line filter
  over the JSONL whenever an as-of question actually comes up.

The shipped auditor (`ledger-tools/conclusions_audit.py`) predates this dated
grammar and treats `path@date` / `path@date#n` pointers as unresolved; a curation
pass or a future auditor update handles them.

Any retrieval or boot-injection logic built on top of this file should treat an
entry carrying `obsoleted_by` as excluded from "current knowledge": superseded, not
current, however recently it was written.

Line format with the extended fields (illustrative shape, not a filled example):

```
{"path": "<repo-relative path, or a domain/datastore identifier>", "when": "<ISO date>", "what": "<one sentence>", "evidence": "<PR #, commit SHA, or doc pointer>", "tags": ["<ruling|gotcha|bug-fix|threshold|deferred|design, or free-form>"], "relates_to": ["<path key this entry is easier to read next to>"], "obsoleted_by": "<path | path@date | path@date#n, on the OLD entry>", "supersedes": "<path@date, on the NEW entry>"}
```

## When to add a line

Add one when the fact would take real time to re-derive, when it corrects a prior misunderstanding (new line, plus `obsoleted_by` on the old one), when it records a gotcha not obvious from the diff, or when it captures a domain fact only the operator knew. Do not add restatements of code (code is the source of truth), anything already in the rules file, or restated PR bodies (link instead).

## Curation

Promote only verified conclusions, and prune wrong ones by superseding rather than deleting. Keep the curated core small and separate from any bulk-mined archive: when one team merged a history-mined backfill of hundreds of entries into the curated file, it swamped the session-verified entries and wrecked lookup precision. The core file stays small and injection-worthy; an archive is a labeled secondary source, and entries promote only when a session actually relies on one and re-verifies it.

The rules file holds the rules. The state file holds the rolling handoff. This file holds what you now know.
