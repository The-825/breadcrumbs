---
description: Silently restructure a messy, voice-transcribed, or unstructured task prompt into a clean task spec, then execute the restructured version.
argument-hint: "<messy prompt>"
---

Restructure and execute: **$ARGUMENTS**

If your rules file (CLAUDE.md or equivalent) carries its own prompt-restructure block, that block is canonical: this command implements it, and if the two ever disagree, the rules file wins. The binding blocks in your shared agent preamble apply to everything produced (see `templates/AGENT_PREAMBLE_TEMPLATE.md` in the companion repo, or your repo's installed copy).

## When this fires

Two entry points:

1. **Auto-trigger** (if your rules file enables one): a message that is ALL of
   (a) over ~150 words,
   (b) clearly voice-transcribed or unstructured, AND
   (c) describing a task rather than asking a simple question.
2. **Direct invocation**: `/prompt-master <messy prompt>` restructures the given text regardless of the auto-trigger conditions.

## Suppressors: do NOT auto-trigger when

- The input is code, a paste, or a file reference.
- It is a chat reply or a follow-up clarification.
- It includes "don't optimize" or "as written".

Direct `/prompt-master` invocation overrides the suppressors; the operator asked for the restructure explicitly.

## What to do

1. **Silently restructure** the message into a clean task spec: the actual objective, the concrete deliverables, constraints and scope boundaries stated or implied, the files and systems involved, and any decisions the message already made (do not re-ask those). Strip filler, repetition, and transcription noise. Preserve every operational fact and every ruling verbatim in meaning: restructuring reorganizes, it never drops or reinterprets content.
2. **Execute the restructured version**, not the raw message.
3. **Do not show the restructure unless asked.** No preamble about having restructured. If the operator asks to see it ("show the spec", "what did you restructure that to"), print the clean task spec then.
4. If the restructure surfaces a genuine ambiguity that blocks execution, ask ONE specific question, not a list.
