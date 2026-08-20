# Fleet presence: a beat, not a board

> Companion to `floating-memory.md`: that essay covers what a shared memory holds and
> how it decays. This one covers a narrower question inside it: how do you know, right
> now, who on the fleet is actually working, on what?
> **Pattern only: no presence service ships in this kit.**

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

## The TCAS layer: pairwise deconfliction, no tower in the loop

Presence tells you WHO is flying. The next failure it does not cover by itself: two
live sessions editing the SAME FILE at the same moment, each about to hand the other
a merge conflict. Routing that through the coordinator loop is too slow, since the
coordinator runs on a cadence and the collision is happening now. Aviation solved
this exact topology decades ago: the tower manages the airspace, but imminent
collisions are resolved peer to peer by the aircraft themselves (TCAS), because the
two parties closest to the conflict have the freshest data and the shortest loop.
The same split works for agent fleets:

- **Positions ride the beat.** Each presence upsert includes the files the session
  is currently touching, self-reported at the same fixed moments as the beat itself.
  No extra write path, no extra thing to forget.
- **Bridge positions to where edits happen.** The moment of collision is an edit,
  and edit-time hooks often cannot query the presence store directly. Have the
  coordinator (or any store-connected pass) dump live positions to a small local
  file the hook CAN read: one row per file and session, with the branch and the
  beat's age. An absent or aging dump degrades to no warning, never to an error.
- **The editing session resolves it, directly.** On a live-position hit, the
  session about to edit sends ONE message to the other session (a one-shot
  scheduled message bound to its session id works where no direct channel exists):
  I am editing this file on this branch; you reported it in your last beat;
  whoever is deeper keeps the file, the other scopes away or waits for the merge.
- **One poke per pair and file, then escalate.** A repeat overlap goes to the
  coordinator's digest, never to a second poke. This is the anti-spam rule that
  keeps peer-to-peer resolution from becoming peer-to-peer noise.
- **Quiet sky costs nothing.** Positions ride beats and beats ride events, so when
  nothing is flying there are no writes, no pokes, and an aging positions file the
  hook ignores. Nothing about this layer polls.

The tower keeps its jobs: orphans, stale claims, digests, dead-claim release.
Pairwise conflict just stops waiting for it. Staleness discipline carries over
unchanged from the beat: a position older than the trust threshold is a trail, not
a live aircraft, and a warning against a folded or dead session is silently
dropped rather than poked.

## When to use it

Worth building once you have enough concurrent sessions that "what's everyone doing"
stops being answerable by scrolling a chat log, roughly three or more running at once.
Below that, asking is cheaper than building a presence table. The TCAS layer earns
its keep one step later: once concurrent sessions start colliding on the same files
often enough that merge conflicts are a recurring tax rather than a rare accident.

## What it isn't

Not a replacement for the task bus or the decisions ledger. Presence answers "who is
active and on what, right now." It says nothing about what got decided or what's still
owed; those live in the ledger and the obligation tracker respectively. A presence
table with no cross-check against real activity degrades back into the same
self-reported board this pattern exists to avoid, so the reconciliation step is not
optional.
