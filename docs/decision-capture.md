# Decision capture: persist a ruling the same turn it lands

> Part of the companion kit for *From Archivist to Architect* (The Architect's Blueprint, Book 1).

The rule: when the operator issues a durable ruling, the session appends it to the decisions ledger in the same turn, before moving on to the work the ruling unblocks. Not at the end of the session, not in a wrap-up pass, not "once the feature is in". The turn the ruling lands is the turn it gets written down.

A durable ruling is any call a future session could plausibly re-open: a product name, a threshold, a policy line, a definition, a scope boundary. The test is durability, not importance. If the same debate could happen again, the answer belongs in the ledger.

## Why the same turn

A ruling that lives only in a session transcript gets re-litigated or silently violated by the next session. A new session starts from the repo, not from earlier transcripts. If the ruling is not in a file the repo carries, the next session either re-opens the question, and may answer it differently, or ships work that quietly contradicts the answer. The contradiction surfaces later, somewhere expensive.

Same turn instead of end of session because sessions do not reliably reach an orderly end. They compact, hit context limits, or get closed mid-task, and anything waiting for a wrap-up step is gone. Capture on the event survives all of those exits. Capture on a schedule survives none of them.

## The two stores

Two files carry settled knowledge, and they carry different kinds.

**The decisions ledger** holds operator rulings: durable product and process calls, written in prose, append-only, numbered. A superseded entry stays in place with a "Superseded by" line, so the history of the call stays visible. Template: [DECISIONS_TEMPLATE.md](../templates/DECISIONS_TEMPLATE.md).

**The conclusions store** holds verified facts: things a session proved that a future session should recall instead of re-deriving. Each entry is one JSON line keyed to the file or domain it concerns, with a date, the fact, and an evidence pointer. Template: [CONCLUSIONS_TEMPLATE.md](../templates/CONCLUSIONS_TEMPLATE.md). Starter file: [conclusions.jsonl](../templates/conclusions.jsonl), three example lines that label themselves for deletion.

The routing test: rulings are decided, conclusions are discovered. "The report is titled Revenue Overview, everywhere it appears" is a ruling; it went one way because the operator said so. "The revenue rollup counts orders on the paid date, not the created date" is a conclusion; it is true whether or not anyone decided anything. When one turn produces both, because the operator ruled on a question a session surfaced, write both entries: the ruling in the ledger, the fact it settles in the store, each citing the other in its source or evidence line.

## How recall works

Capture is half the loop. The other half is the read-back, and the read-back is the half that pays.

At session start, grep the conclusions store for the paths the session is about to touch:

```
grep '"path": "src/sync/' CONCLUSIONS.jsonl
grep '"path": "domain"' CONCLUSIONS.jsonl
```

What comes back is what earlier sessions proved about the code in front of you. A few seconds of grep replaces the re-derivation, or worse, the confident wrong answer.

A recall command can automate the lookup: take a path, return the matching store lines plus recent history for that file in one shot. The command skills that ship in this repo include one. If your agent harness supports session-start hooks, wire the grep in there, so matched lines land in context at boot instead of depending on a manual step each session.

The decisions ledger needs less machinery. It stays small enough to read whole, and the rules file should tell every session to read it at start.

## The scaled-down starter

If two stores is more machinery than the project needs, start with one markdown file and the habit. A single DECISIONS.md, a dated entry appended the turn each ruling lands, a read of the file at session start. That alone stops most re-litigation.

Add the jsonl store when path-keyed facts start to accumulate. The tell is entries that are really "things we proved about src/sync" rather than rulings; that is the split point. The store format is three required fields per line, so the migration is copy and paste.

## What this is not

Neither store holds in-flight state. The active branch, half-done edits, and next steps belong in the living handoff file, refreshed on an explicit trigger: [SESSION_STATE_TEMPLATE.md](../templates/SESSION_STATE_TEMPLATE.md). The three files divide cleanly: the ledger holds what was decided, the store holds what was learned, the state file holds what is in flight right now. The rules file (CLAUDE.md or equivalent) points at all three, so every session starts from the same map.
