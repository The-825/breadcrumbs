# Finish a task with a result you can check

Pattern-only, copy-and-adapt worksheet. Use a text editor and your existing task list or board. No account, package, agent harness or service is required. This worksheet does not execute work, verify identity, grant permission or update a parent board.

Start with the intended result. A person or an agent can perform an eligible step; changing the worker does not change the task, its evidence or the acceptance rule. Keep permission and evidence checks in the system that owns execution.

## Outcome and next action

- **Task ID:** [Existing stable ID]
- **What result do you need?** [Observable result and intended user]
- **Done means:** [Acceptance rule, required validation and any human decision]
- **Parent project:** [Existing project ID, or none]
- **Current task state:** [Next / working / waiting / done]
- **Next action:** [One action, its prerequisite and who can authorize it]
- **Waiting for:** [Missing input, validation or permission; unknown is valid]

## Steps and evidence

| Step ID | Action and dependency | Work | Validation | Result and evidence | Supporting owner |
| --- | --- | --- | --- | --- | --- |
| [Stable step ID] | [Action; depends on step/input] | [Not started / performed] | [Not checked / validated / needs revalidation] | [Exact result, source revision and check] | [Role] |
| [Stable step ID] | [Next action; depends on prior result] | [State] | [State] | [Evidence or explicit unknown] | [Role] |

Performing a step and validating it are separate. A worker's statement, running process or delivery acknowledgment alone does not prove the intended result. Bind validation to the actual result and scope revision. Mark required prerequisites explicitly; a missing or uncertain result keeps dependent work open.

## Completion and parent contribution

- **Required steps with current validation:** [IDs, not an invented percentage]
- **Remaining work or blocker:** [IDs and the missing evidence]
- **Completion accepted by / evidence:** [Authorized role and exact result, or pending]
- **What this contributes to the parent:** [Accepted child outcome]
- **What remains at the parent:** [Other required outcomes, owner decision or unknown]

Do not close a parent because one child is finished. Parent acceptance must cover its declared required scope and current child revisions. Count a child's accepted contribution once, including when a different worker continues the same task.

## If work pauses, resumes or reopens

1. Preserve the same task ID, completed steps, evidence, blocker and next action when pausing. Pausing a task does not prove a submitted remote action stopped.
2. On resume, inspect saved results and current prerequisites. Reconcile an uncertain effect before retrying; do not repeat completed work solely because delivery or acknowledgment is missing.
3. On reopen, record the reason and changed scope/result revision. Preserve earlier acceptance as history, mark affected validation stale, and identify dependent work that needs rechecking.
4. If a required child reopens, flag affected parent acceptance for revalidation. Do not silently erase evidence or keep an outdated parent completion claim.

These are workflow instructions, not an implemented pause/reopen or automatic rollup engine.

## Runtime and worker details

- **Runtime observation:** [Online / offline / idle / unknown, observed time and source]
- **Execution eligibility and permission:** [Owning system's evidence, or not verified]
- **Current worker / supporting owner:** [Role and attribution]

Keep runtime status separate from task status. An idle worker cannot close a task; an offline process does not erase an accepted result. A replacement worker needs the owning system's eligibility and permission checks before acting. A filled worksheet never substitutes for those checks.

## Check whether this helps

Ask another user to identify the outcome, completed versus validated work, blocker, next action and parent contribution. Then ask them to recover one interrupted step using the evidence. Compare with the same task in the existing checklist or spreadsheet, including setup, corrections, maintenance and service costs. Record tokens only when actually observed. Unmeasured savings remain hypotheses.

[Open the read-only example](task-outcome.html). For transferring upkeep between roles, use [workflow maintenance handoff](workflow-maintenance-handoff.md) only when that transfer is needed.
