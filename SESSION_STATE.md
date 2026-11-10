# SESSION_STATE.md · living handoff

> How to use this file: read it FIRST at session start. Refresh it fully when
> the operator says "checkpoint". Move finished work out so this file never
> grows into a log. Durable rules belong in CLAUDE.md, durable rulings in
> `planning/DECISIONS.md`; this file holds only the rolling state.

Last refreshed: 2026-11-10 UTC by Claude Code
Checkpoint status: partly verified (see "Carried forward" below)
Owning repository: `The-825/breadcrumbs`
Source revisions: `origin/main` `28749d5`

## Recovery pointer

- Owning record: the open PR from `claude/focused-ramanujan-1g7m5g`.
- Next action: ship that PR, then open the `ci:` follow-up listed under next steps.

## Current state

- Active branch: `claude/focused-ramanujan-1g7m5g`, cut from `origin/main` `28749d5`.
- In flight: a docs-only refresh. This handoff, the D-75 header encoding in
  `planning/DECISIONS.md`, two missing rows in `docs/README.md`, and the README's
  description of the research archive.
- Checks on `28749d5`, run locally 2026-11-10: guard, migration, workflow and site
  unit tests, `ci-kit/run_guards.sh`, `kit_manifest_check.py`, the five `scripts/`
  `--check` commands and the memory-desk check all pass.
- Research and repository catalog ownership moved to `The-825/staletoast` (D-67).
  The research files under `docs/` are a read-only archive. The archived landscape
  holds 335 assessed repositories (`scripts/repository_landscape.py --check`).
- Latest ruling: D-75, sync publishing scoped to an explicit GitHub App.

## What just landed

- 2026-11-07: scoped App authentication for CI template sync, PR #196 (D-75).
- 2026-11-04: Pages release serialization (#195), the local intake and follow-up
  example (#189), unified ship-it delivery guidance (#194, D-74), the book
  companion entry point (#193) and the outcome-evidence experiment (#192, D-70).

## Next steps (in order)

1. Ship the docs refresh PR.
2. Open one `ci:` PR from the 2026-11-10 codebase review:
   - Make `kit_manifest_check.py` fail when a shipped artifact is not inventoried.
     `templates/memory-desk/`, `templates/intake-follow-up/` and the ADR, incident,
     blueprint and parity templates are absent from `kit.json` and `llms.txt`.
   - Run the `templates/intake-follow-up/` JavaScript tests and
     `benchmarks/outcome-evidence/test_benchmark.py` in CI.
   - Add a UTF-8 guard to `ci-kit/run_guards.sh`. The D-75 header reached main
     with invalid bytes and nothing caught it.
   - Test Python 3.9, or change the "Python 3.9+" claims in `kit.json`. CI runs 3.11.
3. `CLAUDE.md` (220 of 220) and `llms.txt` (130 of 130) have no budget headroom, and
   the `CLAUDE.md` repo map omits `site/`, `scripts/`, `planning/` and `assets/`.
   Trim or raise the budget in the PR that next touches either file.
4. Triage open issues that look resolved on main: #148, #106, #110, #80, #82.
   Route #154, #164, #117 and #99 to StaleToast.
5. Review the leftover `claude/*` remote branches. Issue #185 preserves four of
   them as frozen heads; confirm with the maintainer before deleting any.

## Carried forward, not re-verified this refresh

These came from the 2026-09-11 handoff. Confirm each before acting on it.

- Run the evaluation template in an owning system before promoting any
  work-allocation or multi-agent capability into a shipped claim.
- Keep the first repository self-assessment private until independent review and
  a specific publication approval exist.
- The Atlas independent rerun waits on the maintainer. Keep the 2026-08-12
  self-audit pinned as historical evidence.
- Research follow-ups (full-text appraisal, code traces, memory exam extensions)
  now belong to StaleToast. Do not start them in this checkout.

## Pending decisions

- `docs/figure-citation.md` is pattern-only: build its checker, or leave it labeled.
- Whether the research archive moves to its own directory under `docs/`. It needs
  redirect and script path updates, so it is its own PR.
- Issue #39 dockets the codebase-flywheel port for the next standing-agents expansion.
