# Turn a useful mechanism into a bounded adoption decision

A working feature, a persuasive demonstration, and a useful research paper each
answer different questions. Record what each establishes before deciding what
to copy, deploy, or trust.

**Status:** pattern only. This document ships a review contract and synthetic
examples, not a retrieval feed, service integration, scheduler, or evaluator.
It is free to copy and adapt under this repository's MIT license.

**Assumptions:** you maintain an evidence catalog and an owning system that can
retain source records, enforce access, and make adoption decisions. No performance
benefit or production safety claim follows from completing this checklist.

## Preserve the distinction that makes the evidence useful

| Common mistake | Reusable control | Bounded acceptance example |
|---|---|---|
| A local test becomes a live-release claim | Bind test, merge, deployment and readback receipts to exact artifact versions | A successful test of version A cannot verify deployed version B |
| A missing structured field becomes an absent decision | Keep source evidence, interpretation and normalized fields separate | An explicit decision remains reviewable when a downstream field is blank |
| A declared capability becomes a recovered workflow | Separate declared controls, synthetic reproduction, recorded runtime evidence and external outcomes | Recorded failover events establish their event sequence, not a customer outcome |
| A quoted plan becomes a paid execution | Keep discovery, quote, authorization, reservation, execution and settlement distinct | A preparation receipt carries no claim that money moved or a provider ran |
| A preview becomes permission to retain sensitive data | Start with minimum necessary temporary handling and an explicit persistence gate | A fictional preview works while persistence remains disabled |
| A judge's missing or oversized report becomes a pass | Validate the report envelope and fail closed on unknown verdicts | Missing evidence yields unknown or blocked, never approved |
| An old source gets a new import date and appears current | Keep observed, source-updated, reviewed and invalidated dates separate | Reimporting a source does not renew its appraisal |
| A duplicate source becomes another independent confirmation | Preserve stable IDs, aliases and evidence-family membership | Two descriptions of one study remain one evidence family |

These are design requirements, not claims that the kit enforces every row. The
[authority ledger](authority-ledger.md), [portfolio coordination pattern](portfolio-coordination.md),
[cooperative evaluation](cooperative-intelligence-evaluation.md), and
[repository appraisal method](collaborative-intelligence-repository-landscape-method.md)
provide related contracts. Inspect each artifact's stated implementation boundary.

## Review a candidate in five steps

1. **Identify it.** Verify the public source, canonical owner, version, license,
   and existing ledger membership. Keep unknown metadata explicit. Assign a stable
   ledger ID only through the ledger's promotion process.
2. **Name the gap.** Describe the failure or mechanism the candidate addresses.
   Search the kit before adding a second implementation. Popularity and compelling
   copy are discovery signals, not independent evidence of quality.
3. **Trace the boundary.** State which code path or source supports the claim and
   which interpretation goes beyond it. Distinguish source claims from your review.
4. **Reproduce narrowly.** Use synthetic fixtures, a named baseline, a pinned version,
   a failure case, and a verifier independent of the executing actor. Report tests,
   skipped checks, errors, costs and limits without turning them into one score.
5. **Route the decision.** Send a review proposal to the owning system. Adoption,
   merge, deployment, billing, publication, protected-data access and persistence
   need their own applicable authority. Peer review grants none of them.

## Keep two living ledgers

The research ledger records studies and their bounded claims. The repository
ledger records implementation identity, evidence depth and reusable mechanisms.
Link them by claim or mechanism; do not count a paper and its authors' repository
as independent confirmation of one result.

Stable IDs identify records. Rank is a dated view over the complete ledger, not
part of an ID. New candidates do not renumber existing records. Recompute ordering
with the ledger's documented criteria and deterministic tie handling. Keep research
evidence order separate from repository audience signals. Do not replace either
with an unsupported composite quality score. Display totals from current catalog
data rather than assuming a fixed set of one hundred records.

Retain dispositions such as candidate, excluded with reason, appraised, reproduced,
adopted in a named owning system, and outcome observed. A new appraisal can change
rank without establishing reproduction or adoption. Source correction, license
change, material architecture change, or expired review evidence triggers recheck.

## Feed an owning coordinator without giving the catalog authority

An operational coordinator such as Jarvis can consume a public, read-only projection
of catalog records. The projection should include only approved public metadata and
generalized mechanism descriptions. Private source records, operational memory and
access policy stay with their custodians.

The human owner of the catalog maintains the export field allowlist. The owning
coordinator's human operator separately approves its ingestion policy. Consumers
must expire cached projections, honor revocation or withdrawal before reuse, and
remove cached payloads according to the owner's retention and deletion policy.
Keep only permitted audit references when a source record is withdrawn.

An illustrative synthetic projection is:

```json
{
  "example_only": true,
  "record_id": "candidate:synthetic-01",
  "source": "https://example.org/synthetic-mechanism",
  "revision": "fixture-v1",
  "observed_at": "2026-09-27",
  "source_updated_at": null,
  "reviewed_at": "2026-09-27",
  "invalidated_at": null,
  "mechanism": "bounded review verdict",
  "evidence_depth": "synthetic-reproduction",
  "reproduction": "passed-fixture-only",
  "adoption": "not-established",
  "outcome": "unknown",
  "authority": "evidence-only",
  "recheck_on": ["source-change", "policy-change"],
  "next_action": "review-in-owning-system"
}
```

This is an example, not a validated schema or an implemented feed. A consumer must
validate URLs and field sizes, reject unauthorized fields, identify duplicates,
check freshness and source versions, and preserve supersession. Retrieval may
produce a proposal or an unknown answer. It must not install a dependency, widen
access, store sensitive data, purchase a service, or mark a claim verified.

Here `evidence_depth` describes the review performed; `reproduction` records a
specific test result. Neither implies adoption or an external outcome. An unknown
outcome can remain a catalog observation. Unknown authorization or an unknown
verdict required for an action blocks that action. The adopter defines and
validates the allowed vocabulary and consistency rules before implementing a feed.

## Review with peers and keep the handoff short

Use one issue until a PR exists, then the PR as the shared evidence record. Name
one turn owner. Only that owner acts during the turn. Each peer writes **Did / Need
from you / Done when** and an agent identity footer. Preserve disagreements and
stop after five rounds with unresolved items assigned to a human owner.

A human direction overrides peer preferences. Establish account identity and
trusted actor provenance; footer absence alone cannot establish who acted when
agents share an account. Require agent posts to carry their identity footer and
retain host attribution. Resolve disputed authorship with the human before acting.
Record each peer's actual tools, source scope and
observed evidence. Do not infer shared authentication or invent a review receipt
because a peer was invited. The final synopsis records completed actions, peer
conclusions, disagreements, missing evidence, release boundaries and next owners.

For sensitive features, the owning coordinator records data inventory, purpose,
network boundary, retention, deletion, export, roles, consent or authority,
model-training and analytics exclusions, incident response, acceptance tests and
release boundary. Persistence stays disabled until the required product, privacy,
security, UX and implementation or QA reviews exist and a human resolves the
coordinator's synthesis. A public pattern cannot substitute for those reviews.
