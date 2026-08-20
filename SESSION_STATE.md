# SESSION_STATE.md · living handoff

> How to use this file: read it FIRST at session start. Refresh it fully when
> the operator says "checkpoint". Move finished work out so this file never
> grows into a log. Durable rules belong in CLAUDE.md, durable rulings in
> `planning/DECISIONS.md`; this file holds only the rolling state.

Last refreshed: 2026-08-20 (positioning rewrite landed; correction layer shipped)

## Current state

- Active branches: `claude/mem-correction-layer` (PR #67) and
  `claude/context-budget-guard` (PR #68). Both touch outside the safe set, so
  both wait for the approval label; neither self-merges.
- In-flight, uncommitted edits: none.
- Everything through PR #66 is merged.

## What just landed

**The positioning rewrite (D-14, then D-15, PRs #62 and #63).** The repo's axis
moved twice in one day. It was "remembering at all", became "auditable memory",
and ended at **governed memory**, which is where it stands. The forcing function
was Letta's Context Repositories (February): agent memory as git-backed files,
funded and maintained. That makes "can you read what your agent believes" a
solved, one-command problem, so auditability is table stakes rather than a
position. What is not solved is the process half: who was allowed to write this,
what had to be true before the write was accepted, and whether a correction
provably landed. `docs/versioning-is-not-governance.md` is the argument.

**The operational half (PR #64).** `docs/governing-agents-that-act.md`, published
deliberately rather than kept private, covering what to log, what an agent may
never decide alone, and a self-assessment.

**Memory-that-survives-the-session wave (PRs #65, #66).** The cue-placement
ladder (five rungs, plus the promotion rule), the skill-invocation gap, and two
upgrades to the watch pattern including the rule-6 label it was missing.

**The correction layer (PR #67, open).** `mem` gains `reject` (tombstone with a
mandatory reason, plus a must-not-come-back test in `check`) and `recheck`
(drift by evidence: source commit date beats the calendar). This closes the gap
the Atlas self-audit named against this repo's own desk kit. Tests 24 to 37.

**Claim-to-code sweep (PR #68, open).** Ships the context-budget guard that
`docs/context-budget.md` already claimed existed, plus `CONTEXT_BUDGET.md` as
the real manifest. Labels seven pattern-only docs. D-16 makes the ships-or-not
label a contract rather than a habit.

## Next steps / watch

- **PRs #67 and #68 need the approval label.** Both are outside the safe set.
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
