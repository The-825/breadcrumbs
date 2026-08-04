# Skills

Reusable rule sets for agent-assisted repos. A skill here is a paste-able rule set: a numbered list you can drop into your own agent rules file (CLAUDE.md or equivalent) or a team handbook and enforce as-is. Each file opens by naming the concrete failure the rules prevent, then gives you the block to copy. Take the whole set or cherry-pick single rules; they are written to stand alone.

| File | What it covers |
|---|---|
| [agent-session-efficiency.md](agent-session-efficiency.md) | Token-budget habits that stop an agent session from costing twice what it should, plus the operator-side counterpart. |
| [data-truth-rules.md](data-truth-rules.md) | Four rules against confidently wrong numbers: blank is not missing, signup is not activation, mirror the canonical query, sweep every source first. |
| [feature-flag-lifecycle.md](feature-flag-lifecycle.md) | The graduation ladder for user-visible features: OFF, owner-only, pilot, graduated, retired. Reversible by config, not by revert. |
| [regression-layering.md](regression-layering.md) | Catch each class of regression at the lowest layer that can catch it, from parse checks up to data-quality assertions. |
| [forward-only-migrations.md](forward-only-migrations.md) | Schema changes that only move forward: immutable numbered files, a runner that tracks applied-state, deprecation notes instead of drops. |
| [reuse-first.md](reuse-first.md) | The five-rung ladder that runs before you write new code: does it exist, is there a helper, does a dependency do it, can it be one line, then the minimum. |
| [adoption-verifier.md](adoption-verifier.md) | Verify the rules doc's own claims against the live repo (config, paths, hooks, connectors, counts, copied-kit placeholders): file the drift, never silently fix it. |
| [propose-confirm-execute.md](propose-confirm-execute.md) | The contract for any command touching real mail, files, or calendar: propose in batches, execute only what is confirmed, prefer the reversible operation, and leave the destructive tool unwired. |
