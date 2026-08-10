# Agent session efficiency

One debugging session cost about twice what it should have, and the overage traced almost entirely to recoverable patterns: whole-file reads when 30 lines answered the question, command output echoed back at the operator, long recaps after every step, CI polled seconds after a push. Every turn in an agent session pays for the rules file, the file reads, the tool output, and the response prose. A short set of standing habits caps that budget. Paste the block below into your own agent rules file.

## Agent-side rules

```markdown
## Session efficiency

1. Grep to locate, then read narrow line ranges. Never read a whole file
   when 30 lines answer the question.
2. Never re-read a file in the same session. The harness tracks file
   state; a second read pays tokens for no new information.
3. Cap tool output. Pipe diagnostics through `| head -30`, pass `--limit`
   flags on logs, use value-only output formats for one-shot queries.
   Pulling 30 lines when 5 diagnose the problem is waste.
4. Do not echo command output back at the operator. They just pasted it.
   Acknowledge the finding and move on.
5. End-of-turn summary: two sentences or less. What changed, what is
   next. No bulleted recap of the plan after each step.
6. Corrections: one sentence. "That was wrong, the real answer is X."
7. Prose over headers for short answers. A two-sentence answer does not
   need a Summary heading and bullets.
8. One research agent per question. Parallel agents on overlapping
   queries duplicate work and tokens.
9. No "let me check X" preface before a tool call. Run the tool.
10. Answer-first applies to the FIRST sentence, not only a closing line.
    A reply that opens with the wrong call and corrects itself later will
    be misread by anyone skimming the top, even when the ending is right.
    (Observed in a planted-trap probe: a worker opened "Yes, flag it" and
    closed correctly with the opposite answer.)
```

## Operator-side counterpart

The human on the other side of the session controls half the budget. Worth documenting next to the agent rules:

```markdown
## Operator habits

1. Truncate pasted output. Pipe through `| tail -30` or `| grep -i error`
   when the full dump is not needed.
2. Batch related questions into one message. Each extra turn re-attaches
   the rules file.
3. Reference by path:line ("sync.py:1190") instead of asking the agent
   to go find it.
4. Mark resolved topics ("done with the auth issue") so that context can
   be dropped from active consideration.
```

## Adoption notes

Put both lists in the same file the agent reads at session start, so the rules survive between sessions instead of being restated each time. The payoff is not one big saving. It is a few percent shaved off every single turn, forever.
