---
description: Summon a domain-specialist worker - resolve the desk from the registry, assemble its boot pack, and spawn the agent with commander's-intent framing (GOAL / CONSTRAINTS / DONE-LOOKS-LIKE).
argument-hint: "<desk id or name from your registry>"
allowed-tools: Read, Grep, Bash, Agent
---

Summon the specialist desk for **$ARGUMENTS** per the summon protocol.

Fill these before first use: `<registry-file>` (your specialist roster, e.g. `agents/registry.json`), `<boot-packs-file>` (your per-desk read playlists, e.g. `agents/boot-packs.yaml`). Both start from the templates in `templates/standing-agents/`.

## Step 1: resolve the desk

Match `$ARGUMENTS` against the roster in `<registry-file>` by id or name. If nothing resolves, print the roster (id, name, scope areas) and stop. Read the resolved entry fully: its scope, posture, fare classes, and standing constraints ride into the task spec.

## Step 2: assemble the boot pack

Read the desk's pack from `<boot-packs-file>`. Honor the modes exactly: `mode: full` means the worker reads the whole file; `mode: anchor` means grep the topic in play first, then read ONLY that section (each anchor entry carries the file's full-size estimate precisely so nobody "just reads it"). Honor any trim note. If the pack's estimated total exceeds the registry's boot budget for this desk, trim before spawning; never hand over an over-budget pack.

## Step 3: spawn with commander's intent

Spawn an Agent-tool worker whose prompt contains, in order: (1) the pack's reads, to be performed IN ORDER before any task work; (2) the desk's standing constraints; (3) the task spec in three fields:

- **GOAL**: what and why, one or two sentences.
- **CONSTRAINTS**: what must not change. Any write grant stated explicitly, naming the paths it covers; a pack never grants writes, only this spec does. No grant stated means read-only.
- **DONE-LOOKS-LIKE**: the acceptance shape (a verdict table, a diff, a cited figure, a list).

Require calibrated estimative language in the report: "verified against <source>" vs "likely (unverified)" vs "cannot determine from this scope"; a specialist never rounds a guess up to a fact. For one tricky stretch inside a larger task, use the harbor-pilot variant: same pack, narrower GOAL, plus an explicit hand-back line ("pilot disembarks when <condition>").

## Step 4: fare class sets the call priority

From the registry entry's fare classes: `routine` runs in the background; `priority` runs synchronously (the caller is blocked); `emergency` uses interrupt semantics with your incident playbook riding along.

End with one line: desk summoned, pack size (est tokens), fare class, and the GOAL line.
