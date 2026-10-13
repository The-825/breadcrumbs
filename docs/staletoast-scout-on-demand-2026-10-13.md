# On-demand daily scout verification, October 13, 2026

The owner requested an immediate run of the daily discovery and ranking workflow.
This pass completed public discovery, primary-source screening, deduplication,
retained-lead intake and an end-to-end rerun of the existing ledger and chart
pipeline. It is an on-demand execution, not evidence that the 9 AM timer fired.
The workflow uses Python's standard library and the public GitHub and arXiv
sources below. No upstream package or provider was executed.

Today's unique ledger growth remains one paper candidate, C-025, and one
repository, R-336. Both were already ingested through [PR181](https://github.com/The-825/breadcrumbs/pull/181).
This rerun counts them once and retains five additional leads for later review.
See the [original intake](staletoast-scout-2026-10-13.md) and this pass's
[machine receipt](staletoast-scout-on-demand-2026-10-13.json).

## Discovery and screening

The named question was whether revised evidence and reviewed actions retain
the right authority through recovery, and how workflows and prompts can expose
failures without creating unsupported confidence. Four focused queries covered
workflow recovery, agent memory, systems and prompt evaluation. Exact queries
are in the machine receipt. This was not a systematic or exhaustive search.

Three primary publication identities and abstracts were screened. Two canonical,
public, unarchived, non-fork repository identities were checked, with pinned
README, MIT license and selected documentation collected. All five were absent
from the existing ledgers and retained pool at the time of deduplication.

| Retained lead | Source and review boundary | Next check |
| --- | --- | --- |
| Q-NEXT-032: exact-content approval across restart | [OpenMultiAgent documentation](https://github.com/open-multi-agent/open-multi-agent/blob/6ec5498643c7e431aa66751f17f47a529e7f927c/docs/durable-approvals.md), documentation screen. Its content hash does not bind live deployed code or adapters. | Compare deployment-version binding and store atomicity with WF-006 before a new article or synthetic rehearsal. |
| Q-NEXT-033: prompt evaluation cases | [Prompt Foundry evaluation guide](https://github.com/PJA-lab/Prompt-Foundry/blob/5187654d586912f1e7936013c78c88bcd9a92a27/docs/EVALUATING_PROMPTS.md), documentation screen. An evaluation checklist is not observed model performance. | Compare missing, conflicting and adversarial input checks with the native prompt library before adapting. |
| Q-NEXT-034: reconstructed actions after approval | [From Approval to Execution, v1](https://arxiv.org/abs/2609.26529v1), primary abstract only. | Appraise reconstruction, consumed versions and independent execution observations in the full methods. |
| Q-NEXT-035: repair memory or reread evidence | [When Evidence Changes, v1](https://arxiv.org/abs/2610.03902v1), primary abstract only. | Compare source-filtered rereading and total pipeline costs; do not infer workplace transfer from clinical tasks. |
| Q-NEXT-036: execution consistency beyond memory | [Beyond Corrected Memory, v1](https://arxiv.org/abs/2610.08101v1), primary abstract only. | Inspect evidence-removal design and diagnosis/recovery comparators before candidate intake. |

The [pool](staletoast-next-round-pool.json) preserves all 31 earlier records
unchanged and records the five new pins, review depths, reasons and next checks.
These leads are not ledger additions, validated findings or adopted practices.
Related questions do not make the papers and repositories independent
corroboration. Other search hits were not fully screened.

## Ingestion and ranking verification

1. Compare the pre-intake main revision with the current ledgers. C-025 is
   absent before intake and appears once now. All 334 earlier repository rows
   and the historical import summary are unchanged; R-336 is the added row.
2. Fetch R-336's README and LICENSE again at its recorded commit. Both SHA-256
   digests match the original intake receipts.
3. Rebuild all-source priorities for October 13, then check them. Research has
   123 records and repositories have 335. Both priority views remain unchanged.
4. Rebuild catalogs and rerun October 13 edition generation and check mode.
   Both frozen chart files retain their original byte hashes. The rerun does
   not duplicate identities, invent rank movement or overwrite history.
5. Run the site tests, guard tests, portfolio manifest and landscape,
   historical promotion, triage, workflow registry and reproduction checks.
   All pass. The machine receipt records each actual command and result.

The existing editorial method still determines attention order. Popularity,
family membership and rank are not evidence of scientific confidence or
consumer adoption. C-025 remains an abstract-screened candidate; R-336 remains
a README screen. No claim-register confidence was upgraded.

## Publication and recurring operation

This receipt and the retained leads use the existing PR review and automatic
main/Pages publication workflow. The recurring daily scout stays active at
9 AM Pacific, with the original one-to-two paper and repository targets.
Future runs deduplicate against dated receipts before counting daily growth.
They report screening shortfalls rather than filling quotas with weak sources.

This on-demand pass verifies execution of the workflow the owner requested now.
It does not establish future timer reliability, upstream runtime correctness,
model-output superiority or installation into a consuming system.
