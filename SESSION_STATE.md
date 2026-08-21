# SESSION_STATE.md · living handoff

> How to use this file: read it FIRST at session start. Refresh it fully when
> the operator says "checkpoint". Move finished work out so this file never
> grows into a log. Durable rules belong in CLAUDE.md, durable rulings in
> `planning/DECISIONS.md`; this file holds only the rolling state.

Last refreshed: 2026-08-21 (forgetting-closure branch in progress)

## Current state

- Active branch: `claude/forgetting-closure`.
- In-flight edits: the memory-desk gardener consults rejected-value tombstones
  before promotion, with negative tests proving a re-derived rejected answer
  never changes the index. This branch touches templates and waits for the
  approval label after CI.
- Everything through PR #71 is merged on `main`.

## What just landed

**The forgetting-closure layer (D-19, current branch).** The gardener now treats
negative memory as a pre-write guard. A retained source or fresh capture cannot
re-promote the same normalized key and answer after the operator rejected it;
the index remains byte-for-byte unchanged and the refusal is reported.

## Next steps / watch

- Run the gardener and full repo suites, inspect the diff, then publish and
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
- D-19 is the latest ruling (2026-08-21, negative memory guards derivation
  before it guards CI).
