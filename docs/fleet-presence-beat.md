# Fleet presence: a beat, not a board

> Companion to `floating-memory.md`: that essay covers what a shared memory holds and
> how it decays. This one covers a narrower question inside it: how do you know, right
> now, who on the fleet is actually working, on what?

## The problem

You want to know what every active agent session is doing without opening each one.
The obvious answer is a status board: a page or table where each session writes what
it's working on. It looks fine in a demo and rots within hours in production, because
nothing forces an update. A session that crashes, gets clear'd, or just moves on to a
different task leaves its last self-reported line standing, confidently wrong, for as
long as nobody happens to check.

## The pattern

Replace self-reported status with presence upserted at fixed moments, then cross-check
it against independently observed activity.

- **Upsert, don't append, at four fixed moments.** A session writes one row to a
  presence table on boot, on claiming a task, on switching focus, and on completion.
  Each write overwrites the same row for that session identity; there's no history to
  go stale, only a current state that's either fresh or provably old.
- **A timestamp is the only trust signal.** A presence row older than some threshold
  (tuned to your task grain, an hour is reasonable for interactive agent work) is
  treated as stale automatically. No session has to remember to say "I'm done" for the
  system to stop trusting it.
- **Cross-check against ground truth.** Presence claims are one input. A coordinator
  loop also reads git activity, open PRs, and claims on the task bus (see
  `issue-backed-task-bus.md`), and reconciles: does this session's presence match what
  it's actually touching? A stale presence row next to fresh commits is a bug in the
  presence write, not a stale session, and the reconciliation catches the difference
  either way.
- **Poke once, then let the reaper handle it.** A stale claim gets one scheduled
  nudge asking the claimant to confirm or release. No nudge loop, no escalation
  ladder. If nothing answers, the task bus's own expiry (see the task-bus doc) takes
  it from there.

## When to use it

Worth building once you have enough concurrent sessions that "what's everyone doing"
stops being answerable by scrolling a chat log, roughly three or more running at once.
Below that, asking is cheaper than building a presence table.

## What it isn't

Not a replacement for the task bus or the decisions ledger. Presence answers "who is
active and on what, right now." It says nothing about what got decided or what's still
owed; those live in the ledger and the obligation tracker respectively. A presence
table with no cross-check against real activity degrades back into the same
self-reported board this pattern exists to avoid, so the reconciliation step is not
optional.
