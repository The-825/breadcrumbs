# StaleToast source scout, 2026-10-11

**Status:** public-source research intake record and reviewable local ledger
change. This assumes public scholarly pages and GitHub metadata. It implements
no new discovery runtime, model, stopping rule, or public chart.

## Question and search

Which source-discovery and deduplication mechanisms improve relevant unique
qualified finds while reducing screening burden? Targets are CI-004 (cost and
burden) and CI-012 (human verification). This was a purposive gap-directed
search, with no publication-date cutoff; older methods can fill a current gap.
New means absent from the checked cumulative records, not newly published.

Exact web queries on 2026-10-11:

1. `ASReview active learning systematic reviews Nature Machine Intelligence 2021 van de Schoot`
2. `ASySD automated deduplication systematic reviews paper GitHub`
3. `citationchaser forward backward citation chasing systematic reviews 2022 GitHub`
4. `site:reddit.com ASReview citationchaser systematic review screening`

The general search surfaced scholarly records and GitHub implementations.
Primary verification used arXiv, the journal publisher, and canonical GitHub
metadata plus pinned README content. Reddit provided discovery context only;
its unverified performance claims were not imported. This search is not an
exhaustive database search or a systematic review.

Six distinct paper identities received title/identity screening: ASReview,
ASySD, Citationchaser (10.1002/jrsm.1563), the integrated collection/screening
framework (arXiv:2202.10033), Paperfetcher (arXiv:2110.12490), and Improving
Active Learning (arXiv:1801.09496). Two received primary abstract/method screens
and were included; the other four were deferred under the bounded daily scope,
not excluded on quality. Of five repository leads, three received canonical
identity screening: ASReview, ASySD, and citationchaser. Surveyer and the PISMA
pipeline remained unverified discovery leads. Two repository records were
included; citationchaser was deferred because metadata did not resolve a license.

Access failures: opening the Nature journal page returned an internal error;
ASReview's related arXiv v3 abstract and publisher-index metadata supplied the
bounded screen. PMC's ASySD page returned a browser check; the publisher's
version-of-record page was accessible. No paid corpus or credentialed API was used.

## Identity and appraisal

| Queue to ledger | Primary source or pinned repository | Depth and disposition |
|---|---|---|
| Q-P-003 to C-011 | [ASReview journal identity](https://doi.org/10.1038/s42256-020-00287-7), 2021; [related arXiv v3](https://arxiv.org/abs/2006.12166v3), revised 2020-12-04 | Screened abstract; `watch`; journal full text not appraised. Same ASREVIEW family as R-313. |
| Q-P-004 to C-012 | [ASySD version of record](https://doi.org/10.1186/s12915-023-01686-z), 2023-09-07 | Screened abstract and selected methods; `watch`; no full-text appraisal or replication. Same ASYSD family as R-314. |
| Q-R-001 to R-313 | [ASReview README](https://github.com/asreview/asreview/blob/79d568212b2b0a78f9fd7be3c5117dfb890489f9/README.md), Apache-2.0, unarchived; head dated 2026-08-31, last push 2026-10-06 | README-screened; gap is human-label-driven screening and frozen labeled-corpus simulation. Paper results do not validate current v3 behavior. |
| Q-R-002 to R-314 | [ASySD README](https://github.com/camaradesuk/ASySD/blob/7b240f14284e74d4d726e3a9a7e3c4e2bfd8a7f3/README.md), GPL-3.0, unarchived; head and last push 2026-08-07 | README-screened; gap is citation identity matching. This is supporting bibliographic infrastructure, not an agent runtime. No code adoption. |

Title, DOI, arXiv, canonical repository, alias, and fork checks found no match in
the current research ledger, repository ledger, queue, or preserved local intake
package. The related ASReview preprint is retained as a version pointer, not a
second paper. The two paper/repository pairs are two evidence families, not four
independent validations. Reserved IDs C-009, C-010, and R-312 were not reused.
The original repository rows and historical import summary remain unchanged.

## Editorial priority

Prior global chart ranks are unknown and remain unchanged. Local appraisal
priority for this question is ASySD first, ASReview second, for both paper and
implementation. ASySD has high relevance to duplicate burden and false merges;
ASReview has high relevance to screening order but requires an explicit recall
and stopping-rule appraisal. Both have medium transfer directness and high
validation gaps. This ordering is editorial work priority, not confidence,
scientific superiority, measured savings, or adoption.

## Validation boundary

Two screened research candidates and two pinned README repository records were
added locally. Appraisals, collection log, dispositions, and current summaries
were updated together. The historical 001-100 research catalog is unchanged.
The existing ledger-growth validation correction is a prerequisite: the current
branch's fixed historical total rejects any direct intake. Reviewable validation
uses the preserved growth-aware checker without changing the historical import.
The current branch's CI gate remains blocked until that separate correction is
integrated. Catalog publication is also held pending the separate per-record
popularity-date correction, so new star observations must not be presented with
the historical collection date.

Candidate workflow concepts are frozen-corpus replay for screening priority,
metadata normalization with ambiguous matches retained for review, and seed
citation expansion with database coverage recorded. None was installed or
adopted. There is no comparable prior search receipt for this exact question;
today's search cannot establish a reduction in burden or missed sources.
A subsequent comparison must freeze inputs and inclusion labels, hold effort
budgets equal, and record qualified unique finds, missed known sources,
duplicates, false positives, calls, elapsed time, and human review burden.

## Validation correction, 2026-10-12

The earlier fixed-count blocker is resolved in the local repair. Current import validation passes on 314 records; 12 landscape, 5 portfolio and 15 catalog tests pass. Live totals are checked against actual rows, historical import stays unchanged, direct intake identities are unique and existing, bulk reimport cannot erase direct intake provenance, and the renderer uses each row's observation date. This is local validation, not remote CI or release approval. Papers retain their stated abstract or selected-method screening depth; none were promoted to full-text appraisal.
