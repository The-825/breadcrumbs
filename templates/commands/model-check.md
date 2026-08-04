---
description: Classify a task description by shape (LOOKUP / SHIP / COMPLEX) and recommend a model tier from the table below. A check, not an executor.
argument-hint: "<task description>"
allowed-tools: Read
---

Classify **$ARGUMENTS** by task shape and print the model recommendation. Do NOT run the task itself; this command is a check, not an executor.

## Step 1: Classify the shape

Judge the task description against these shapes, in order:

- **LOOKUP**: a question answered by locating and reading something. No edits. Signals: "what / where / which / how many", a single file or fact, no deliverable beyond the answer.
- **SHIP**: a bounded, well-specified change with a known recipe. Signals: "add a route like the existing ones", "fix <named bug> (cause known)", "write <doc> from <template>", one or two files, acceptance criteria clear from the ask.
- **COMPLEX**: the approach itself is undecided. Signals: multi-file design work, debugging with an unknown cause, cross-cutting refactors, anything touching data migrations or auth, "figure out why".
- **TRIVIAL / continuation**: a short reply ("yes", "go", a follow-up clarification). Print one line: "task shape unclear or trivial, no advisory; whatever model is running is fine." Do NOT fabricate an advisory.

## Step 2: Recommend a tier

Print the shape, the recommended tier from this table, and one sentence of reasoning.

| Shape | Tier | Your model (edit this column) |
|---|---|---|
| LOOKUP | fast, cheap tier | `<fast-model>` |
| SHIP | daily-driver tier | `<default-model>` |
| COMPLEX | deepest tier you pay for | `<deep-model>` |

Example ladder, for calibration only: one production setup ran Haiku for lookups, Sonnet for shipping, and Opus for complex work. Treat that as the shape of a ladder, not a prescription; model lineups and prices change, so fill the column from your provider's current offerings. (The named ladder stands by design: decisions ledger entry D-5 sanctions model names inside labeled, calibration-only examples like this table; the no-model-identifiers rule governs committed artifacts.)

## Step 3: Cite the counter-rule

When a strong advisory fires, also cite the standing counter-rule for the tier, so the operator sees the reasoning and not just the label. Generic versions worth adapting into your rules file:

- Deep tier: prone to over-exploring a simple ask; scope it tightly.
- Mid tier: prone to plausible guessing; require it to verify against the code or data before asserting.
- Fast tier: lookups and single-file mechanical edits only; never multi-file changes.

## Caveats

- Classification is heuristic (shape signals plus length). It is not a substitute for judgment on ambiguous asks; when genuinely torn between two shapes, say so and recommend the higher tier.
- Silence is a valid answer. Continuation replies and clearly-SHIP tasks the default model handles fine need no advisory.
- The system this was extracted from also ran an automatic version of this check as a prompt-submit hook backed by a small classifier script. This file is the on-demand version and has no script dependency; if you want the automatic version, wire the same table and shapes into a hook of your own.
