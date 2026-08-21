# SESSION_STATE.md · living handoff

> How to use this file: read it FIRST at session start. Refresh it fully when
> the operator says "checkpoint". Move finished work out so this file never
> grows into a log. Durable rules belong in CLAUDE.md, durable rulings in
> `planning/DECISIONS.md`; this file holds only the rolling state.

Last refreshed: 2026-08-21 (consolidation-proposal branch in progress)

## Current state

- Active branch: `claude/consolidation-proposals`.
- In-flight edits: possible semantic duplicates become stable, typed,
  idempotent proposal records preserving candidate and existing lineage. The
  proposal queue is review-only and no memory is merged automatically.
- Everything through PR #72 is merged on `main`.

## What just landed

**The consolidation-proposal layer (D-20, current branch).** The gardener's
semantic-overlap warning now has a durable, machine-readable review surface.
Stable ids make retries idempotent, both source rows remain inspectable, and
proposal creation carries an explicit `mutates: false` contract.

## Next steps / watch

- Run the gardener and full repo suites, inspect the diff, restore the
  executable bit lost during the prior connector publish, then publish and
  greenlight under the operator's standing instruction.
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
- D-20 is the latest ruling (2026-08-21, consolidation starts as a durable
  proposal).
