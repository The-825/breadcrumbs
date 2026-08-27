# SESSION_STATE.md · living handoff

> How to use this file: read it FIRST at session start. Refresh it fully when
> the operator says "checkpoint". Move finished work out so this file never
> grows into a log. Durable rules belong in CLAUDE.md, durable rulings in
> `planning/DECISIONS.md`; this file holds only the rolling state.

Last refreshed: 2026-08-27 (cooperative evaluation protocol pass)

## Current state

- Active branch: `claude/cooperative-evaluation-protocol`, cut from current `main`.
- Merged in PR #86: a host-bound context service derives memory clearance from
  an authenticated principal and fixed policy. Requests cannot assert or widen
  audience, and ungranted principals fail closed.
- The low-level memory engine, golden exam, and new scope-gate selftest pass.
- The cooperative-intelligence vision is documented as a public research and pattern
  layer. It does not import private implementation material or claim that research has
  validated a live system.

## In flight

**Cooperative evaluation protocol (D-31).** A public, pattern-only method and owning
repository template now evaluate orientation, handoff, correction, ownership, and
recovery separately from throughput, quality, cost, and burden. The kit adds no runtime
evaluator, score, or authority.

## What just landed

**A2A score export and work-governance related work (D-27).** Both are merged on
`main`. Breadcrumb Score remains evidence-scoped and publication-gated.

## Next steps / watch

- Run the evaluation template in an owning system with a safe, bounded work item. Do not
  promote the candidate work-allocation or multi-agent capabilities into shipped claims
  without matched, consequential, privacy-constrained tests that compare against the
  better individual baseline.
- Request an independent Atlas rerun when the maintainer is ready to contact Simon.
- Keep the first repository self-assessment private until independent review
  and a specific publication approval exist.
- Atlas follow-up: contact Simon for an independent rerun only after the scope
  gate is merged and publicly inspectable.
  Keep the 2026-08-12 self-audit pinned as historical evidence rather than
  silently rewriting it to match current main.
- `docs/figure-citation.md` is labeled pattern-only. Building its checker
  remains a separate feature decision.
- Issue #39 dockets the codebase-flywheel port. The issue ledger also holds the
  synthetic-fixtures limitation.

## Pending decisions

- The figure-citation checker: build or label. See above.
- D-28 is the latest ruling (2026-08-24, scope is derived from trusted
  identity).
