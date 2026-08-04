# Model Playbook

> Part of the companion kit for *From Archivist to Architect* (The Architect's Blueprint, Book 1).

Treating every model tier as interchangeable fails in both directions. Cheap models silently apply prototype discipline to production repos (guessed figures, skipped verification, confident paraphrases that drop the one nuance that mattered), while strong models burn budget re-deriving lookups the repo already answers in a file. This playbook is the fix: a boot protocol every session follows, a pre-flight guardrails table, counter-rules per tier, and an operator cheat sheet for matching the task to the model. It is vendor-neutral on purpose; lineups change faster than the pattern does, so it speaks in tiers (strongest, middle, cheapest) and you map your provider's current models onto them.

## The core idea

Model tiers trade inference depth for cost. A strongest-tier session can infer its way to the right file, the right caveat, the right query. A cheaper session gets to the same accuracy at a fraction of the cost by substituting deterministic routing for open-ended inference: index files, data dictionaries, and settled-conclusions ledgers that the repo maintains so the model does not have to rediscover them. The playbook only works if those routing docs exist. If your repo has no index or dictionary yet, that is the prerequisite, not this doc.

## The boot protocol (index-first routing)

Every session, any tier, in order:

1. Never re-read what is already in context. The rules file auto-attaches in most agent setups; re-reading it pays hundreds of lines for zero new information.
2. Resuming mid-stream? Read the session-state handoff file first, before anything else.
3. Task wider than a lookup? Read the one-page system mental-model doc once. Skip it entirely for pure lookups.
4. Route every "where is X" and "what computes Y" question through the repo's machine-first index file (the where-is map, route map, thresholds with file and line, invariants, doc router). One index read replaces a whole exploratory grep arc.
5. Then open only the narrow cited source: grep to locate, read a line range. Reference docs are grep targets, never end-to-end reads.
6. Use the repo's packaged skills and commands instead of hand-rolling the workflows they already encode.
7. Distrust any dated snapshot for current numbers. Verify a live value against its canonical source once, then trust it for the rest of the session.

## Pre-flight accuracy guardrails

These are the error modes that cost real rework, each reduced to a one-line rule. Cheaper tiers hit them more often, so the table is mandatory pre-flight reading for those sessions and cheap insurance for the rest.

| Error mode | Rule | Where the answer lives |
| ---------- | ---- | ---------------------- |
| Hand-rolled aggregation diverges from the official number | Reported figures come from the canonical endpoint, never a fresh query off the raw tables | The route logic and the views it reads |
| "This field is sparse" when blank means No | Blank is not missing; check field semantics before calling anything a gap | The data dictionary |
| Signup counted as activation | A form submission is intent, not behavior; reconcile through the behavioral verifier | The reconciliation query the repo already ships |
| Status filter drops null-status rows | Use the canonical active filter verbatim; never compare against a literal that null rows fail | The rules file |
| Platform quirks burn an hour each | Region-scoped metadata queries, permission-split access paths, and their kin are documented once | The index's gotchas section |
| Git flow improvisation | Push, never merge by hand; feature-slug branches only | The rules file |

Maintain the table the same way you maintain any doc: when a new error mode costs a session real time, it gets a row here and an entry in the index's gotchas, in the same PR as the fix.

## Strong and cheap models fail differently

This is the transferable insight. The counter-rules differ per tier because the failure modes do.

**Strongest tier** fails by excess. It reads broadly "to be safe," re-verifies what the index already pins, narrates its plan between tool calls, and lets scope creep in on long arcs. Counter-rules: grep-first narrow reads, one agent per research question, verify once then trust, no prefaces before tool calls, a pre-push check that the diff matches the stated scope, and plan mode reserved for genuinely multi-file work.

**Middle tier** (the daily driver) fails by plausible guessing, not over-exploration. Counter-rules: never assert a figure without naming its source; quote domain semantics verbatim from the dictionary instead of paraphrasing, because a confident paraphrase that drops one nuance is this tier's costliest failure; treat the guardrails table as a mandatory pre-flight; after two failed lookups, stop and ask for a pointer instead of synthesizing one; verify against the live source before every write.

**Cheapest tier** is for status pulls, single-file lookups, log reads, yes-or-no checks, and CI watching. Never schema changes, migrations, multi-file refactors, or anything touching domain-data semantics. Its tripwire is structural: the moment it finds itself editing a second file, that is the signal the task was mis-tiered, and it should stop and say so rather than push on.

## Match the task to the tier

| Task shape | Examples | Tier |
| ---------- | -------- | ---- |
| Lookup | status pull, single-file read, log tail, yes-or-no check | Cheapest |
| Ship | a scoped feature or fix with a known target file and a pattern to mirror | Middle |
| Complex | multi-file refactors, schema and migration work, debugging with an unknown cause, anything touching data semantics | Strongest |

Start cheaper and escalate on a wall; that is almost always the right default. The exception is work you already know is complex-shaped, where starting cheap just prepays the escalation.

## The escalation valve

A cheaper session must be allowed, and expected, to hand up. The trigger is concrete: if a debugging arc is still guessing after about thirty minutes on a fix that looked five-minute-shaped, the session recommends restarting the turn on the stronger tier. That costs one restart. Letting the cheap session keep digging costs more dead-end turns plus the cleanup. Before any mid-arc model switch, refresh the session-state handoff file first, so the next model boots from written state instead of a lossy summary.

## Operator cheat sheet

The habits on the human side of the session, roughly in order of money saved:

- Batch related asks into one message. Every separate turn re-attaches the rules file.
- Reference by path and line ("the watermark logic in sync.py around line 90"), not "that file we talked about."
- Front-load any operational fact that changes the data model ("that vendor was suspended in March"). It exists nowhere else, and the model cannot infer it.
- When correcting a number, name the canonical source in the same breath, so the correction sticks as a rule rather than a one-off.
- Shape the prompt to the tier. Middle tier: give the target file, the pattern to mirror, and the acceptance criterion up front; explicit beats inferable. Strongest tier: give the goal, the constraints, and what is out of scope, then let it plan.
- Mark resolved topics ("done with the sync issue") so stale context can be dropped from consideration.

Ownership note: this playbook is a living doc on the same continuity sweep as the rest of your operating docs. When the model lineup changes or a new recurring error mode shows up, update the tier mapping and the guardrails table in the same pass. A playbook that lags the lineup by six months is just another stale doc teaching sessions to ignore it.
