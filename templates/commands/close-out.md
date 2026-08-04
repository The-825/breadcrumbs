---
description: End-of-session close-out bundle. PRs accounted for, feature-toggle state noted, every ruling captured, ledgers ticked, then /checkpoint to refresh the handoff.
argument-hint: "[optional note folded into the checkpoint]"
allowed-tools: Bash, Grep, Read, Edit, Write
---

Close out the session so nothing this session produced evaporates. Work the checklist in order; each item ends in a one-line status.

Fill these before first use: `<branch-prefix>`, `<approval-label>`, `<flag-store>` (wherever your feature toggles live: a flags table, a config file), `<conclusions-store>` (your append-only rulings ledger). Delete the steps that reference things your repo does not keep.

## 1. Open PRs accounted for

`gh pr list --state open --limit 20` plus this session's branches. Every PR this session touched is either merged, green-and-waiting on `<approval-label>` (say so, that is not broken), or explicitly handed off with its blocker named. Merged is not the finish line when deploys are batched: note per merged PR whether the change has actually rolled out (`/verify-deploy` if installed, or the deploy workflow run matching the merge SHA) or is still waiting on the next deploy window.

## 2. Feature-toggle state

Anything toggled this session in `<flag-store>`: note the flag, the hop (OFF / owner-only / role pilot / default-ON, or whatever ladder your repo uses), and whether any seed or snapshot file that mirrors the store was regenerated. Runtime toggles rarely write back to seed files, so an unnoted flip is invisible to the next session.

## 3. Rulings all captured

Grep `<conclusions-store>` for this session's topics and today's date. Every ruling the operator issued this session must already be there (same-turn capture is the mechanism; this step is the backstop, not the mechanism). Any miss gets appended NOW.

## 4. Active ledgers ticked

Any review ledger or punch-list this session advanced: statuses ticked, rulings recorded verbatim, shipped items struck through with their PR numbers.

## 5. Refresh the handoff

Run `/checkpoint` (with `$ARGUMENTS` as the note if given). That command owns the session handoff file: current branch, in-flight edits, next steps, pending decisions, the irreplaceable-values section preserved verbatim. Do not duplicate its work here.

## 6. Report: the three-way ledger

End with a three-way ledger, not a prose recap (this is the answer to "anything else to close out?"):

- **(a) Done and verified**: each item merged AND rollout-verified (or explicitly "merged, awaiting the next batched deploy"), with the toggle state it shipped in (flag name + hop, from step 2).
- **(b) Operator-side steps**: anything only the operator can run, as exact copy-paste blocks with real values, naming WHICH host or console each runs on. No placeholders in a handoff block; resolve the real values first.
- **(c) Parked on their call**: items awaiting a ruling, an approval, or a pointer, each with a one-line "what unblocks it." This is the board the operator pulls from days later; keep it complete.

Plus rulings captured (count), ledgers ticked, checkpoint done.
