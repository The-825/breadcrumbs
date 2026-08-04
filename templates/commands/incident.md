---
description: Incident triage + rollback playbooks. Flag flip, config revert, bad-deploy revert, data restore, user comms. Cheapest reversal first; canonical stores never dropped.
argument-hint: "<what-broke> (e.g. 'status panel showing wrong values since this morning')"
allowed-tools: Bash, Grep, Read
---

Incident response for `$ARGUMENTS`. Work the triage ladder top-down and take the CHEAPEST reversal that fixes it. State which rung applies before acting.

Fill these before first use: `<flag-store>` (where feature toggles live and how to flip one), `<config-registry>` (your central config file or table), `<hosting-platform>` (what serves the app and how it rolls traffic between revisions or releases), `<backup-store>` (where recoverable copies of canonical data live), `<canonical-stores>` (the datasets no process may ever drop), `<conclusions-store>`, `<branch-prefix>`. The binding blocks in your shared agent preamble apply (see `templates/AGENT_PREAMBLE_TEMPLATE.md` in the companion repo, or your repo's installed copy); destructive actions always wait for the operator's explicit go.

## Triage ladder

1. **Flag-revertable?** Did the broken behavior ship behind a feature flag (your flag-per-feature rule says it should have)? Flip the flag OFF. Seconds, no deploy, no data touched.
2. **Config-revertable?** Is it a threshold or setting in `<config-registry>`? Revert the value in a fix PR; no schema or data work.
3. **Deploy-revertable?** Did a bad deploy cause it? Route traffic back to the previous revision or release on `<hosting-platform>`. The code-level revert PR follows at leisure.
4. **Data-restorable?** Is canonical data damaged (bad merge, wrong update, truncation)? Restore from `<backup-store>` per Playbook 3. Slowest, most careful rung.

If none apply, it is a live bug: reproduce, fix on a `<branch-prefix>/<slug>` branch, ship through the normal lane.

## Playbook 1: flag-flip rollback

- Identify the flag: grep the route or component for the flag check, or use your flags admin surface.
- Flip it OFF in `<flag-store>`. If the store supports per-user enablement, consider leaving the owner's preview on so the fix can be verified without re-exposing everyone.
- Verify within the flag cache's TTL that the behavior is gone. Log the flip (step 2 of `/close-out` depends on it), and note the re-enable path for after the fix lands.

## Playbook 2: bad-deploy rollback

- Confirm the deploy is the cause: match the symptom's start time against the deploy history (`/verify-deploy` if installed, or your deploy workflow's run list).
- Roll traffic to the previous revision or release using `<hosting-platform>`'s mechanism. If the session cannot run it, hand the operator a runnable command with every real value filled in; a placeholder in an incident handoff wastes the minutes the rollback was meant to save.
- Traffic rollback is temporary state: open the revert or fix PR immediately so the next green deploy supersedes it.

## Playbook 3: data restore from `<backup-store>`

The shape, non-negotiable:

- **Forensics first, read-only.** If your warehouse supports point-in-time reads (time travel), query the table's state from before the bad write to scope the damage before restoring anything.
- **Additive first, always.** Copy the recovery source (point-in-time read, snapshot, or backup clone) into a scratch table. Never restore over live in one step.
- **Verify scratch vs live**: row counts, checksums, a keyed diff. Confirm the diff matches the incident story; a restore that "fixes" rows the incident never touched is a second incident.
- **Canonical stores are never dropped.** The restore lands additively; the destructive cutover (replacing live with the scratch copy) runs ONLY after the operator confirms on THIS incident. Then re-derive anything downstream of the restored table (syncs, derived statuses, caches).

## Playbook 4: comms to affected users

Send only what affected users need, plain language, no PII, no jargon. Template:

> Subject: <product> - <feature/page> issue
> The <feature/page> has been showing <wrong/stale/no> data since <time>. Everything else is working and no records were lost. We have <turned the feature off / rolled back the update / restored the data> and expect it back to normal by <time>. If you made edits in <feature/page> between <time> and <time>, hold them until we confirm. Questions to <owner>.

Skip the message entirely if the issue was invisible to users; note that decision instead.

## Close-out

Capture the incident cause and fix as a `<conclusions-store>` entry (same turn), file the follow-up fix PR, and write the postmortem as a dated file in your incidents directory using `templates/INCIDENT_TEMPLATE.md` (the misdiagnosis-lessons section is the part that pays for itself). If data was restored, sweep everything the restore touched for consistency before finishing.
