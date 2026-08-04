---
description: Cut a fresh feature branch from the default base following the <branch-prefix>/<feature-slug> convention. Local branch only; nothing is pushed and nothing merges.
argument-hint: "<short-name-kebab-case>"
allowed-tools: Bash
---

Start a new feature branch named `<branch-prefix>/$ARGUMENTS`.

Fill these before first use: `<branch-prefix>` (the agent-branch prefix your repo uses, e.g. `claude`), `<default-base-branch>` (usually `main`; if your repo promotes through a staging branch, that branch instead, with a hotfix carve-out that cuts from `main` directly and says so).

Steps:

1. **Fail-safe:** if `git status -s` shows uncommitted changes, stop and tell the operator to commit or stash first. Never cut a branch over a dirty tree.
2. **Sync the base:** `git fetch origin <default-base-branch>`. Do NOT `git checkout <default-base-branch>`: swapping the working tree onto a possibly-stale local base branch strands committed edits, and the fetched ref is all this needs.
3. **Cut the branch:** `git checkout -b <branch-prefix>/$ARGUMENTS origin/<default-base-branch>`.
4. **Report state:** show `git log --oneline -5` so the operator can confirm the baseline is right.
5. **Do not pre-create changelog or doc entries.** The first edit is whatever the actual work needs; a changelog entry gets written WITH the code, not before it.

Naming discipline (the reason this command exists): the branch is slugged after the feature, and the eventual PR title names the same feature, so branch, PR title, and commit subject all read as one thing. Never push a session-named or auto-generated branch (a `ccr-*` or random-hash name) to the remote; if a session finds itself pinned to one, cut the feature branch immediately and work there.

This command creates a local branch and stops. It does not push, does not open a PR, and never merges anything; `/ship` handles push and PR when the work is ready.

End with one line: "Branch ready: <branch-prefix>/$ARGUMENTS, based on `<short-sha>` (<default-base-branch>). Ready for edits."
