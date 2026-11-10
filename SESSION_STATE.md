# SESSION_STATE.md · living handoff

> How to use this file: read it FIRST at session start. Refresh it fully when
> the operator says "checkpoint". Move finished work out so this file never
> grows into a log. Durable rules belong in CLAUDE.md, durable rulings in
> `planning/DECISIONS.md`; this file holds only the rolling state.

Last refreshed: 2026-11-10 UTC by Claude Code
Checkpoint status: partly verified (see "Carried forward" below)
Owning repository: `The-825/breadcrumbs`
Source revisions: `origin/main` `50d7a4b`

## Recovery pointer

- Owning record: the open `ci:` PR from `claude/focused-ramanujan-1g7m5g`.
- Next action: the PR changes `ci-kit/` and `.github/workflows/`, so it waits for
  the maintainer's ship-it label after checks pass.

## Current state

- Active branch: `claude/focused-ramanujan-1g7m5g`, cut from `origin/main` `50d7a4b`.
- In flight (D-76): CI runs `ci-kit/run_guards.sh` over this repo, the intake and
  follow-up Node checks, `benchmarks/outcome-evidence/test_benchmark.py`, and a
  Python 3.9 pass of every manifest selftest. `kit_manifest_check.py` gains an
  inventory coverage check and `--run-selftests`. `guard_valid_utf8.py` is new.
  `kit.json` gains rows for the artifacts that had none.
- Checks, run locally 2026-11-10 on the branch: every command in `ci.yml` passes
  on Python 3.13, and the 3.9 floor step passes on Python 3.9.25. Not yet
  observed on a GitHub runner.
- Research and repository catalog ownership moved to `The-825/staletoast` (D-67).
  The research files under `docs/` are a read-only archive.

## What just landed

- 2026-11-10: handoff refresh, D-75 header encoding fix and docs index rows, PR #197.
- 2026-11-07: scoped App authentication for CI template sync, PR #196 (D-75).

## Next steps (in order)

1. Ship the `ci:` PR once checks pass and the label is applied.
2. `CLAUDE.md` is at 220 of 220 lines and its repo map omits `site/`, `scripts/`,
   `planning/` and `assets/`. Trim or raise the budget in the PR that next touches it.
3. `templates/memory-desk/gardener/promote.py` has no test or selftest. Add one
   or say so in its README.
4. `templates/memory-desk/` states Python 3.8+ in its README and CLI docstring.
   CI checks 3.9 and 3.11 only; align the claim or test 3.8.
5. Triage open issues that look resolved on main: #148, #106, #110, #80, #82.
   Route #154, #164, #117 and #99 to StaleToast.
6. Review the leftover `claude/*` remote branches. Issue #185 preserves four of
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
