# The decision-capture nudge hook

> Part of the companion kit for *From Archivist to Architect* (The Architect's Blueprint, Book 1).

The decision-capture rule ([docs/decision-capture.md](../../docs/decision-capture.md)) says a ruling gets written to the ledger the same turn it lands. The rule fails in one predictable way: the session is mid-task, the operator drops a ruling in passing, and the session keeps working. Nothing malfunctioned; the capture step just never fired. This hook makes that failure louder. When a submitted prompt contains ruling-shaped language, a reminder to capture lands in the session context alongside the ruling itself.

## What it is, mechanically

Claude Code hooks are shell commands the harness runs at fixed lifecycle events, configured in `.claude/settings.json` under a `hooks` key. This one registers on the **UserPromptSubmit** event: every time the user submits a prompt, the harness runs the command and passes a JSON payload on stdin that includes the prompt text. For this event, whatever the command prints to stdout on a zero exit is added to the turn's context, so the model processes the prompt with the hook's output in view.

[capture_nudge.py](capture_nudge.py) reads the payload, runs a fixed list of regular expressions over the prompt ("ruling", "standing rule", "from now on", "going forward", clause-initial "always/never do X", and so on), and prints a one-line reminder on a match. On no match it prints nothing and the turn proceeds without a trace.

## Setup

Copy the script into your repo (conventionally `.claude/hooks/`), then register it:

```json
{
  "hooks": {
    "UserPromptSubmit": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "python3 \"$CLAUDE_PROJECT_DIR/.claude/hooks/capture_nudge.py\" 2>/dev/null || true"
          }
        ]
      }
    ]
  }
}
```

Edit the `NUDGE` string in the script to name your repo's actual ledger files, and extend `PATTERNS` with the phrasings your operator actually uses.

The `2>/dev/null || true` wrapper is deliberate, on top of the script's own always-exit-0 design. On UserPromptSubmit, a hook that exits nonzero can surface errors into the session or, at exit code 2, block the prompt entirely. A reminder is never worth blocking a prompt, so the hook fails open twice: once in the script, once in the registration.

## Limits, stated plainly

- **It matches text; it does not understand anything.** The regex list is lexical. A ruling phrased without any marker ("make the header blue on every page") passes silently, and a pasted document that happens to contain "from now on" fires the reminder. Keep the patterns conservative: a missed nudge costs nothing new, while a noisy one trains everyone to ignore it.
- **It reminds; it cannot capture.** A hook is a subprocess, not a participant. It cannot write the ledger entry, verify one was written, or make the session comply. The injected line raises the odds the capture step runs this turn; the rule in the rules file is still what binds.
- **It sees one prompt, not the conversation.** The payload carries the submitted prompt. A ruling established across several turns, or one that arrives inside tool output rather than a user prompt, is invisible to it.
- **It runs on every prompt, so it must stay cheap.** Stdlib only, no file or network I/O, well under 100ms. Anything slower taxes every turn of every session to catch an occasional event.

Treat the hook as a seatbelt reminder chime, not the seatbelt: cheap, occasionally annoying, and it exists because the step it points at is easy to skip exactly when it matters.
