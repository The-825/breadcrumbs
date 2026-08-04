# Conclusions provenance fields

> Part of the companion kit for *From Archivist to Architect* (The Architect's Blueprint, Book 1).

This extends the base line format in [CONCLUSIONS_TEMPLATE.md](../CONCLUSIONS_TEMPLATE.md). It does not replace it. The base format records what was concluded; these three optional fields record where the conclusion came from, when it was last checked against reality, and which surface wrote it down.

Why bother: a conclusions store earns its keep only while its entries stay true. Code moves, data models change, and a fact verified in February can be quietly wrong by August. Without provenance, an old entry is unfalsifiable folklore: nobody can tell whether it was ever checked, or by what. With provenance, staleness becomes something a script can measure (see [conclusions_audit.py](conclusions_audit.py)).

## The three fields

All three are optional, and the extension is strictly additive: every base-format entry stays valid untouched, and the append-only rule is intact. Add the fields on new entries when you have the information at write time.

- **`src`**: pointer to the entry's origin. A PR (`"PR #23"`), a session date (`"session 2026-03-01"`), or a doc path. This is distinct from `evidence`: `evidence` is how a reader verifies the claim; `src` is how the entry got into the ledger. At creation they are often the same pointer. They diverge when, for example, a backfill pass mines an old fact out of git history: `src` is the mining pass, `evidence` is the original commit.
- **`verified`**: ISO date `YYYY-MM-DD` the claim was last checked against reality (the code, the live data, or the operator). At creation this usually equals `when`. This is the one field that may be refreshed in place on an existing entry: bumping it records a re-check of the same claim, not a rewrite of history. `what`, `when`, and `evidence` stay immutable; a claim that changed gets a new line plus `obsoleted_by` on the old one.
- **`by`**: the surface that wrote the entry. A session or agent name (`"review-session"`, `"doc-sync-agent"`), never a model identifier. Model names date fast and tell you nothing useful; the surface name tells you which workflow produced the entry, which is what you need when a whole class of entries turns out to be unreliable.

## Worked examples

Two synthetic lines (same fictional project as the base template's examples):

```
{"path": "src/sync/orders_sync.py", "when": "2026-02-14", "what": "The orders API DateUpdated field is unreliable for incremental pulls; the watermark must use DateCreated.", "evidence": "PR #23", "src": "PR #23", "verified": "2026-02-14", "by": "build-session"}
{"path": "domain", "when": "2026-03-01", "what": "A blank plan_type on the membership table means the default plan, not missing data; never count blanks as a coverage gap.", "evidence": "Operator ruling, session 2026-03-01", "src": "session 2026-03-01", "verified": "2026-06-30", "by": "review-session", "tags": ["ruling"]}
```

The second line shows a `verified` refresh: the ruling landed in March, and a June session re-checked it against the live table and bumped the date. Nothing else on the line changed.

## How the auditor uses these

[conclusions_audit.py](conclusions_audit.py) reads `verified` (falling back to `when`) and flags any entry with no check inside the re-verification window (180 days by default) as AGING, meaning re-verify before relying on it. Entries whose keyed path no longer exists are STALE regardless of dates. A refreshed `verified` date is what clears an AGING flag, so the field gives re-verification somewhere to land.

## Adoption notes

- Do not backfill provenance by guessing. A blank `src` on an old entry honestly says "origin unknown"; a guessed one lies with confidence. Backfill only what you can actually trace.
- The `verified` refresh is the single sanctioned in-place edit on the ledger. Everything else stays append-only, which is also what keeps the union merge setting safe for this file (see [union-merge.md](union-merge.md)).
- If your entries capture operator rulings as well as discovered facts, keep the routing rule from the capture doc ([docs/decision-capture.md](../../docs/decision-capture.md)): rulings are decided, conclusions are discovered, and a turn that produces both writes both.
