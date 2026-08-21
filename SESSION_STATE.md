# SESSION_STATE.md � living handoff

> How to use this file: read it FIRST at session start. Refresh it fully when
> the operator says "checkpoint". Move finished work out so this file never
> grows into a log. Durable rules belong in CLAUDE.md, durable rulings in
> `planning/DECISIONS.md`; this file holds only the rolling state.

Last refreshed: 2026-08-21 (contradiction-proposal branch in progress)

## Current state

- Active branch: `claude/contradiction-proposals`.
- In-flight edits: a typed, proposal-only contradiction layer with exact-match,
  temporal non-overlap, evaluator failure, malformed response, and positive
  contradiction checks. The branch touches a template, so it waits for the
  approval label after CI.
- Everything through PR #70 is merged on `main`.

## What just landed

**The contradiction-proposal layer (D-18, current branch).** The engine now has
a read-only seam before mutation. Exact normalized values propose corroboration,
fully bounded disjoint validity windows propose coexistence, and ambiguous or
failed evaluation stays unknown. A positive contradiction verdict proposes
review rather than changing facts or tombstones.

## Next steps / watch

- The engine's 61 checks and the full local CI-equivalent suite are green.
  Inspect the draft PR; it needs the approval label because it changes a template.
- Atlas thread (r/AIMemory): a round-3 reply is drafted and unposted. It opens by
  conceding the correction gap and says what #67 did and did not close. Check
  whether the author replied to round 2 before posting.
- Open from the #68 audit, deliberately not guessed at: `docs/figure-citation.md`
  describes a `[fact:key]` checker that does not ship. Build it, or label it
  pattern-only. Same shape as the context-budget call, so the cheap answer is
  probably to build it.
- Issue #39 dockets the codebase-flywheel port (trigger: standing-agents
  expansion). The issue ledger also holds the synthetic-fixtures limitation.

## Pending decisions

- The figure-citation checker: build or label. See above.
- D-18 is the latest ruling (2026-08-21, contradictions are proposals before
  they are mutations).

