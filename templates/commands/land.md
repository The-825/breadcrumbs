---
description: Shepherd one or more open PRs to merged. Checks, conflicts, and the correct automerge path. Read-and-shepherd only, it never merges by hand and never applies the approval label.
argument-hint: "<pr-number> [<pr-number> ...]"
allowed-tools: Bash, Grep, Read
---

Shepherd these PRs to merged: **$ARGUMENTS**

Fill these before first use: `<owner>/<repo>`, `<branch-prefix>` (e.g. `claude`), `<default-base-branch>`, `<required-check>` (the check name your merge gate waits on), `<approval-label>` (the label a human applies to authorize merge, if your repo gates on one), `<protected-paths>` (the path list that always requires the label, if your gate has one), `<conclusions-store>` (your append-only rulings ledger, if you keep one).

The binding blocks in your shared agent preamble apply (see `templates/AGENT_PREAMBLE_TEMPLATE.md` in the companion repo, or your repo's installed copy).

Hard rule up front: this command shepherds, it does not authorize. It never merges by hand, never enables auto-merge, and never applies `<approval-label>` or any other label. When a PR is green but gated on the label, report it as green-and-waiting; applying the label is the operator's act, outside this command.

**Land ONE PR at a time**, in the order given. Sibling PRs cleared as a batch race each other: the first merge modifies the base and can conflict the rest, so finish each one (merged or parked) before touching the next.

Per PR:

1. **State check**: `gh pr view <n> --json mergeable,mergeStateStatus,headRefOid,labels,files,statusCheckRollup,isDraft` for mergeable state, head SHA, labels, changed files, and check status.

2. **Workflow-file wall (check FIRST, if it applies to your setup)**: if your merge automation runs on a token without the workflows permission (most GitHub App installation tokens), a PR touching `.github/workflows/*` cannot be merged by it; the API refuses with a "refusing to allow a GitHub App to create or update workflow" error. No label cycle or re-run gets past it. Report that the operator must merge it in the GitHub UI, and move on to the next PR.

3. **Conflicts** (dirty mergeable state): resolve ON the feature branch, never on the base. `git fetch origin <default-base-branch> && git merge origin/<default-base-branch>`, fix, push the branch. For `<conclusions-store>` or any append-only ledger: UNION the tails, keeping both sides' appended lines in chronological order, drop both conflict markers, lose no entry, never pick one side.

4. **Wait for CI**: `<required-check>` must be green. Poll with backoff (`gh pr checks <n>`), not hot loops; runs take 30s+ to even show status.

5. **Merge path** (the automation owns the merge; this command never performs it):
   - **Label-free lane** (if your gate has one): a `<branch-prefix>/*` PR into the base self-merges on green checks with no label unless it touches `<protected-paths>`. Just wait and confirm. A green gate RUN is not proof of merge; the gate also ends green for PRs it decided to wait on. Confirm `merged: true` on the PR itself.
   - **Label-gated PRs**: report green-and-waiting on `<approval-label>` and stop on that PR. That state is waiting, not broken.
   - **Fail-closed states** (no merge, by design): draft PRs, zero check runs on the head SHA, any failing check, dirty or unknown mergeable state.

6. **Re-fire semantics**: if your gate triggers on `[opened, reopened, labeled, synchronize, ready_for_review]`, any push to the PR branch (conflict fix, lint fix) re-fires it by itself. One straggler case: a PR opened before the current gate definition merged runs the OLD definition until its branch is updated from the base; for those, update the branch from the base to get the current gate.

7. **Report** per PR: merged (with merge SHA) / green-and-waiting on `<approval-label>` / parked with reason.
