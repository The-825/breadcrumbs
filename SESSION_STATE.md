# SESSION_STATE.md · living handoff

> How to use this file: read it FIRST at session start. Refresh it fully when
> the operator says "checkpoint". Move finished work out so this file never
> grows into a log. Durable rules belong in CLAUDE.md, durable rulings in
> `planning/DECISIONS.md`; this file holds only the rolling state.

Last refreshed: 2026-08-10 (rubric completions; engine at valid-at + audience scoping)

## Current state

- Active branch: none in flight; #27 through #40 all merged (#34 checkpoint,
  #36 SESSION_STATE safe-set, #37 budget loans + skills rule 10, #38 docs
  ports, #40 rubric completions).
- Open PR: none.
- In-flight, uncommitted edits: none.

## What just landed (2026-08-10, merged)

- Rubric completions (#40): valid-at windows (`build_context(valid_at=)`,
  composing with `as_of` for the two-clock query) and audience scoping
  (public/internal/regulated, fail closed at assembly). The selftest caught a
  real leak (supersession episodes embed prior values), so any audience
  filter omits the unscoped episodic tier entirely, stated in the header.
  With #29's tombstones this closes every code-shaped Atlas rubric gap.
- Cross-repo ports (#37/#38): budget loans tool + red-first skills rule;
  trap-fixtures essay, raise-is-a-loan section, one-review-queue rule.
- SESSION_STATE joined the tier safe set (#36, D-13): checkpoint refreshes
  merge on green unlabeled (this PR is the proof).

## Prior landing (2026-08-09, all merged)

- Memory desk kit (#27, `templates/memory-desk/`), with its CI gate step.
- Agent Memory Atlas round-2 fixes (#28): same-value `store_fact()` no longer
  demotes verified; `kit_manifest_check` fails when a manifest-listed selftest
  is absent from ci.yml.
- Rejected-value tombstones + as-of (learned-at) replay in the memory engine
  (#29), closing two rubric gaps the Atlas named.
- Tiered merge gate (#30, D-12): docs-class PRs (docs/, checklists/, README,
  decisions ledger; no deletions/renames) merge on green with NO label;
  everything else keeps `greenlight`. Policy `ci-kit/workflows/greenlight_tiers.py`;
  the gate runs the base branch's copy. First live proof: #33 merged unlabeled.
- README: banner (#31, arrow fix #32), the doing-over-thinking second goal in
  "The token angle" (#31), and the concurrent-sessions collision story (#33).

## Next steps / watch

- The operator POSTED the reply to the Atlas author's r/AIMemory thread
  (2026-08-09). Watch the thread; the open question put to the author is what
  an honest anonymized real-shape fixture for the forbidden check looks like.
- Issue ledger still carries: scope-enforced retrieval (declined with reasons)
  and the synthetic-fixtures limitation.
- Obsolete remote branch for the operator to delete in the GitHub UI:
  `claude/preflight-overlap-check` (content fully contained in main).

## Pending decisions

- None. D-12 was the day's ruling and is in the ledger.
