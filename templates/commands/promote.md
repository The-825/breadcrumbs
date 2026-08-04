---
description: Drive one staging-to-main promotion end to end - preflight, the promotion PR, the known gate snags, and the post-merge staging reset. The gate owns the merge; the operator's label (or a cited promotion grant) releases it.
argument-hint: "[optional: 'preflight' to run the checks and stop before opening the PR]"
allowed-tools: Bash, Read, Grep
---

Run one staging-to-main promotion per docs/staging-promotion.md (the
model; this command is the session driver). Never merge by hand: the
automerge gate owns the merge, and the promotion PR merges only on the
operator's approval label, or, if you wired authority-ledger Phase 2, a
cited promotion-window grant. If **$ARGUMENTS** says `preflight`, stop
after Step 1 and report.

Fill these before first use: `<staging-branch>`, `<main-branch>`, and the
name of your staging-reset workflow (the kit ships one:
ci-kit/workflows/staging-reset.yml).

## Step 1: preflight (read-only)

1. `git fetch origin <main-branch> <staging-branch>` first; never reason
   from cached refs.
2. **Staging exists.** "Couldn't find remote ref" is the known auto-delete
   snag: a promotion PR whose head IS the staging branch gets the branch
   auto-deleted by the platform's delete-head-branch setting the moment it
   merges. Recovery: dispatch the staging-reset workflow, which
   force-pushes staging back to main's SHA and recreates the ref (nothing
   to lose, the guard passes trivially). Then re-fetch.
3. **Staging is a superset of main** (`git log origin/<main-branch> --not
   origin/<staging-branch> --oneline` is empty). If main has commits
   staging lacks (a hotfix landed direct), merge main into staging first
   and let its checks re-run.
4. Checks green on staging's head; list what the promotion carries
   (`git log origin/<main-branch>..origin/<staging-branch> --oneline`).

## Step 2: open the promotion PR

Head `<staging-branch>`, base `<main-branch>`, ready-for-review. Title
names the wave (`chore: promote staging to main (<date> <wave>)`); the
body lists the riding PRs by number and title, so the operator approves a
manifest, not a diff dump.

## Step 3: the known snags while it waits

- A label added by automation emits no workflow event; the gate only sees
  it on the PR's next real event. Unstick: toggle the label by hand.
- Zero check runs on the head SHA: empty commit to fire CI.
- A conflict means main moved after preflight: repeat Step 1.3 on the
  staging branch and push.

## Step 4: after the merge

Reset staging onto the new main (the same staging-reset workflow), so the
next cycle starts from a clean superset. If your deploys batch on a
schedule, say which firing will carry the promotion rather than implying
it is live; confirm on the deploy lane's own evidence when it runs.

End with: what rode, the PR number, its state, and the reset confirmation.
