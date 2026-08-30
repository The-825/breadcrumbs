# Merge-lane companions: operator conveniences around the approval label

The automerge template in this directory ships label-gated by default (`REQUIRE_LABEL` in
`automerge.yml`; see `AUTOMERGE_GOTCHAS.md`, "The operator-label gate"): checks green is
necessary, and an operator-applied approval label is the explicit merge instruction. That
gate buys a human in the loop at the cost of one manual action per PR.

The three workflows and one template in this set exist to make that manual action cheap
without removing it. The framing matters, so here it is plainly: **these are conveniences
around a human-held approval, not a replacement for it.** The comment command and the bulk
labeler only APPLY the label. Neither one merges anything, and neither one decides
anything. The merge gate evaluates separately, with its own fail-closed guards, exactly as
it would if the operator had clicked the label in the GitHub UI. The human step stays; it
just stops being tedious.

## The pieces

### `greenlight-all.yml`: batch-apply the label

Manual dispatch only. Sweeps every open, non-draft PR on the agent branch namespace,
checks that ALL check runs on the head SHA are completed and none failed (zero check runs
counts as not green), and applies the approval label to the green ones. A run-summary
table reports every PR touched or skipped and why. Use it when a review session ends with
a wave of PRs the operator has looked at and wants released together: dispatching the
workflow is the approval action.

### `greenlight-command.yml`: apply the label from a comment

The operator comments the approval word (`greenlight` or `gl`, as the entire comment
body) on a PR and the workflow applies the label, with a +1 reaction as the receipt.
Built for the phone-review case: a comment is one line; the label UI is four taps.
Authorization is an explicit allowlist of GitHub logins checked against the verified
event payload, never against comment text, and the comment body flows through `env`
rather than `${{ }}` interpolation so it can never execute as shell.

### `auto-update-branches.yml`: keep agent branches current

When the base branch moves, server-side update-branch every open agent PR that is behind
(zero checkout cost). This is what re-fires checks: a PR that went green last Tuesday is
green against last Tuesday's base, and updating the branch makes the gate's evidence
current. On a merge conflict it applies one `needs-conflict-resolution` label and posts
one comment naming the resolution recipe, idempotently (no comment spam on repeated
firings); a later clean update removes the label automatically. The file's header
carries the loop-termination argument for why the update -> checks -> automerge -> push
cascade is bounded, and the token trade-off (a PAT makes the pushed merge commit re-fire
checks; the default `GITHUB_TOKEN` updates the branch but fires no runs).

### `../pull_request_template.md`: the judgment-only PR template

Summary / Versions / Test plan / What's NOT in scope. The pre-flight block inside the
test plan carries ONLY the judgment calls robots cannot check (flag seeded default OFF,
view shipped through the view layer, thresholds in the config registry, source sweep
recorded), answered in prose. Deliberately no checkboxes: test-plan items are evidence of
what already ran, not reviewer TODOs, and a wall of pre-ticked boxes trains everyone to
stop reading. Everything a robot CAN check belongs in the guards and gates, not in the
template.

## The no-event label-add gotcha

Both labeler workflows carry this limitation in their headers because it is the single
most surprising behavior in the set, learned in production rather than from the docs:

**Labels added with the default `GITHUB_TOKEN` emit no run-starting events.** That is
GitHub's recursion guard, the same one behind the automerge deploy gotcha in
`AUTOMERGE_GOTCHAS.md`. Two consequences:

1. A merge gate with a `pull_request: [labeled]` trigger will not fire from these
   workflows' label-adds. The `labeled` event only starts runs when a user (or a PAT or
   GitHub App identity) applies the label.
2. A gate that reads labels from its frozen event payload (the `github.event` snapshot
   taken when the run started) cannot see a label added after that event was captured.

Net effect: the label lands immediately, and the merge gate evaluates it on the PR's
**next** event: a new commit, a draft flipped to ready-for-review, or a manual label
toggle in the UI. In practice this is fine, because `auto-update-branches.yml` and
ordinary agent activity generate those events anyway. But do not stand at the Actions tab
waiting for an instant merge after a batch labeling run; that is not how the event model
works. For a same-instant merge on one PR, toggle the label by hand in the UI, which does
emit the event.

**Closing the gap instead of just documenting it.** If your merge gate accepts a
`workflow_dispatch` `pr_number` input and resolves PR state (labels included) live rather
than from the frozen event payload, both labeler templates now add a re-evaluation step
right after the label: `gh workflow run <merge-gate> -f pr_number=<n>`. That dispatch run
sees the label because it reads live, closing the gap without waiting for an unrelated
event. It costs one more `actions: write` permission and one more line; delete the step if
your gate has no dispatch trigger; the label still lands either way. Learned in production
the same way the gotcha itself was: hand-added independently to several downstream repos
before it made it back into this template.

The honest version of this note belongs in your own workflow headers too. A teammate who
runs the batch labeler and sees nothing merge will conclude the lane is broken unless the
file itself says "the label lands now, the merge follows on the next event."

The merge-gate side of this same mechanism is gotcha 7 in `AUTOMERGE_GOTCHAS.md` (labels
are read from the frozen event payload); this section and that one describe the two ends of
one behavior.

## Fail-safe defaults across the set

Every file in the set is written to fail closed and to fail loudly:

- **Zero check runs is not green.** The bulk labeler refuses to label a PR whose checks
  never started. A missing checks workflow must read as "not ready," never as "nothing
  failed."
- **A failed read is a failed run.** If the check-runs API read fails (a token missing
  `checks: read` is the classic cause), the sweep exits with an error annotation instead
  of silently labeling nothing. An earlier production variant suppressed that error with
  `2>/dev/null` and died quietly; a gate helper that cannot see checks must say so.
- **Authorization from the verified payload, never from text.** The comment command
  authorizes on `github.event.comment.user.login` against an explicit allowlist. Comment
  bodies are attacker-controlled on a public repo; payload identity is GitHub's own
  attestation of who commented.
- **Untrusted text stays out of shell.** The comment body reaches the shell only through
  `env`, never through `${{ }}` interpolation inside `run:`.
- **One label, one comment, idempotent.** The branch updater flags a conflict with a
  single label and a single comment, only when the label was newly added, and clears the
  label on the next clean update. Re-firing never spams the PR.
- **Pushes go to PR heads only, never to the base.** The branch updater cannot re-fire
  itself directly, and its indirect cascade strictly shrinks the set of open agent PRs,
  so it terminates.
- **The conveniences hold no authority.** Remove all three workflows and the merge lane
  still works; the operator is back to clicking labels by hand. Nothing in the set can
  merge a PR, approve its own change, or widen the gate.

One more adoption note: these files ARE merge machinery. If you run a protected-paths
policy that human-gates changes to the merge gate itself, list these workflows in it. A
workflow that applies approval labels, or that pushes to every open PR branch, deserves
the same skepticism as the gate it feeds.

## Lane-hardening notes from production mileage

Three small, cheap hardenings that each closed a real annoyance:

- **Gate the deploy lane on the test lane, explicitly.** If deploys batch on a schedule, make the deploy workflow run the full test suite (or require the checks workflow's success) BEFORE build-and-push, so a red test lane blocks every deploy instead of racing it. The failure this closes: a lint-guard defect merged to the default branch quietly rides the next scheduled deploy.
- **Make workflow shell guards SIGPIPE-safe.** A guard step that pipes into `head` or `grep -q` can die on SIGPIPE with the step reading as failed (or worse, as passed, depending on pipefail) once the reader closes early. Structure guards so the producing command cannot outlive its reader, or read into a variable first; the symptom is a safety guard that intermittently reds a healthy run.
- **Cache the browser install in end-to-end lanes.** A Playwright-style `install --with-deps` on every run is often the single largest line in the lane's bill. Cache the browser directory keyed on the framework version and gate the install step on a cache miss; runs drop by minutes and the lane's cost stops scaling with merge count.
