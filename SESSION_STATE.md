# SESSION_STATE.md · living handoff

> How to use this file: read it FIRST at session start. Refresh it fully when
> the operator says "checkpoint". Move finished work out so this file never
> grows into a log. Durable rules belong in CLAUDE.md, durable rulings in
> `planning/DECISIONS.md`; this file holds only the rolling state.

Last refreshed: 2026-08-21 (memory golden-corpus branch in progress)

## Current state

- Active branch: `claude/memory-golden-corpus`.
- In-flight edits: a committed five-case, fifteen-assertion retrieval corpus
  covering expected and forbidden recall, deterministic fusion, scope, both
  temporal axes, and verification-time masking, plus its CI-wired runner.
- Everything through PR #73 is merged on `main`.

## What just landed

**The memory golden corpus (D-21, current branch).** Retrieval quality now has a
versioned regression surface rather than one embedded happy path. Each case
states what must appear and what must never appear, and deterministic cases run
twice to catch unstable output.

## Next steps / watch

- Run the exam and full repo suites, inspect the diff, then publish and
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
- D-21 is the latest ruling (2026-08-21, retrieval quality is a committed
  corpus, not a demo).
