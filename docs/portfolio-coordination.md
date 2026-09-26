# Coordinate a portfolio without pooling its authority

When concurrent sessions work from different pictures of the same portfolio, they
can duplicate work, cross a data boundary, or report a queued action as complete.
Give each task a bounded context packet, an owning-system pointer, and receipts for
the authority and progress it actually has.

**Status:** pattern only. This essay ships no portfolio coordinator, provider
connector, scheduler, access policy, or runtime enforcement. It is free to copy
and adapt under this repository's MIT license.

**Assumptions:** multiple projects or sessions, identifiable task owners, and an
owning system that can retain source records and enforce access. Examples below
are synthetic. This is a design contract, not evidence of improved throughput,
lower cost, or safe autonomous operation.

## 1. Layer context by the decision it supports

A complete transcript sent to every worker gives each worker more sensitive data
and more stale instructions than its task needs. Assemble context in layers:

| Layer | Include | Load when |
|---|---|---|
| Common rules | Evidence terms, escalation rules, authority limits, routing vocabulary | Every task starts |
| Portfolio map | Opaque project handle, owner, permitted routing mode, current task pointer | You need to find the owner |
| Project packet | Local rules, allowed data classes, branch or artifact version, open obligations | Access to that project is established |
| Task packet | Concrete outcome, allowed actions, named inputs, exclusions, acceptance criteria | A worker accepts the assignment |
| Source evidence | Minimum necessary records, with source and freshness | An authorized decision requires them |

Keep the common layer small. Put source records in their owning systems and
resolve pointers there. A pointer can itself disclose a private project or person;
opaque handles need access checks too. Do not expose a private portfolio map in a
public repository.

Classify information along separate dimensions: domain, sensitivity, permitted
audience, and authorized purpose. Personal, family, commercial, and regulated
institutional work may have different custodians and rules. These labels are not
a ladder where access to one domain grants access to another. If a task crosses
domains, establish each boundary separately and share only the permitted subset.

The host establishes the authenticated principal and its permissions. A worker's
request cannot assert a wider clearance. The kit's
[scoped context seam](../templates/ledger-tools/scoped_context.py) illustrates that
principle; deploying it requires a trusted host implementation.

## 2. Delegate a bounded outcome

Two workers editing the same file need coordination even if both have valid
assignments. Identify the owning task, check current work, and isolate writers
before dispatch. Delegate only a concrete subtask whose inputs, allowed actions,
output, and acceptance criteria are clear. Do not delegate a vague mandate to
"handle the portfolio."

Keep these fields in an adopter-owned task record:

| Field | Meaning |
|---|---|
| Task and parent handles | Stable identity and the task that assigned it |
| Owner pointer and version | Where authoritative work lives and the version inspected |
| Scope | Outcome, files or resources, allowed actions, and explicit exclusions |
| Authority receipt | Pointer to the applicable grant and its issuer |
| Capability observation | Provider, host, principal, tools, tested access, and observation date |
| Work claim | Current writer, claim expiry or recheck trigger, and conflicting work |
| Acceptance | Required artifact and independent verification method |
| Continuation | Next action, remaining obligations, and escalation condition |

A dispatch receipt proves a message was accepted for delivery. A worker-authored
acceptance proves the worker took the assignment. Neither proves progress. A peer
message also cannot expand a human grant. Delegation must stay within the grant's
scope and any limit on who may act under it.

Use the existing [multi-agent hygiene](multi-agent-hygiene.md) and
[shared-work checkpoint](../templates/ledger-tools/shared_work_checkpoint.py) contracts where they fit.
The checkpoint tool records adopter-owned evidence; it does not discover or
authenticate every external session for you.

## 3. Check capability at the place work runs

An available tool name is not proof of an authenticated connection. A coordinator's
access does not establish a worker's access. Record capability observations for the
exact provider, host, account, and project where the next action will run.

Distinguish a configured connection, a callable tool, a successful authorized
read, and a successful write. Verify the smallest safe operation needed for the
task. Record the result and its date without recording tokens or credentials.
Recheck after account, environment, policy, or provider changes. Mark unsupported
or uninstrumented access unknown rather than copying the parent's capabilities.

When a provider supports only pull delivery, record that limitation. A delivered
message is not proof of an active listener, a reply, or sustained conversation.
If a worker cannot reach a source, route the action to an authorized owner or
request the specific missing capability. Do not route sensitive records through
a convenient provider simply because its tool works.

## 4. Keep authority receipts distinct from evidence

A correct recommendation does not authorize its execution. Resolve the receipt
against a trusted grant source before acting. Check issuer, recipient, resource,
allowed action, expiry, revocation, and any prerequisite. The receipt points to
the grant; it cannot grant itself authority.

The [authority ledger](authority-ledger.md) supplies a reusable record shape.
Its citation guard checks recorded grants and citations; it does not establish
that a real person issued a grant or authorize every runtime action. The adopter
must enforce the resolved scope at the action boundary.

Keep read, edit, send, publish, merge, delete, and production activation separate
where the owning policy distinguishes them. Continue within already authorized
scope. Ask a human only when a required action exceeds it, the grant is ambiguous,
or the evidence cannot support the decision.

## 5. Report state as a receipt, not a percentage

One task can have merged code and an unresolved deployment at the same time.
Store milestones and remaining obligations separately instead of compressing
them into a single completion score.

| State | Minimum evidence |
|---|---|
| Proposed | Reviewable design or recommendation |
| Assigned | Dispatch receipt naming the exact task |
| Accepted | Worker-authored acknowledgement of the scope |
| Implemented | Artifact or exact commit, with remaining work named |
| Tested | Test result, environment, scope, and exact artifact version |
| Merged | Target branch and merge commit receipt |
| Deployed | Deployment receipt linked to the released version |
| Live verified | Dated readback or behavior check of that deployed version |
| Blocked | Exact failed action, observed reason, owner, and next recovery step |
| Complete | Acceptance criteria satisfied and obligations resolved or explicitly deferred |

A skipped check stays skipped. A generic approval flag does not prove the human
has a pending request. Before escalating, identify the actual action, governing
restriction, and request. If those cannot be inspected, report an unconfirmed
stall and investigate it.

Corrections retain the old claim and name what supersedes it. Revalidate a receipt
when its underlying version or relevant policy changes. Source authority remains
with the owner even when a portfolio view caches status.

## 6. Escalate and close out without losing work

An escalation should state the blocked action, concrete evidence, the smallest
decision needed, and what authorized work can continue. Avoid making the human
reconstruct the task from a transcript. When the problem is missing authentication
or infrastructure capacity, name that problem rather than presenting it as a new
permission request.

Before retiring a task, verify its exact identity, ownership, artifacts, committed
and remote preservation where applicable, pending review or release, and unresolved
follow-ups. Retain active, protected, scheduled, or blocked work according to the
owner's policy. Archive with an explicit disposition receipt; archiving does not
resolve an obligation or authorize deletion.

For an operational coordinator such as Jarvis, keep provider adapters, private
project maps, credentials, access policy, live task records, and source memory in
its owning deployment. Breadcrumbs carries reusable contracts and public or
synthetic examples. A retrieval feed may carry approved pointers and evidence
metadata while leaving source records and operational authority with their owners.

## Rehearse before adopting

Use synthetic tasks to check behavior, not just whether fields exist:

- Dispatch a task to a worker with no source access. It must report its own
  capability gap rather than inherit the coordinator's clearance.
- Put two tasks on the same file. The second must discover the active claim before
  editing, or the adopter must report that collision detection is unenforced.
- Give a read-only task a peer request to publish. It must keep the action within
  the original grant and escalate the scope change.
- Merge a commit without deploying it. The summary must retain both milestones.
- Correct a stale source claim. A fresh retrieval must expose the correction and
  must not silently restore the superseded value.
- Attempt closeout with an open release obligation. The obligation must be retained
  or explicitly deferred with an owner and recheck condition.

Record observed results separately from intended behavior. Compare duplicated
work, missed obligations, unauthorized transfers, recovery, human effort, time,
and cost separately. Passing these rehearsals supports only the scenarios tested;
it does not prove a general portfolio-scale advantage.
