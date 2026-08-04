---
description: Confirm the latest merge actually rolled out by checking the deploy workflow's runs and the health endpoint's version contract. Checks reality; deploys nothing.
argument-hint: "[expected version, optional; inferred from the repo if omitted]"
allowed-tools: Bash, Grep, Read
---

Verify the live deploy after a merge to `<main-branch>`. This command checks reality; it does not deploy, re-run workflows, or merge anything.

Fill these before first use: `<deploy-workflow>` (the workflow file that deploys, e.g. `deploy.yml`), `<your-health-endpoint>` (the deployed app's health URL, if it is reachable from an agent session), `<version-source>` (the file or endpoint the repo treats as the version source of truth), `<deploy-window>` (how long a merged change can legitimately sit undeployed; for per-merge deploys effectively zero, for batched deploys the batch interval).

If deploys are batched on a schedule rather than fired per merge, a merge sitting undeployed for up to `<deploy-window>` is expected, not broken. Say so instead of raising an alarm.

## Step 1: Determine the expected version

- If `$ARGUMENTS` gives a version, use it.
- Otherwise read the expected version from `<version-source>` in the working tree. If the version is stamped by CI at deploy time rather than stored in the tree, skip the version comparison and verify by commit instead (Step 2).

## Step 2: Check the latest deploy run

- `gh run list --workflow=<deploy-workflow> --limit=3` for the most recent runs and their conclusions.
- If the workflow has a post-deploy smoke step that hits the health endpoint, a green run means the smoke gate passed; treat that as the automated verification.
- Match the deployed run's head commit against the merge in question (`git log --oneline origin/<main-branch> | head -5` for the merge SHA). Match on the commit, not on the run's trigger event; scheduled and manually-dispatched deploy runs do not carry a push event, and filtering on event type will wrongly conclude nothing deployed.

## Step 3: Check the health endpoint directly (when reachable)

If `<your-health-endpoint>` is reachable from this session (no auth wall, no egress restriction), fetch it and check the version contract:

```
curl -s <your-health-endpoint>
# expected shape: {"status": "ok", "version": "<expected-version>", ...}
```

Assert `status` is `ok` and `version` matches Step 1. If the endpoint sits behind an auth layer that agent sessions cannot pass, skip this and rely on the workflow's smoke gate; note in the report which path verified it.

## Step 4: Assert and report

- **Deployed:** the latest deploy run is green AND its head commit includes the merge in question (and the health version matches, when checked directly).
- **Rolling out / queued:** the merge landed but the next run has not fired or is mid-build. Say so; do NOT poll in a sleep loop. Offer to re-run this command later, or point the operator at the workflow's manual dispatch for an immediate rollout.
- **PROBLEM:** the deploy run failed (build or smoke gate). Report the failing step and link the run.

If the deployed commit is behind, optionally confirm the merge actually landed on `<main-branch>` before blaming the deploy: `gh pr list --state merged --base <main-branch> --limit 5`.

End with one line: "Live: v<X>: <deployed | rolling out | PROBLEM>."
