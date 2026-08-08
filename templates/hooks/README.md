# Hooks

A rule that lives only in the rules file holds only while the model remembers it, and memory is the first thing context pressure takes. Hooks are the harness-side floor under those rules: small shell scripts the harness runs at fixed lifecycle events (turn end, session start, before compaction), so the check fires whether or not the model remembered, on the hundredth turn as reliably as on the first. Copy this directory the day one of your rules starts with "always" or "at the end of every turn" and compliance depends on the model remembering to comply.

| File | What it covers |
|---|---|
| [stop-hook-batch-cadence.sh](stop-hook-batch-cadence.sh) | Turn-end git check that stays silent inside a batch-push window and warns only on stale or unsafe work |
| [batch-cadence.md](batch-cadence.md) | The pattern behind it: two good rules that fight, the window rule, the unconditional safety checks, and the durability trick that survives launcher re-provisioning |
| [pre-compact-save.sh](pre-compact-save.sh) | PreCompact hook that copies the full transcript to a local save directory before compaction can lose detail |
| [post-compact-pointer.sh](post-compact-pointer.sh) | SessionStart companion (matcher "compact") that tells the post-compaction session where the save landed |
| [model-routing-prompt-hook.sh](model-routing-prompt-hook.sh) | UserPromptSubmit hook that classifies the prompt's task shape and injects a one-line model-tier hint; continuation replies stay silent |
| [task_shape.py](task_shape.py) | The classifier behind it (LOOKUP / SHIP / COMPLEX, mirroring the model-check table); fail-open, at most one line of output |
| [outbound-pii-screen.sh](outbound-pii-screen.sh) | PreToolUse gate on non-git outbound tool calls (email, cloud-drive, publish); screens the payload with the shared PII detector before it leaves the building |
| [outbound-pii-screen.md](outbound-pii-screen.md) | The pattern behind it: one detector (`ci-kit/guards/guard_no_pii_in_fixtures.py --stdin`) wired to three call sites, CI lint, pre-push git guard, and this hook, instead of three copies that drift |

This directory is a bundle seed, not a framework. It ships one worked pattern per lifecycle event, and the events compose: the stop hook guards turn end, the compaction pair guards the context window, and the prompt-side capture nudge in [../ledger-tools/capture-nudge.md](../ledger-tools/capture-nudge.md) guards the ledger. The memory desk ([../memory-desk/](../memory-desk/README.md)) ships its own trio (kernel at session start, index hits at prompt time, file notes at first edit) that registers the same way. Grow your own bundle by adding one hook per failure you have actually watched happen, and keep every hook cheap and silent by default. A hook that talks on every event is a second boot surface taxing every session ([../../docs/context-budget.md](../../docs/context-budget.md)).

## Registering hooks

Hooks register in your harness settings file (for Claude Code, `.claude/settings.json` under a `hooks` key). One entry per lifecycle event, each running a command; the paths below are examples, keep the scripts repo-tracked so they version with the code:

```json
{
  "hooks": {
    "Stop": [
      {
        "hooks": [
          { "type": "command", "command": "bash \"$CLAUDE_PROJECT_DIR/.claude/hooks/stop-hook.sh\"" }
        ]
      }
    ],
    "SessionStart": [
      {
        "hooks": [
          { "type": "command", "command": "bash \"$CLAUDE_PROJECT_DIR/.claude/hooks/session-start.sh\"" }
        ]
      },
      {
        "matcher": "compact",
        "hooks": [
          { "type": "command", "command": "bash \"$CLAUDE_PROJECT_DIR/.claude/hooks/post-compact-pointer.sh\"" }
        ]
      }
    ],
    "PreCompact": [
      {
        "hooks": [
          { "type": "command", "command": "bash \"$CLAUDE_PROJECT_DIR/.claude/hooks/pre-compact-save.sh\"" }
        ]
      }
    ]
  }
}
```

The `matcher` on the second SessionStart entry scopes it to post-compaction starts. Exit codes are the interface, and the contract differs per event: on Stop, exit 2 feeds stderr back to the agent and exit 0 stays silent; on SessionStart, stdout on exit 0 becomes model context. Know your harness's contract for an event before writing a hook against it.

## Portability

The scripts target plain bash + git + jq, and each carries a fallback (targeted grep or sed) for when jq is absent. File mtimes are read with GNU `stat -c %Y` first and BSD/macOS `stat -f %m` as the fallback; `date +%s` is portable, so nothing else in the date math varies by platform.

## Adoption notes

- Copy the scripts, register them, then trip each one on purpose once. Verifying a hook fires is a ten-second test now and a silent hole forever if skipped.
- These hooks fail open: an unreadable payload or a failed save exits 0 instead of blocking the turn or the compaction. Match that posture in your own additions unless the hook IS the gate.
- Some launchers re-provision stock hook scripts into the home directory on every fresh container. The repo-tracked re-apply pattern that survives that is in [batch-cadence.md](batch-cadence.md), Durability section.

The rules file says what should happen. Hooks are what happens anyway.
