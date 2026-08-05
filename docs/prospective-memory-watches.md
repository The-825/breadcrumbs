# Prospective memory: acting when a condition becomes true, not on a date

> Distinct from the deferral pattern in `floating-memory.md` (a fixed-due-date item on
> a minimum-equipment list). This is for the other half of "remember to do this later":
> not later on the calendar, but later when something specific becomes true.

## The problem

Scheduled triggers (cron, a send-later reminder) cover "do this at a known future
time." They don't cover "do this once some condition I can't put a date on becomes
true": once a dependency ships, once a flag flips, once a metric crosses a threshold,
once a file stops existing. The naive fix is a human remembering to check periodically,
which is exactly the kind of remembering agent memory work is supposed to remove.

## The pattern

A watch is a row, not a reminder: a checkable condition, an intention, and an owner,
evaluated on a cheap recurring pass instead of held in anyone's head.

- **The condition is checkable, not vague.** A query predicate against a live store, a
  capability probe, a file-existence check, something a script can evaluate in
  isolation without judgment calls. "Watch for the API to stabilize" isn't a watch;
  "watch for `GET /v2/status` to return 200" is.
- **Cheap evaluation, expensive action.** The recurring pass that checks conditions
  should cost almost nothing, a handful of fast checks, so it can run often. Only a
  condition that trips spawns real work: a fresh agent session gets the intention and
  the context that triggered it.
- **The intention is written when the watch is set, not when it fires.** Write down
  what should happen and why at the moment you realize you'll need to act later, while
  the reasoning is fresh. The watch firing months later hands a session a complete
  intention, not a bare fact that needs re-deriving.
- **An owner, always.** Same discipline as any deferred obligation: a watch with no
  owner is a watch nobody answers for when it fires.

## When to use it

Worth it for anything you'd otherwise handle by periodically remembering to check:
"has this shipped yet," "did that flag graduate," "is this workaround still needed."
If the trigger condition is actually just a date, use a scheduled trigger instead;
watches are for conditions a calendar can't express.

## What it isn't

Not a general-purpose event system and not a substitute for real alerting on
production incidents. A watch is for low-urgency, high-forgettability conditions where
the cost of missing the moment is a delayed follow-up, not an outage. Anything
time-critical belongs in your actual monitoring stack, not a memory pattern.
