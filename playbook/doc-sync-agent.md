# The doc-sync agent

Documentation rots on a schedule you can predict: true at commit 1, mostly true at commit 50, lies by commit 200. When the only sync mechanism is one person remembering to update the README after each merge, the docs decay exactly as fast as that person gets busy, and they are usually the same person whose absence the docs were supposed to survive. The fix is an agent that reads what actually merged and updates the docs on a cadence, with a hard contract limiting what it may touch. Below is the pattern as a pair: the workflow that schedules it and the prompt that constrains it.

## How it works

The agent runs in batch mode. A lightweight moving tag marks the last commit already considered for doc sync. Each run diffs from that tag to the current head, updates only the documentation files in its scope (README, CHANGELOG, runbook, roadmap), and opens a pull request rather than pushing to the default branch. The cadence is two triggers: a gated merge trigger (every Nth merged PR, so the agent is not paying for a run per merge) plus a weekly cron backstop that no-ops when the gated runs already kept up. A successful run advances the tag, so the next run starts where this one ended.

Two properties carry the whole design. Least privilege: the workflow can write a branch and open a PR, nothing else, and the agent inside it can edit a named list of doc files, nothing else. Reviewability: the output is an ordinary PR that a human approves, so a hallucinated changelog entry dies in review instead of landing on the default branch.

## Part 1: the workflow sketch

```yaml
# doc-sync.yml
# Cadence: a push trigger gated in-job to every Nth merged PR, plus a
# weekly cron backstop that no-ops when the marker is already current.
name: Doc sync

on:
  push:
    branches: [main]
  schedule:
    - cron: '0 14 * * 0'
  workflow_dispatch: {}

# Least privilege: write a branch and open a PR. Nothing wider.
permissions:
  contents: write
  pull-requests: write

# One sync at a time; let a running sync finish rather than cancel it.
concurrency:
  group: doc-sync
  cancel-in-progress: false

jobs:
  doc-sync:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0
          fetch-tags: true

      # Resolve the sync window. The moving tag doc-synced marks the last
      # commit already considered. First run (no tag) falls back to a
      # 7-day window. On push events, gate to every Nth merged PR by
      # parsing the PR number from the squash-commit subject, and skip
      # the agent's own doc-sync merges entirely (loop prevention).
      - name: Resolve window
        id: window
        run: |
          set -euo pipefail
          MSG=$(git log -1 --format=%s HEAD)
          if printf '%s' "$MSG" | grep -qi '^docs: scheduled doc sync'; then
            echo "count=0" >> "$GITHUB_OUTPUT"; exit 0
          fi
          BASE=$(git rev-parse doc-synced 2>/dev/null \
            || git rev-list -n1 --before='7 days ago' HEAD)
          {
            echo "base=$BASE"
            echo "count=$(git rev-list --count "$BASE"..HEAD)"
          } >> "$GITHUB_OUTPUT"

      # Run the agent headlessly over the window. The window is passed
      # via env so the prompt file stays static. Allowed tools are the
      # minimum the task needs: read, edit, search, and shell for git.
      - name: Run doc-sync agent
        if: steps.window.outputs.count != '0'
        env:
          AGENT_API_KEY: ${{ secrets.AGENT_API_KEY }}
          SYNC_BASE: ${{ steps.window.outputs.base }}
          SYNC_HEAD: ${{ github.sha }}
        run: |
          agent-cli -p "$(cat .github/doc-sync-prompt.md)" \
            --allowed-tools "read,edit,grep,bash"

      # Open a PR rather than pushing to main. The sync is reviewed
      # like any other change; a wrong entry dies in review.
      - name: Open follow-up PR
        if: steps.window.outputs.count != '0'
        uses: peter-evans/create-pull-request@v6
        with:
          branch: docs/sync-${{ github.sha }}
          base: main
          title: "docs: scheduled doc sync"
          body: |
            Automated doc sync covering all merges since the last marker.
            Review that the CHANGELOG entry matches what actually shipped
            and that no invented features appear.
          labels: docs
          delete-branch: true

      # Advance the marker so the next run starts where this one ended.
      - name: Advance marker
        if: steps.window.outputs.count != '0'
        run: |
          git tag -f doc-synced "$GITHUB_SHA"
          git push -f origin refs/tags/doc-synced
```

Swap `agent-cli` for whatever headless agent runner you use; the surrounding structure does not care.

## Part 2: the agent prompt template

Save as `.github/doc-sync-prompt.md`. The scope list and the hard contract are the load-bearing parts; everything else is instructions.

```markdown
# Doc-sync agent

You keep this repo's documentation aligned with the code. You run on a
batch cadence: one or more PRs merged since the last sync, given as a
commit window in env vars SYNC_BASE and SYNC_HEAD.

## Scope: the ONLY files you may edit

- README.md
- CHANGELOG.md
- docs/runbook.md
- docs/roadmap.md

Anything outside this list is out of scope. If a merge in the window
needs a change elsewhere, flag it in your final report; do not touch it.

## What to do

1. Inspect the window with `git log SYNC_BASE..SYNC_HEAD --oneline` and
   `git diff SYNC_BASE..SYNC_HEAD --stat`. Read per-file diffs only for
   files relevant to the doc scope, a few at a time. Never dump the full
   unfiltered diff of the whole window; a weekly window can exceed your
   context. Work from the log subjects and the stat, drill in as needed.
2. Produce ONE consolidated sync covering the whole window: one
   CHANGELOG entry summarizing the batch (not one entry per PR), one
   runbook update if operational behavior changed, one roadmap status
   update for anything the window completed.
3. Match the existing voice and entry format in each file exactly. The
   file's current style wins over any template.
4. Before exiting, run a cross-doc drift scan: grep the docs for stale
   references the window made wrong (renamed files, removed endpoints,
   changed commands) and report each hit, fixed or flagged.

## Hard contract (never violate)

- Edit docs only. Never code, config, schema, tests, or workflows. If a
  merge shipped a real bug, flag it in your report; do not fix it.
- Never delete records. No removing CHANGELOG entries, ledger entries,
  or known-issue items, even ones that look obsolete.
- Never bump what you do not own. Version strings stamped by CI or owned
  by another process are read-only to you; describe them, never set them.
- Do not invent features. Nothing goes in the CHANGELOG that the diff
  does not show. When unsure, prefer a shorter accurate entry over a
  longer plausible one.
- Do not loop on your own merges. If the newest commit is a prior doc
  sync, exit without changes.
- Your output is a reviewable PR. Write for the human who will approve
  it: cite the commits behind each entry.

If nothing needs updating, print exactly DOC_SYNC_NO_CHANGES and stop.
```

## Adoption notes

Start with a scope of two files (README and CHANGELOG) and widen only after a few clean cycles; a narrow scope makes the first reviews fast and builds trust in the contract. Keep the gate number modest (every 10th merge works well) so the agent-minutes cost stays flat as merge volume grows. And the corollary for humans: once the agent owns a doc surface, stop hand-editing what it maintains, because dueling editors is how drift comes back.

A cadence lesson from production mileage: at high merge volume the Nth-merge trigger eventually loses to a plain daily run. One pass every morning over the prior day's merges produces one coherent, reviewable PR per day, keeps the moving-tag logic trivial (yesterday's boundary, not a modulo counter racing concurrent merges), and costs a fixed number of agent minutes regardless of how busy the day was. The Nth-merge gate plus weekly backstop above is still the right way to START, because at low volume a daily run mostly no-ops; switch to daily when the every-Nth runs start firing more than once a day.

This agent is one instance of a general shape. The scope line, the hard contract, the PR-not-push posture, and the `DOC_SYNC_NO_CHANGES` sentinel are all specific expressions of [the unattended agent contract](unattended-agent-contract.md), which covers the same ground for any scheduled agent: the mode switch, the enforced write surface, the bounded read set, degrade-do-not-hard-fail, and the triage-only posture. If you are wiring a second scheduled agent for a different job, start from that contract rather than copying this one.

The docs your team trusts are the ones something is responsible for. Make that something a process, not a person.
