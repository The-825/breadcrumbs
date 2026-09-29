# The hidden curriculum in agent systems

**Status:** public field note. It generalizes mechanisms from a dated source intake.
It does not certify the sources, install their software, or authorize an external action.

The visible feature is usually the least interesting lesson. A memory server advertises
recall. A gateway advertises tools. A research harness advertises better results. The
development lesson sits underneath: what state must remain visible when the happy path
breaks, who owns that state, and what evidence permits the next action.

The source and disposition record is
[reddit-systems-intake-2026-09-29.json](reddit-systems-intake-2026-09-29.json).
Repository entries are pinned to the revision reviewed on September 29, 2026.

## 1. Unknown is a state

After an external request leaves your system, a timeout does not prove failure. The
effect may have happened while the response was lost. The safe lifecycle is:

1. reserve the exact operation;
2. dispatch it once;
3. record completed when a receipt arrives;
4. record uncertain when the outcome cannot be established;
5. inspect and reconcile before considering a new operation.

An idempotency key binds identity. It does not grant permission to keep sending. A safe
uncertain state remains non-retryable until another evidence source resolves it.

This public note transfers the mechanism, not an operated system's identity, internal
implementation evidence, or authority. Implementation status remains with its source.

## 2. Identity comes before shared context

A group agent needs a verified participant identity before it can decide what is shared.
Shared memory and personal memory are different scopes, not different search filters over
one undifferentiated pool. Permission to read one scope never implies permission to write
it, publish it, or copy it into another project.

This is why repository and project boundaries belong in code. The prompt can ask for a
scope, but the authenticated host decides which scopes exist and which the caller holds.

## 3. Memory needs an explanation path

Semantic recall is useful, but a score alone cannot explain why a memory appeared or why
retrieval stopped. A governable memory result needs:

- the named record and owning project;
- provenance and verification state;
- supersession and tombstone handling;
- the retrieval path or ranking trace;
- the stop reason and warnings;
- a visible refusal when scope or authority does not permit recall.

Graph recall can improve inspection. It cannot replace authority, retention, correction,
or provenance.

## 4. Discovery has a budget

Tool and agent discovery is a read path, but reads still consume time, calls, context, and
attention. A compact discovery mechanism should be compared against the current registry
on completeness, calls, bytes, latency, and unsafe over-discovery. Smaller output is not
better if it hides a required control or returns a broader tool surface than the task
needs.

## 5. Self-improvement needs a holdout

A system that edits its own research process can optimize the visible benchmark instead
of the intended capability. Preserve the full edit history, price every edit, keep one
evaluation set untouched, run a leakage check, and define the stop rule before the
experiment starts. An author benchmark motivates a trial. It does not supply the result.

## 6. Prefer the missing mechanism to the whole platform

The intake found mature external systems with memory graphs, policy gateways, workflow
graphs, voice tooling, and large collections of skills. None should be adopted wholesale
when the owning system already has the relevant control. Search the current repository
first, name the exact missing mechanism, implement the smallest native change, and compare
it against the baseline. If no gap remains, the correct disposition is study or reject.

## 7. Labels are controls

Reported, calculated, assumed, and AI-interpreted are different evidence classes.
Likewise, submitted, accepted, completed, verified, merged, deployed, and activated are
different states. Clear labels stop a plausible output from quietly acquiring authority
it did not earn.

## What this intake did not authorize

It did not authorize package installation, voice cloning, biometric storage, scraping,
Docker socket access, Reddit activity, production deployment, billing changes, or
transfer of private records. Those remain separate decisions in their owning systems.
