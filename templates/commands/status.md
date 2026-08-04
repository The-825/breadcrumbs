---
description: Snapshot of open PRs, local working state, what is awaiting the operator, and what is blocked.
allowed-tools: Bash
---

Produce a concise status report for this repo. No PRs to open, no code to write; synthesize from these inputs:

1. Open PRs: `gh pr list --state open --limit 20`
2. Local working tree: `git status -s`
3. Current branch: `git branch --show-current`
4. Commits ahead of the base: `git log --oneline origin/<main-branch>..HEAD 2>/dev/null | head -10`
5. Last 5 merges: `git log --oneline --merges -5`
6. Optional, if your repo surfaces a version somewhere: read it from `<version-source>` (the file or endpoint your repo treats as the version source of truth) for orientation.

Then render a status table:

```
SHIPPED (most recent 5 merges)  ->  list with PR numbers
IN FLIGHT (open PRs)            ->  PR # | title | draft? | CI status | conflicts?
AWAITING OPERATOR INPUT         ->  open questions, drafts parked on a decision
BLOCKED                         ->  items with a named external blocker
```

For the last two rows, pull from wherever your repo parks such items: the known-issues ledger in the rules file, `<roadmap-file>`, the pending-decisions section of the session handoff file. Name the blocker, not just the item.

Keep the whole report under 30 lines. End with one line: "Next recommended action: <X>", chosen by what is blocking the most work.

This command reads and reports only. It does not push, merge, label, or edit anything.
