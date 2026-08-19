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

## Two things a first version gets wrong

Both of these were found by running the pattern, not by thinking about it, and both are
cheap to build in from the start and annoying to retrofit.

### Overwriting state destroys the only question worth asking

The obvious schema puts the watch's current state on the watch row: last checked, last
result, fired at. Every re-check overwrites the previous one.

That schema cannot answer "has this watch ever been worth interrupting someone for."
After a month you have a table of watches, no idea which ones earned their keep, and no
basis for retiring the noisy ones except a feeling.

Make evaluations and outcomes append-only rows instead. Every check writes a row. Every
delivered raise writes a row. Every human response to a raise, acted on it, dismissed it,
it was wrong, writes a row that points at the specific raise it judges. The watch row keeps
only what it needs to schedule the next check.

Now retirement is a query rather than an argument. A watch that has raised eleven times and
been dismissed eleven times is not a watch, it is a habit, and you can see it.

One schema detail that matters more than it looks: **make the stored result three-valued.**
True, false, and could-not-check. A two-state field forces a failed evaluation to be
recorded as false, and a system that cannot distinguish "checked and it was false" from
"the check itself did not run" will eventually act with total confidence on a check that
never happened.

### A tripped condition is not automatically a current fact

A watch condition goes true. The raise gets queued. Something delays delivery: the session
that would act was busy, the queue backed up, the person was asleep. The raise arrives
later carrying a fact that was true when it was measured and may not be now.

The failure is quiet and it costs trust in the whole notification layer the first time
someone catches it, because a system that tells you a stale thing as though it were current
has to be re-checked by hand from then on, which is the entire cost the watch was supposed
to remove.

**Gate delivery on the freshness of the evidence, not on the fact that the condition
tripped.** If the reading is older than the watch's own check cadence, do not deliver.
Re-evaluate silently and raise on the next pass with a fresh reading. A watch that checks
hourly should never deliver a raise built on a reading from yesterday.

This is worth stating as a hard rule rather than a nice-to-have, because the failure mode
is not a missed raise, it is a confidently wrong one.

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
