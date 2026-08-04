# The unattended agent contract

An agent you watch is a different animal from an agent that fires at 6am on a cron while you sleep. When you are in the loop, your judgment is the backstop: you see the wrong file get touched and you stop it. Unattended, there is no backstop. Whatever the prompt permits, the agent eventually does, on a morning when the input it expected is missing and it improvises.

The failure is rarely dramatic. It is a scheduled sweep that was supposed to update three files, hit an unreachable source, decided the right fix was broader, and quietly rewrote a fourth. Nobody notices for a week because the job went green.

Every scheduled, no-human-in-the-loop agent gets the same five controls. This is the contract.

## 1. A mode switch

Three modes, named in the prompt, selectable per run:

- **`smoke`.** Prove the agent can reach its inputs. Read the sources, write nothing, print one agreed sentinel string, stop. This is what you run after changing the prompt or rotating a credential, and what a fresh install runs first.
- **`dry_run`.** Do the full analysis and report exactly what it WOULD write, without writing. This is the mode you read when you want to trust the thing again.
- **`full`.** Do the work for real.

The point of `smoke` is that "can it authenticate and see its inputs" and "is its judgment any good" are separate questions, and the first one should be answerable in seconds without risking a write. Most of the mornings an unattended agent breaks, it breaks on the first question.

## 2. A named, bounded write surface, enforced outside the prompt

The prompt states the write surface as a closed list: "these three files are your entire write surface; anything else is out of bounds." Then a post-run guard checks the actual diff against that list and fails the job on any out-of-scope change.

Both halves are required, and the second is the one that matters. A prompt-only bound is a request. An agent under pressure from a weird input will honor the spirit of the task over the letter of a scope line, because that usually reads as the helpful thing to do. The guard is what makes the bound real: it does not care what the agent believed it was doing.

## 3. A bounded read set

Say where reading starts and stops: begin from the generated-facts file and the index, do not walk the tree. An unattended agent with an unbounded read set has an unbounded token bill and an unbounded set of things it might decide are relevant. Bounding the read set is how the 6am run costs the same on a busy week as a quiet one.

## 4. Degrade, do not hard-fail

One unreachable source is a one-line note in the report, not a crash and not an abandoned run. A sweep over six sources that dies on the second one has done nothing useful and has told you almost nothing.

The inverse failure matters just as much: an agent that hits a missing input and *substitutes* something plausible. The contract is explicit that a gap gets reported as a gap. Never fabricate a zero for something you could not measure; say the measurement was not available and name why.

## 5. A triage-only posture

Anything outside the write surface gets FILED, never fixed. The agent opens an issue, appends a ledger row, or adds a line to a report, and moves on. This is what keeps an unattended run from turning into an unattended refactor, and it is also what makes the output reviewable: a human reads a short list of filed items instead of auditing a wide diff.

Close the prompt with the reporting rule: **silent, or one line, when clean.** An unattended agent that reports at length on a normal day trains you to skip its output, and then the one abnormal day scrolls past unread.

## The prompt template

`../templates/standing-agents/routine-prompt.template.md` is this contract as a fill-in-the-blanks prompt file. Copy it per scheduled agent, fill the five slots, wire the post-run guard.

## An instance of this contract

[doc-sync-agent.md](doc-sync-agent.md) is one worked example: a scheduled agent with a two-file scope, a hard contract that forbids inventing records, a PR-not-push least-privilege posture, and a sentinel string (`DOC_SYNC_NO_CHANGES`) for the clean case. Read it as this contract applied to one job, and generalize from it rather than copying it for a different job.

## Adoption notes

Adopt the modes first, even if you adopt nothing else. `smoke` and `dry_run` cost an afternoon to add and immediately change how you feel about the 6am run, because you stop guessing whether it still works and start checking.

The post-run guard is the piece teams skip, and it is the piece that converts the write surface from a hope into a property of the system. If you only have budget for one enforcement mechanism in your scheduled jobs, make it that one.

An agent you cannot watch needs a contract you can enforce. Write the bound, then make something other than the agent check it.
