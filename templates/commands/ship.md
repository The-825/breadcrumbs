---
description: Commit, push, and open a ready-for-review PR with a structured body. Opens the PR and stops. It never merges, never enables auto-merge, and never applies approval labels.
argument-hint: "<PR title>"
allowed-tools: Bash, Grep, Read, Agent
---

Ship the current branch as a ready-for-review PR titled: **$ARGUMENTS**

Fill these before first use: `<branch-prefix>` (e.g. `claude`), `<default-base-branch>` (usually `main`, or your staging branch if you promote through one), `<approval-label>` (the label a human applies to authorize merge, if your repo gates merges on one), `<changelog-file>` (optional; delete step 4 if the repo keeps no changelog).

Hard rule up front: this command ends at "PR open, URL reported." Merging is a human decision. The command never merges, never enables auto-merge, and never applies `<approval-label>` or any other label; if the repo runs a label-gated automerge, applying that label is the operator's explicit act, not this command's.

Steps:

1. **Pre-flight:** confirm the session is on a `<branch-prefix>/*` branch (`git branch --show-current`) and not on `<default-base-branch>`. If on the base branch, stop and ask; `/sprint` cuts the feature branch.
2. **Stage + diff:** `git status -s` and `git diff --stat HEAD`. If nothing is staged AND nothing is modified, stop.
3. **Cheapest parse check:** run the parse-level check for whatever the diff touches, e.g. `node --check` per changed `.js` file, `python3 -m py_compile` per changed `.py` file, a YAML load per changed workflow file. Docs-only diffs skip this.
4. **Changelog check (if your repo keeps one):** if `<changelog-file>` was modified, confirm the top entry matches the PR title's intent; if not, fix before committing.
5. **Commit:** build a multi-line commit message from the diff (or the top changelog entry when there is one). Subject line matches the PR title's intent.
6. **Adversarial verify (ship-time bar):** run `/adversarial-verify` in ship-time mode before pushing. That file is the single source for the subagent prompt and triage rules; do not restate the prompt here (drift risk). Ship-time bar: only findings that are BOTH high severity AND high confidence block the push. Everything else is logged as `adversarial noise, dismissed: <reason>` and the flow continues. On a blocking finding, STOP, propose the fix, and wait for the operator. Print the one-line outcome before the push.
7. **Pre-push gauntlet:** re-read the full diff against the PR base (`git diff origin/<default-base-branch>...HEAD`), classify the changed files, and run the cheapest regression layer that covers each class (parse checks, the relevant unit or route tests, the relevant end-to-end spec). Then confirm the diff matches the PR title's stated scope: no stray files, no scope creep. If a layer fails or the diff overshoots, STOP and fix before pushing. No "push then clean up." Print one line: `pre-flight: <layers run> green, scope matches.`
8. **Push:** `git push -u origin <branch>` with retry on network failures (2s / 4s / 8s / 16s backoff).
9. **Open the PR** ready for review, never draft: `gh pr create --base <default-base-branch> --title "$ARGUMENTS" --body "..."` with this body:

```
## Summary

<one-paragraph summary derived from the diff>

## Test plan

- <the checks run pre-push, phrased as evidence: "Ran X, N/N pass" or "Verified Y via Z">

## What's NOT in scope

- <what this PR deliberately does not touch>

## Adversarial verify

<Include ONLY if the pass surfaced findings the operator dismissed with reason.
One bullet per dismissed finding: "- <one-sentence concern>. Dismissed: <reason>".
Omit the whole section if the pass returned NOTHING or only inline-fixed findings.>
```

10. **Report the PR URL** and stop. Do not poll CI immediately; checks take time to appear.

Convention on `- [ ]` checkboxes in PR bodies: do NOT use them for test-plan items. Test-plan items are evidence of what already ran pre-push, not TODOs for a reviewer, and unchecked boxes leave a "0 of N completed" counter on every merged PR. Reserve `- [ ]` for genuine deferred work linked to an issue; otherwise plain `-` bullets that read as statements of fact.
