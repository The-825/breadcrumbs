# Context budget

The line budgets for this repo's boot set, in one table, parsed by
`ci-kit/guards/guard_context_budget.py` on every run of `ci-kit/run_guards.sh`.
Over budget fails the build. The pattern and the reasoning behind it are in
[docs/context-budget.md](docs/context-budget.md); this file is the worked
instance of it, the numbers that actually bind here.

Raising a budget is allowed in the same PR that needs it, with a reason in the
Notes column. Shrinking one when a restructure lands is the ratchet: run
`python3 ci-kit/guards/guard_context_budget.py --report` to see the headroom
each file is currently carrying.

| File | Class | budget_lines | Notes |
|---|---|---:|---|
| `CLAUDE.md` | kernel | 220 | Binding rules plus the repo map. Reference detail routes to docs/. |
| `SESSION_STATE.md` | handoff | 90 | Rolling handoff; refreshed on checkpoint, never accumulated. |
| `llms.txt` | router | 130 | The agent-facing map. Route by problem, one line per destination. |

Not budgeted, deliberately: `README.md` (a reader lands on it by choice, it is
not attached to every session) and `kit.json` (machine inventory, read by tools
rather than loaded into a window). Routed docs are unbudgeted by design; the
discipline for them is reachability, not size.
