# The batch-cadence stop hook

> Part of the companion kit for *From Archivist to Architect* (The Architect's Blueprint, Book 1).

Two good rules collide at every turn end. Rule one: warn the agent when the tree holds uncommitted or unpushed work, because genuinely forgotten work is real and expensive to notice a day late. Rule two: batch your pushes, commit locally per change and push every few hours, so a dirty tree is the intended normal state for hours at a stretch. A stock always-warn stop hook cannot tell those states apart. It fires at every turn end for the whole batch window, and every false warning buys one wasted model turn (the agent stops, the hook objects, the agent spends a turn explaining that the batch is still open) while training the operator to ignore the alarm that was installed to be believed. Blanket silencing is worse: it deletes the forgotten-work alarm entirely. The fix is a window-aware hook, silent while work is fresh, loud only when work has gone stale. Install [stop-hook-batch-cadence.sh](stop-hook-batch-cadence.sh) the day you adopt a batch-push cadence.

The whole contract:

```text
clean tree, nothing unpushed                   -> silent, exit 0
dirty or unpushed, activity inside the window  -> silent, exit 0
dirty or unpushed, stale past the window       -> warn on stderr, exit 2
recursion guard · no repo · no remote · placeholder identity
                                               -> handled unconditionally, never window-suppressed
```

Exit 2 is the load-bearing part: on the Stop event it is what feeds the warning text back to the agent for one more turn. Exit 0 keeps the turn end silent. Every false exit 2 therefore has a precise price, one model turn, and that price is what makes the window worth engineering.

## The window rule

The hook measures activity, not wall-clock time since the last push. The freshness timestamp is the newest of two things: the committer time of the newest local commit, and the newest file mtime among the modified and untracked paths that `git status --porcelain` reports. If that timestamp is younger than the window, the hook exits 0 without a word.

Both inputs matter. Commit time alone misses the state where the session has been editing for an hour without committing yet. File mtimes alone miss the state where the tree is clean, everything is committed locally, and the branch is unpushed. Together they answer the only question the alarm should ask: has anything moved recently? An agent mid-batch is not forgetting its work. Work is forgotten precisely when nothing has moved.

The window defaults to 14400 seconds (four hours) and reads `STOP_HOOK_BATCH_WINDOW_SECS` from the environment, so matching it to your cadence is configuration, not a script edit. Deleted files and paths git quotes (embedded spaces, escapes) are skipped in the mtime pass; the commit timestamp covers them.

## What stays unconditional

Four checks never get window-suppressed, because they are safety and correctness, not noise:

- **The recursion guard.** The harness passes JSON on stdin with `stop_hook_active` set when this stop was itself caused by a stop-hook warning. Warning again would loop the agent forever. The hook reads the flag with jq, falls back to a targeted grep when jq is absent, and exits 0 immediately when the flag is true.
- **The not-a-git-repo bail.** No repository, nothing to check.
- **The no-remote bail.** Every warning this hook can emit asks for a push. With no remote configured, the ask is meaningless.
- **The placeholder-identity check.** Unpushed commits authored with an unset or placeholder git identity (the `(none)` domain git invents, `example.com` addresses, an empty email, the literal "Your Name") warn immediately, whatever the window says. Identity is cheap to fix before a push with `--reset-author` and painful after. When identity is configured correctly this branch stays silent, so it adds zero per-stop noise in normal operation. Extend the pattern list in the script to whatever placeholders your environment invents. One deliberate boundary: the check ranges only over commits unique to the branch relative to its own remote-tracking ref, and skips entirely when the branch has none and only the origin/HEAD fallback exists. A fallback range can include history the default branch already published (stock hooks with a fixed comparison point have flagged every squash-merge commit on main this way), and rewrite advice pointed at published commits is wrong every time it fires.

The suppression logic only ever wraps the "have you pushed lately" nag. The checks that indicate a broken setup or a doomed push stay loud.

## Durability: the launcher that puts the stock hook back

Fixing the script once is not enough when your launcher provisions the stock always-warn script into the home directory on every fresh container. You relax the hook today, tomorrow's container ships the stock version again, and the false alarms return without a diff anywhere you can see. The durable fix cannot live in the home directory at all. It lives in the repo: a repo-tracked SessionStart hook that overwrites the launcher-level script at session start.

Three properties make the re-apply safe and quiet:

- **Marker-guarded.** It greps the installed script for a string only the replacement contains (this one's header says `batch-cadence-aware`) and does nothing when the marker is present, so it runs once per container, not once per session.
- **Backed up.** The stock script is copied to a `.bak-stock` sibling before the overwrite, so diffing against or restoring the original stays a one-command job.
- **Silent.** On SessionStart, stdout becomes model context. Plumbing maintenance has no business in the context window, so the block prints nothing.

The copy-paste block, for the top of your repo-tracked SessionStart hook:

```bash
# Re-apply the batch-cadence stop hook over the launcher-provisioned stock
# script. Marker-guarded: runs once per container. Prints nothing.
STOCK="$HOME/.claude/hooks/stop-hook.sh"          # wherever your launcher puts it
REPO_COPY="$CLAUDE_PROJECT_DIR/.claude/hooks/stop-hook-batch-cadence.sh"
if [ -f "$STOCK" ] && [ -f "$REPO_COPY" ] && ! grep -q "batch-cadence-aware" "$STOCK" 2>/dev/null; then
  cp "$STOCK" "$STOCK.bak-stock" 2>/dev/null || true
  cp "$REPO_COPY" "$STOCK" 2>/dev/null && chmod +x "$STOCK" 2>/dev/null
fi
```

If your harness runs SessionStart hooks before the checkout exists, inline the replacement script as a heredoc instead of copying from the repo. The marker guard and the backup work the same either way.

## Adoption notes

- Register the script on the Stop event (registration snippet in the [README](README.md)) and trip it once on purpose: dirty a file, backdate it with `touch -d '1 day ago'` (GNU touch syntax), and confirm the warning arrives; then make a fresh edit and confirm the silence.
- With a remote configured but never fetched, the unpushed count reads as zero because no remote-tracking ref exists yet to count against. Fetch once to arm it.
- If an untracked file older than the window keeps warning, that is the alarm working: commit the file or ignore it. Do not widen the window to mute a real signal.
- Set the window from your actual cadence. A window much longer than your push rhythm never fires; much shorter and you are back to alarm training.

An alarm that fires every turn is not an alarm. Keep it rare and it stays believed.
