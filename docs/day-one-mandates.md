# Day-one mandates

> Part of the companion kit for *From Archivist to Architect* (The Architect's Blueprint, Book 1).

Every practice on this list is cheap on day one and expensive as a retrofit. The pattern behind all of them is the same: adopted early, the practice shapes everything that follows for free; adopted late, it has to fight everything that already exists, and usually arrives right after the incident that proves it was needed. A clean-slate repo adopts the whole list before the first feature.

Each mandate names the retrofit pain it avoids. The phased version of this list, with exit criteria and gates, is [templates/BLUEPRINT_TEMPLATE.md](../templates/BLUEPRINT_TEMPLATE.md); the founding-docs version is [four-founding-docs.md](four-founding-docs.md).

## The mandates

**1. CI from the first commit.** A gate added months in inherits a codebase full of existing violations, so it launches with grandfathered exceptions and never fully closes. A gate added at commit one never lets the first violation in. The runnable version is in [`ci-kit/`](../ci-kit/), including the self-tests that prove each guard actually bites.

**2. The decisions ledger from day one.** Rulings made before the ledger exists live in transcripts, and transcripts evaporate. The debate you settled in week two gets rerun in month four, sometimes landing the opposite way. Template: [DECISIONS_TEMPLATE.md](../templates/DECISIONS_TEMPLATE.md).

**3. Feature flags before features.** The first feature that misbehaves in production gets rolled back by git revert instead of switched off by config, taking whatever shipped with it. Retrofitting flags later means reopening every feature already shipped without one. Flags are infrastructure; they exist before the first thing they gate. See [skills/feature-flag-lifecycle.md](../skills/feature-flag-lifecycle.md).

**4. Forward-only migrations.** The first schema rollback that drops a column takes data with it, and the convention adopted after that loss is a memorial. Adopted before, it is a guardrail: add columns, deprecate in place, never roll back. See [skills/forward-only-migrations.md](../skills/forward-only-migrations.md) and the runner in [`ci-kit/migrations/`](../ci-kit/migrations/).

**5. The numbered issue ledger.** Without one, known problems get rediscovered from scratch, each time at full diagnosis cost, and quietly dropped fixes leave no trace. A numbered entry (`KI #<n>`: date, evidence, status, moved to Resolved with the fix reference) turns "haven't we seen this before" into a lookup. The ledger section is built into [CLAUDE_TEMPLATE.md](../templates/CLAUDE_TEMPLATE.md).

**6. The session handoff file.** Without it, every new session or teammate reconstructs where things stand from git archaeology, so mid-flight work gets finished twice or dropped entirely. One living file holding the active branch, in-flight work, and next steps, refreshed on a trigger word. Template: [SESSION_STATE_TEMPLATE.md](../templates/SESSION_STATE_TEMPLATE.md).

**7. A parity contract when replacing an existing system.** Rebuilds fail by silently dropping the capability nobody remembered, discovered only after the old system is off, when recovering it is an emergency. Inventory every old capability as a row before writing code; check rows with evidence. Template: [PARITY_TEMPLATE.md](../templates/PARITY_TEMPLATE.md).

**8. An in-process test harness before the first route.** Adopted at route one, a harness that boots the real app with only the I/O edges faked makes every later route testable by default. Adopted at route one hundred, it competes with a feature backlog and loses, so the routes stay testable only by deploy-and-click. Skeleton: [templates/test-harness/](../templates/test-harness/README.md).

**9. Record significant choices as ADRs.** A year in, nobody can explain the warehouse layout or the auth model, so the next rebuild re-litigates both from zero. One page per decision, written the day it lands, is the entire cost. Template: [ADR_TEMPLATE.md](../templates/ADR_TEMPLATE.md).

## Starter checklist

Copy this into your repo's first issue or first PR description and check it off before the first feature merges.

```markdown
## Day-one checklist

- [ ] CI workflow gates every PR (parse checks + lint guards), live from the
      first commit, with each guard proven to fail a bad fixture
- [ ] `DECISIONS.md` exists and carries D-1 (the decision to start, with why)
- [ ] Feature-flag store is live and fail-closed, before the first feature
- [ ] Migration rule written down: forward-only, numbered files, applied
      through a runner that refuses duplicates and out-of-order apply
- [ ] Known-issues ledger section exists in the rules file (`KI #<n>` format)
- [ ] `SESSION_STATE.md` exists and the refresh trigger word is agreed
- [ ] Parity inventory filled across every bucket (replacements only), or
      "no predecessor" recorded in one line
- [ ] Test harness boots the real app in CI, before the first route merges
- [ ] `docs/adr/` exists with the template, and ADR-1 is written
```

Nine checkboxes, one afternoon. The alternative is adopting each item later, one incident at a time, at retrofit prices.
