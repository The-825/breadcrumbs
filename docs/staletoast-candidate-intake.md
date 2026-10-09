# StaleToast candidate intake

**Status:** public research queue and pattern-only method. It does not implement a
scout, establish research validity, or change shipped guidance. This pass assumes
public paper pages and public repositories. Verified source identity is not
verified performance.

## Use the existing records

A candidate can disappear between discovery and appraisal, or be counted twice
under a new title. Keep this queue as a short routing view, then promote into the
existing [source ledger](collaborative-intelligence-research-ledger.md), [source
appraisals](collaborative-intelligence-source-appraisals.md), [claim
register](collaborative-intelligence-claim-register.md), or [repository
landscape](collaborative-intelligence-repository-landscape.md). Do not maintain a
second findings ledger.

1. Start each scout pass with a named `CI-###` claim or design question. Search
   public GitHub, public Reddit discussions, scholarly sites, and the general
   web as discovery channels. Log the date, sources searched, exact query,
   date window, inclusion and exclusion rules, and inaccessible material under
   the collection rules in [Method v2.0](collaborative-intelligence-method-v2.md).
   A scout hit is a lead. A Reddit discussion is not evidence for a paper's
   result or a repository's mechanism; follow it to a primary source.
2. Open the primary paper page or canonical public repository. Record its stable
   arXiv, DOI, or repository URL; source version or 40-character commit; source
   date; verification date; and public evidence pointer. Check title, authors,
   aliases, fork or product lineage, and existing ledger IDs before assigning a
   queue ID. Use `Q-P-###` for papers and `Q-R-###` for repositories. Keep the ID
   after disposition; link duplicates to the surviving ID.
3. State the exact claim fit and what was actually read. Use Method v2.0 paper
   depth or the [repository method](collaborative-intelligence-repository-landscape-method.md)
   depth. Record both supportive and contrary signals, uncertainty, possible
   shared evidence family, and the next check. A repository README claim is a
   mechanism observation at most, not an outcome test.
4. Rank appraisal work by claim relevance, potential to change an existing
   conclusion, directness, evidence gap, and independent evidence family. Mark
   each dimension high, medium, low, or unknown with a short reason. Order by
   the strongest case for reducing a consequential uncertainty, not by source
   count, stars, recency, or a composite score. Ties remain ties.
5. Set one intake state: `verify`, `appraise`, `watch`, `duplicate`, `exclude`,
   or `promoted`. Give the next check or exclusion reason. `Promoted` means
   linked records were updated at their defensible depth; it never means a
   finding was adopted. Compare any proposed public guidance change against
   the exact evidence and route wording through separate review.
6. Reassess the queue and linked records when the paper is revised, corrected,
   or published; a repository's pinned revision, license, or lifecycle changes;
   contrary evidence arrives; or Method v2.0's task, model, policy, population,
   outcome, or implementation triggers apply. Record the old and new rank,
   reason, date, and affected IDs. Do not silently overwrite an appraisal.

For a paper promotion, add its identity and bounded finding to the source ledger,
its depth and risk flags to source appraisals, then update the claim register
only if claim-specific evidence warrants it. For a repository, first reconcile
identity and lineage against the 311-entry public landscape and its collection
log. Portable identity intake may expand; a detailed appraisal requires a named
mechanism gap, pinned snapshot, and the repository method's evidence procedure.
The detailed-appraisal saturation rule does not cap portable intake.

## Rolling chart and cumulative archive

The proposed StaleToast view uses two dated editorial charts: one for
collaborative-intelligence papers and one for public repositories that work
with agentic methods, models, or concepts. The existing ledgers retain the
cumulative archive behind both.
The charts are not scientific confidence rankings, adoption lists, or a
permanent top-100 limit. Link entries across charts through a shared `CI-###`
claim or named design question, while using paper validity and repository
mechanism evidence separately. Show each entry's as-of date, current and prior
rank, movement, rank reasons, evidence state, and history link. A drop from a
chart does not delete an archived source or reverse a prior appraisal. Re-rank
only on a logged new source, claim need, contradiction, correction, or material
change, and preserve the previous rank and date.
Chart publication and rank history are not implemented in this change.

## Reviewed downstream handoff

A ranked candidate may suggest a source-linked proposal for an owning
repository's memory or development backlog. Name the target, bounded
claim or problem, evidence state, next test, and owner. Review the proposal in
that repository before changing its records or plan. Do not copy a source
summary into memory as a confirmed fact or treat chart rank as adoption
authority. Keep private target context in its owning repository; this public
queue contains only public sources and public-safe aggregate relevance.

## First source-checked pass

**Question:** Which public studies could test memory authority or repeated
human-agent adaptation under `CI-009` and related governance claims?
**Scout:** gap-directed review of two supplied arXiv leads on 2026-10-08.
**Query:** exact identifiers `2609.01836` and `2609.04141` at arxiv.org.
**Screen:** two primary abstract pages opened; both included as distinct
preprints, with no matching arXiv ID or title in the existing public docs.
Full-text methods, independent replication, and repository code were not
reviewed. No repository candidate was verified in this pass.

| Queue ID and primary record | Claim fit and screened signal | Rank and reason | State and next check |
|---|---|---|---|
| Q-P-001: [Cerruti, Okamoto, and Erol, arXiv:2609.01836v1](https://arxiv.org/abs/2609.01836), submitted 2026-09-01; verified 2026-10-08 | `CI-009` memory and authority boundary. The authors report a benchmark in which incorrect stored permissions led to unauthorized actions and describe safeguards with a legitimate-action tradeoff. This is an abstract-level account of the authors' tests, not independent validation or a general rate for deployed agents. | High relevance, high potential to qualify memory authority, medium directness, high appraisal gap, unknown independence. First for full-text appraisal. | `appraise`: inspect task construction, authorization ground truth, baselines, false rejection, and transfer before touching the claim register. |
| Q-P-002: [Wang et al., arXiv:2609.04141v1](https://arxiv.org/abs/2609.04141), submitted 2026-09-03; verified 2026-10-08 | `CI-009` repeated interaction and `CI-004` human effort. The authors report adapting agents to individual writing and visual tasks and an evolving evaluation rubric. The abstract does not establish net benefit after collection, review, and adaptation costs, or authorize persistent personal data collection. | Medium relevance, medium potential to qualify the claims, medium directness, high appraisal gap, unknown independence. Second for full-text appraisal. | `appraise`: inspect comparators, task split, participant selection, cost, retention, and failure measures before touching the claim register. |

Both records are `screened` only at the abstract level. They are distinct from
the existing paper records by arXiv ID and title. Their findings are reported
claims, not adopted findings. A later pass must record its own search and
screening counts rather than treating this bounded lead check as exhaustive.
