# Docs

Pattern essays: the reasoning behind the kit's artifacts, in this repo's own words. Read
the essay when you want to know why a piece is shaped the way it is; copy the matching
artifact from `ci-kit/`, `skills/`, `templates/`, or `checklists/` when you just want
the piece.

| Essay | Why read it |
|---|---|
| [breadcrumbs-whitepaper.md](breadcrumbs-whitepaper.md) | The working paper: cue-placement memory for agent fleets, the five mechanisms, the caught-itself case study, and the join protocol. Start here for the whole argument. |
| [context-budget.md](context-budget.md) | Price what every session auto-loads, and enforce the budget in CI so it cannot silently regrow. |
| [the-airport-model.md](the-airport-model.md) | The wayfinding idea grown up: one warehouse is a signed terminal, an institution is the airport, and the operation is reflected in code. |
| [floating-memory.md](floating-memory.md) | The airport model applied to agent memory: a git-backed memory branch, a fold protocol where completion is asserted and oracle-gated, trust-ranked decay plus use-stamped decay, and the operational sweeps (NOTAMs, MEL, orphan matching, mishandled-rate SLAs, single-threaded ownership). |
| [memory-desk.md](memory-desk.md) | The read side refined: make retrieval mechanical and maintenance intelligent. One lookup verb over a flat, gardener-maintained fact index, misses that print the next command, so the cheapest session finds settled facts without judgment calls. |
| [fleet-presence-beat.md](fleet-presence-beat.md) | Replace a self-reported status board (which rots in hours) with presence upserted at fixed moments and cross-checked against real activity. |
| [prospective-memory-watches.md](prospective-memory-watches.md) | Acting when a condition becomes true, not on a date: a checkable predicate, an intention written in advance, cheap evaluation, expensive action. |
| [memory-threat-model.md](memory-threat-model.md) | Write the threat model for a shared memory system separately from the mechanics: four failure modes, the mechanism that answers each, and an explicit extraction boundary. |
| [composite-persona-method.md](composite-persona-method.md) | Tell true stories from protected data without exposing anyone: fictional people built pattern-first from verified aggregates, with receipts. |
| [day-one-mandates.md](day-one-mandates.md) | Nine practices that are cheap at commit one and expensive as retrofits, with a starter checklist. |
| [self-improvement-loop.md](self-improvement-loop.md) | The evidence-driven loop that makes the rules compound: instrument session exhaust, retro every arc, land each lesson as exactly one artifact. |
| [specification-debt.md](specification-debt.md) | A correction you keep re-issuing means your spec is missing a rule: count across sessions, patch past three, route by correction type. |
| [artifact-correction-ledger.md](artifact-correction-ledger.md) | Bind corrections to the artifact, not the conversation, and replay them before every regeneration so an accepted fix survives being rebuilt. |
| [figure-citation.md](figure-citation.md) | Numbers that cannot rot silently: a generated facts ledger plus inline fact citations on quoted figures, checked by CI on every PR so a stale number fails loudly instead of misleading a reader. |
| [batched-decision-blocks.md](batched-decision-blocks.md) | Front-load ambiguity into one numbered block of questions with recommended picks. Question density correlates with low turn count, not high. |
| [authority-ledger.md](authority-ledger.md) | Who is allowed to say yes, written down: standing grants with scope and expiry, so authority is not a hallway rule. |
| [trap-fixtures.md](trap-fixtures.md) | Plant the exact questions your system once got wrong and grade them deterministically across model tiers; routing-shaped traps discriminate, fact-shaped ones only confirm the kernel. Plus the process drill: stage a deliberate conflict to prove the dormant machinery actually fires. |
| [memory-measurement.md](memory-measurement.md) | Test whether your memory layer actually surfaces: reachability verdicts, a lane probe, use-stamp readout, and a search-miss ledger. Writing is instrumented; retrieval usually is not. |
| [decision-capture.md](decision-capture.md) | Why rulings get written down the same turn they land, not at end of session. |
| [four-founding-docs.md](four-founding-docs.md) | The four files a disciplined repo is born with: rules, build order, parity, decisions. |
| [model-playbook.md](model-playbook.md) | Match the task to the model tier without losing accuracy: boot protocol, guardrails, counter-rules. |
| [multi-agent-hygiene.md](multi-agent-hygiene.md) | Several agents in one repo without trampling: worktrees, disjoint file sets, pre-assigned numbers. |
| [rules-spine.md](rules-spine.md) | The long-form guide to writing a binding CLAUDE.md, the file every other doc defers to. |
| [staging-promotion.md](staging-promotion.md) | The graduated merge lane: agent PRs flow to staging on green, one human switch in front of production. |
| [chorus.md](chorus.md) | Freeze the handful of facts where a miss is dangerous, verbatim at the top of the rules file, held by a unit test. |
| [enforcement-manifest.md](enforcement-manifest.md) | One JSON object per floor rule, bound to its honest enforcement point, with a coverage gate that makes downgrades tamper-evident. |
| [catalog-routing.md](catalog-routing.md) | Three narrow hops, kernel to catalog to file, that keep a large doc corpus reachable without loading it all. |
| [issue-backed-task-bus.md](issue-backed-task-bus.md) | GitHub issues as a lightweight, lockable task queue for multiple agents: labels as state machine, expiring claims, comments as audit trail. |
| [report-catalog-pattern.md](report-catalog-pattern.md) | Safe self-service data access: a catalog of pre-approved parameterized queries behind one endpoint, a hard row cap, and a role-gated escape hatch. |
