# Standing-desk lifecycle

> Part of the companion kit for *From Archivist to Architect* (The Architect's Blueprint, Book 1).

Two failure modes bracket a fleet. Keep every specialist warm and you pay standing cost for desks nobody calls; summon cold every time and a high-traffic desk pays full boot price per call, several times a day. This page is the dial between them: when to stand a desk, how to stand it, how to keep it honest, and how to retire it without losing what it knew. Use it the first time one desk starts taking several calls a day.

Stand-a-desk checklist, copy and run:

```
[ ] Traffic test passed: several calls a day to this one desk, or a live
    cycle where per-call re-boot costs more than one warm session
[ ] Dedicated session created, named for the desk ("Desk: Ops")
[ ] Booted from the pack IN ORDER (modes honored), then the conclusions
    ledger swept for the desk's paths
[ ] Announced on the task bus: one open task naming desk id + session id,
    closed on stand-down (the discoverable record other sessions find)
[ ] Wake wiring chosen: poll the bus on wake, accept pokes from other
    sessions, or a scheduled wake, whichever your tooling supports
[ ] Delta cursor recorded: the commit SHA the boot reflects
```

## The decision rule

Summon by default. A desk is a durable definition (registry entry, boot pack, accumulated conclusions), so a fresh worker with the pack IS the specialist: zero standing cost, nothing to babysit. Stand a desk only when call frequency justifies it: several calls a day to one desk, or a live cycle (a launch week, an incident arc) where re-booting the pack per call costs more than keeping one session warm. Traffic earns standing; importance alone does not.

If you are unsure whether traffic justifies standing, it does not. The summon path is always correct, just sometimes slower; a stood desk that was not earned is pure carrying cost.

## Serving calls

A standing desk serves exactly the summon contract: commander's intent in, calibrated registers out, read-only unless the calling spec grants writes. Standing changes the economics, never the contract. On each wake, delta-verify before answering: fetch the default branch, diff from the recorded cursor SHA over the desk's paths, re-read only what changed, record the new SHA. That keeps a warm desk current for the price of a log read instead of a re-boot.

Fare classes still apply at a warm desk: routine calls queue and batch, a priority call jumps the queue because someone is blocked, and an emergency preempts whatever the desk is doing. If emergency calls become common, the problem is upstream of the desk, not in it.

## Keeping a desk honest

Warm sessions drift. On a fixed cadence (monthly works), review the desk against its registry entry: is it answering only inside its scope, are its pack reads still the right diet (files move, docs split), do its standing constraints still match reality? Fix the registry and the pack, not the session; the files are the desk. And treat the session as disposable: on container loss or compaction damage, re-stand from the checklist. Nothing in the session is load-bearing; if losing the session would lose knowledge, that knowledge belonged in the conclusions ledger.

## Retiring a desk

When traffic drops, stand down: close the announce task, flip the registry status back to summonable (or to retired if the domain itself is done), and note the date. Retired entries stay in the roster; the history of which desks existed and why is cheap to keep and expensive to reconstruct. Never delete the boot pack with the desk; the pack is how the area gets re-learned later.

## Closeout transition checklist

When the surface hosting your standing sessions changes or goes away (a tool migration, a platform sunset), the desks need their own wiring on the new surface:

- [ ] Stand the highest-traffic desks first; everything else reverts to summon-on-demand until traffic re-earns standing.
- [ ] Re-home every scheduled check-in that pointed at a dead session to the new session or a calendar.
- [ ] Update each announce task with the new session id, so discovery keeps working.

A desk you can retire and re-stand from files in ten minutes is the proof the substrate works.
