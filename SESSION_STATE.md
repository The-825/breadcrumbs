# SESSION_STATE.md � living handoff

> How to use this file: read it FIRST at session start. Refresh it fully when
> the operator says "checkpoint". Move finished work out so this file never
> grows into a log. Durable rules belong in CLAUDE.md, durable rulings in
> `planning/DECISIONS.md`; this file holds only the rolling state.

Last refreshed: 2026-08-20 (retrieval-fusion branch ready for review)

## Current state

- Active branch: `claude/memory-retrieval-fusion`.
- In-flight edits: stable episode handles, fact-to-episode source links,
  deterministic reciprocal-rank fusion, tests, and index updates. The branch
  touches templates and `kit.json`, so it waits for the approval label after CI.
- Everything through PR #69 is merged on `main`.

## What just landed

**The retrieval-fusion layer (D-17, current branch).** The existing engine
already shipped bi-temporal replay, audience scoping, oracle-gated verification,
supersession, and tombstones. This branch adds stable episode handles, refuses
made-up source references, lets facts cite exact source episodes, and fuses
lexical, action/tag, and recency ranks without adding a database. A second review
made repeated evidence accumulate without demoting a verified fact and preserved
old and new source links inside supersession events. All 54 engine checks and the
repo's guard, migration, workflow, manifest, retrieval, audit, and preflight
self-tests pass locally.

## Next steps / watch

- Commit, push, and open the retrieval-fusion PR. It needs the approval label
  after CI because it changes a template and `kit.json`.
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
- D-16 was the last ruling (2026-08-20, D-3 gets a mechanical check and a stated
  default).

