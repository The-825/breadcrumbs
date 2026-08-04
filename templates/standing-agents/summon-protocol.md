# Summon protocol

> Part of the companion kit for *From Archivist to Architect* (The Architect's Blueprint, Book 1).

An unscoped agent session boots by wandering: it reads whatever looks relevant, spends half its context window before the first useful step, and starts work with no agreed shape for "done", so you can judge neither the answer nor the cost. The summon protocol replaces the wander with a contract: pick the desk, hand it its boot pack, write the task as commander's intent, and require calibrated language in the report. Use it every time you spawn a specialist worker, even for small questions.

The task spec, copy and fill:

```
DESK: <desk id from the registry>        FARE CLASS: routine | priority | emergency

BOOT: perform your boot pack's reads IN ORDER before any task work.
<paste the desk's pack entries here>

GOAL: <what and why, one or two sentences>

CONSTRAINTS: <what must not change. Any write grant stated explicitly,
naming the paths it covers; a write grant lives here in the task spec,
never in the boot pack. No grant stated means read-only.>

DONE-LOOKS-LIKE: <the acceptance shape: a verdict table, a diff, a cited
figure, a list. Concrete enough that both sides know when to stop.>
```

## The flow

1. Resolve the desk from the registry. The entry's scope, posture, and standing constraints ride into the spec. If no desk owns the question, that is a registry gap to note, not a reason to skip the contract.
2. Assemble the boot pack. Honor the modes exactly: full means the whole file, anchor means grep the topic first and read only that section. Honor the trim note when the task does not need a read, and check the pack against the desk's boot budget.
3. Write the spec above and spawn the worker with it.
4. Set the call priority from the fare class: routine runs in the background, priority runs synchronously because the caller is blocked, emergency interrupts and brings your incident playbook along.

## Commander's intent, not a script

GOAL / CONSTRAINTS / DONE-LOOKS-LIKE is deliberate: you state the destination, the boundaries, and the acceptance shape, and leave the route to the specialist. Step-by-step scripts fail twice over: they cost you the planning you meant to delegate, and they bind the worker when the terrain differs from your assumptions. If you find yourself writing step five of a script, either the desk's pack is missing a read or the task wants splitting.

## Calibrated reports

Require estimative language with teeth. Three registers, and the report says which one every claim sits in:

- "verified against <source>": the worker read or ran the thing and cites it.
- "likely (unverified)": inference from the pack; plausible, not checked.
- "cannot determine from this scope": the honest miss, with what would settle it.

A specialist never rounds a guess up to a fact. A report without registers gets sent back; that is the quality half of the contract, and enforcing it is cheaper than re-verifying everything yourself.

## The harbor-pilot variant

For one tricky stretch inside a larger task (one migration, one derivation change, one cutover step), summon the same desk with the same pack but a narrower GOAL, plus an explicit hand-back line: "pilot disembarks when <condition>". The parent session keeps overall command; the pilot takes the wheel only through the strait. Prefer this over handing the specialist the whole voyage when the parent needs to keep context continuity.

## Adoption notes

Start by writing the spec even when you summon nothing: forcing GOAL / CONSTRAINTS / DONE-LOOKS-LIKE onto your own next hour is the fastest way to learn the shape. Then wire it into a slash command that resolves the desk and assembles the pack for you (this kit ships one in [../commands/summon.md](../commands/summon.md)). The contract is the point; the automation just makes it cheap.
