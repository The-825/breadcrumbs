# Checklists

Operational checklists, ready to run as-is. Each is tied to a moment in the work: run `pr-discipline.md` before opening a PR, `pre-push.md` before every push, and `continuity-sweep.md` after any change to a fact that other surfaces cite. Each one takes under two minutes; each one exists because skipping it has a documented cost.

| File | What it is |
|---|---|
| [pr-discipline.md](pr-discipline.md) | Pre-open checklist for PR shape: one concern, the ~500-line split question, intent-tagged titles, feature-slug branches, the scope-forcing body template. |
| [pre-push.md](pre-push.md) | Verify-before-push: re-read the diff, run the cheapest covering check, confirm scope. Includes the change-type to check table. |
| [continuity-sweep.md](continuity-sweep.md) | After-change sweep: drift check (every citing surface matches the canonical source) plus completeness check (surfaces that should now reflect the change and do not). |
