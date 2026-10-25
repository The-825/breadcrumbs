# Intake and follow-up, draft local prototype

Draft, not a released workflow or connected service. This copy-and-adapt browser prototype uses invented requests only. You need a modern browser; checks use Node.js 24.22 with no packages. No sender, account connection, background worker, persistent database or authenticated permissions are implemented. Do not enter personal or sensitive data.

## Try the minimum path

1. Open index.html in a normal browser. The page loads sibling core.js and ui.js. If your environment blocks local scripts, stop and use its approved local-preview method; do not bypass a browser security warning.
2. Select Fill example and Add intake. Inspect the stable ID, owner and date.
3. Add the identical intake again. It reuses the record and records the repeat. Changed content under the same ID is rejected rather than overwritten.
4. Select Prepare follow-up, enter an invented outcome, then Record outcome. Inspect the result and ordered history. Done means this local exercise, not delivery of a real message.
5. For failure recovery, select Simulate a failed action before preparing follow-up. State stays unchanged. Retry after inspecting the recorded failure.

Customize field labels and unique lowercase keys in the JSON editor before creating records. The fields.json file is a starting definition; the browser editor controls the current session. Reload clears memory. CSV/JSON download is an explicit local file save. JSON import is not implemented.

## Held work and review

A missing required date retains the request as held/unknown. Prepare date question once creates a reusable unsent clarification. Other missing required fields stop intake. You mark conflicting instructions yourself; no automatic prose interpretation is claimed.

To correct a held request, enter its ID, corrected fields and review flags. Explain the change and select Resolve held request. Prior values remain in history; edits clear stale draft text. A resolved date or conflict can resume the normal path. Conflict-held requests cannot draft. A missing-permission request can prepare an explicitly unsent draft while staying held.

A missing delivery acknowledgment holds new drafting and scheduling. Clearing it requires a reference beginning SYN-EVIDENCE- in this simulation. The resulting synthetic evidence field does not authenticate a receipt; sent remains not_connected. Real uncertain effects need the authorized owning system's reconciliation, not this prototype. A simulated permission declaration never authorizes sending.

## Run the checks

From this directory:

```
node test.js
node six-case-check.js
node recovery-test.js
```

The six-case runner writes invented packet/results files locally; these generated files are ignored by Git. It checks complete request, missing date, human-marked conflict, repeated ID, unauthorized external action and missing acknowledgment. Outcomes include held requests, not six completed tasks. The recovery runner checks resolution, prior-state retention, stale-draft invalidation and newly asserted acknowledgment uncertainty. All actions are local logic; there is no executor.

schema.sql is a proposed SQLite shape, not an enabled storage layer or production migration. The browser uses memory only. It does not enforce access control, immutable audit history or crash-safe persistence.

## Evidence and unfinished work

Local logic checks have been exercised on Node24.22. Browser/mobile usability for the current draft remains unverified. No connected Trust Plane adapter, authenticated approval, external receipt verification, automatic parent rollup or production delivery has been established. Keep task/step validation and runtime status separate; use the existing [task-outcome worksheet](../workflow-worksheets/task-outcome.md) for acceptance and parent contribution.

Potential work removed is repeated intake setup and reconstructing follow-up history. Work transferred includes maintaining fields, reviewing flags and checking outputs. Compare the same task with an existing checklist or spreadsheet, including setup, corrections, maintenance and service costs. No matched comparison, measured time/token savings or recurring service-cost result is claimed.

This directory is preserved for review and further consumer checks. Its presence on a draft branch is not installation, adoption, merge or deployment approval.
