# Requested source expansion, 2026-10-12

**Status:** 10 paper candidates and 20 repositories added locally at stated review depth; all-source appraisal priorities rebuilt. Publication is authorized; finding promotion and adoption remain separate review decisions. Assumes the existing research and repository methods.

The research ledger now contains 100 historical reviewed-catalog records plus 22 candidates, including C-015 through C-024 from this expansion. Nine new candidates received selected full-text review and C-023 received primary-abstract review because its proceedings download failed. This is not 10 completed full-text validity audits. The repository ledger grew from 314 to 334, with 229 README-screened mechanism records and 105 portable-only identity records. All 314 prior rows and the historical import summary are unchanged.

## Search and selection

Exact queries on October 12, 2026 Pacific:
- `agent failure recovery benchmarks multi agent handoff evaluation 2026 papers`
- `human AI collaboration longitudinal field randomized study 2026 complementary performance`
- `agent memory benchmark 2026 long horizon memory evaluation arxiv`
- `GitHub durable agents agent evaluation recovery benchmark 2026`
- `MemoryArena benchmark github paper`
- `MemoryAgentBench github 2507`
- `Why Do Multi-Agent LLM Systems Fail MAST github`
- `AgentAsk Multi Agent Systems Need to Ask github`
- `AgentHarm github benchmark official`
- `LongMINT github UNC`
- `RE Bench METR github 2411.15114`
- `BEAM long term memory benchmark 2510.27246 github`
- `MemoryArena github Zexue He repository`
- `github agentharm ai safety institute official code`
- `github agentops pydantic logfire agentevals official`

Search channels: primary arXiv/ACL/AIS pages and public canonical GitHub APIs/READMEs; general search and Reddit results were discovery only. No date filter or exhaustive recall claim. Ten distinct paper identities were selected; other paper leads are retained in the pool and were not appraised as exclusions. Thirty-four requested repository identities were collected or attempted; 20 were selected, and 14 were deferred/unverified/lineage. A wrong repository guess is an unverified lead, not a confirmed nonexistent project. License metadata NOASSERTION was resolved by pinned license text for Inngest, RE-Bench and BrowserGym. Inngest server SSPL/delayed publication is distinguished from SDK terms; RE-Bench informal anti-contamination requests are preserved. Unknown license projects stay in the pool.

Dedup used the complete owning ledger, candidate rows, canonical identities and aliases. LongMINT/MINTEval share one arXiv ID. MemoryAgentBench and MemoryArena have overlapping authors and reused datasets; related paper/repository pairs do not provide independent confirmation. Existing source IDs remain stable.

## New papers

| ID | Primary record | Review depth | Reviewed sections |
|---|---|---|---|
| C-015 | [Why Do Multi-Agent LLM Systems Fail?](https://arxiv.org/abs/2503.13657v3) | selected-full-text | Primary v3 abstract and study framing; v2 study methodology and inter-annotator validation inspected separately, not treated as identical revisions. |
| C-016 | [AgentAsk: Multi-Agent Systems Need to Ask](https://aclanthology.org/2026.acl-long.1294/) | selected-full-text | Published PDF introduction, edge-error mechanism and evaluation framing; related preprint limitation on internal-agent errors. |
| C-017 | [MINTEval: Evaluating Memory under Multi-Target Interference in Long-Horizon Agent Systems](https://arxiv.org/abs/2605.18565v2) | selected-full-text | Benchmark construction, revision-domain sampling, generated questions and stratified human validation. |
| C-018 | [Evaluating Memory in LLM Agents via Incremental Multi-Turn Interactions](https://arxiv.org/abs/2507.05257v4) | selected-full-text | Dataset preparation, LongMemEval reconstruction, limitation on agent coverage, and cost-method assumptions. |
| C-019 | [MemoryArena: Benchmarking Agent Memory in Interdependent Multi-Session Agentic Tasks](https://arxiv.org/abs/2602.16313v2) | selected-full-text | Primary abstract and full-text framing of multi-session action versus static recall evaluation. |
| C-020 | [AgentHarm: A Benchmark for Measuring Harmfulness of LLM Agents](https://arxiv.org/abs/2410.09024v3) | selected-full-text | Benchmark overview, synthetic tools, rubrics, model/API caveats and discussion limitations. |
| C-021 | [tau-bench: A Benchmark for Tool-Agent-User Interaction in Real-World Domains](https://arxiv.org/abs/2406.12045v1) | selected-full-text | Primary abstract, final-state evaluation and discussion of simulated-user limitations. |
| C-022 | [Beyond a Million Tokens: Benchmarking and Enhancing Long-Term Memory in LLMs](https://arxiv.org/abs/2510.27246v2) | selected-full-text | Primary identity, hierarchical conversation generation and bounded clarification-generation process. |
| C-023 | [Designing For Complementary Performance: A Conceptual Model Of Human-AI Collaboration In Strategic Intelligence](https://aisel.aisnet.org/ecis2026/genai/genai/13/) | abstract-only | Primary proceedings metadata and abstract; full text inaccessible in this pass. |
| C-024 | [RE-Bench: Evaluating frontier AI R&D capabilities of language model agents against human experts](https://arxiv.org/abs/2411.15114v2) | selected-full-text | Primary version identity, human comparison, time-budget analysis and limitation/cost discussion. |

## New repositories

All below are pinned README screens, not executed tests. Star observations are dated October 12 and are discovery metadata, not quality measures.

| ID | Repository and pinned source | License boundary | Commit date |
|---|---|---|---|
| R-316 | [temporalio/sdk-python](https://github.com/temporalio/sdk-python/blob/93cb530461d90ab1ab9b150cef21ae1b4f33eca9/README.md) | MIT | 2026-10-12T16:31:11Z |
| R-317 | [dbos-inc/dbos-transact-py](https://github.com/dbos-inc/dbos-transact-py/blob/1857ac86352cef8d639cdd59fb74a02637093c31/README.md) | MIT | 2026-10-12T18:25:15Z |
| R-318 | [inngest/inngest](https://github.com/inngest/inngest/blob/beb36b58874c689be6fb907ebdc3d9844330160f/README.md) | SSPL-1.0; delayed Apache-2.0 publication per pinned LICENSE.md | 2026-10-09T23:25:52Z |
| R-319 | [triggerdotdev/trigger.dev](https://github.com/triggerdotdev/trigger.dev/blob/598fdf267005e5385fcdce0c663e6ff4ca07d68b/README.md) | Apache-2.0 | 2026-10-12T17:05:22Z |
| R-320 | [PrefectHQ/prefect](https://github.com/PrefectHQ/prefect/blob/302beb37eb79cd6ba37fcaa9fa002c4429b45702/README.md) | Apache-2.0 | 2026-10-12T16:53:18Z |
| R-321 | [dagster-io/dagster](https://github.com/dagster-io/dagster/blob/c97898c3e4a8a3cc5e32fcc2ca97aea810342ed9/README.md) | Apache-2.0 | 2026-10-12T16:39:39Z |
| R-322 | [ray-project/ray](https://github.com/ray-project/ray/blob/68174559b27a4eba8db6b3c7ef7aaa2678ec20c8/README.rst) | Apache-2.0 | 2026-10-12T18:15:04Z |
| R-323 | [get-convex/workflow](https://github.com/get-convex/workflow/blob/c82303ad87c4796d7918e06a577ad314dd4cee18/README.md) | Apache-2.0 | 2026-10-12T13:38:13Z |
| R-324 | [sierra-research/tau2-bench](https://github.com/sierra-research/tau2-bench/blob/4ce7c0397c1eb65c9bbe59aeacfe1ca44a1cd699/README.md) | MIT | 2026-10-07T04:04:44Z |
| R-325 | [METR/RE-Bench](https://github.com/METR/RE-Bench/blob/93b98062e55f6945d4a7e213a3226dd419896170/README.md) | MIT; informal anti-contamination requests per pinned LICENSE | 2025-01-30T08:20:51Z |
| R-326 | [mohammadtavakoli78/BEAM](https://github.com/mohammadtavakoli78/BEAM/blob/b2da22eac88bb0874c64665f13457eb99835774a/README.md) | MIT | 2026-08-31T02:12:10Z |
| R-327 | [SWE-bench/SWE-bench](https://github.com/SWE-bench/SWE-bench/blob/02e7a74ffd0b707aab73d203fe87bdc7c76afc8e/README.md) | MIT | 2026-09-02T01:50:34Z |
| R-328 | [ServiceNow/BrowserGym](https://github.com/ServiceNow/BrowserGym/blob/e71419aef5759a11cb7896a26c36e5f7e92d82b2/README.md) | Apache-2.0 per pinned LICENSE | 2026-10-05T23:54:34Z |
| R-329 | [microsoft/agent-lightning](https://github.com/microsoft/agent-lightning/blob/69f5a40b36d9bff646b8e7a5532e8b78bd41eaf9/README.md) | MIT | 2026-10-09T07:46:44Z |
| R-330 | [statelyai/xstate](https://github.com/statelyai/xstate/blob/da4c74efa441dd3a4c1d9835c42c3d1f87cdcaba/README.md) | MIT | 2026-10-08T21:23:04Z |
| R-331 | [open-telemetry/opentelemetry-python](https://github.com/open-telemetry/opentelemetry-python/blob/2417c7a516416209470928788fc4c8ba7c6915a5/README.md) | Apache-2.0 | 2026-10-12T18:03:33Z |
| R-332 | [AgentOps-AI/agentops](https://github.com/AgentOps-AI/agentops/blob/f8e907b92dabe47232978023fdcb01e2a7d4b752/README.md) | MIT | 2026-06-25T08:25:03Z |
| R-333 | [pydantic/logfire](https://github.com/pydantic/logfire/blob/199cc4df2dec0944015344fae467dba258fbd3a0/README.md) | MIT | 2026-10-10T16:11:31Z |
| R-334 | [HUST-AI-HYZ/MemoryAgentBench](https://github.com/HUST-AI-HYZ/MemoryAgentBench/blob/538026089d1a8a8eff05121d0db89b388f360eba/README.md) | MIT | 2026-09-25T06:11:33Z |
| R-335 | [harbor-framework/harbor](https://github.com/harbor-framework/harbor/blob/dc933be707feafbb9efcdf092cb8a0e391332617/README.md) | Apache-2.0 | 2026-10-11T04:40:12Z |

## Ranking and retained leads

[All-source appraisal priorities](staletoast-appraisal-priorities.md) includes every paper and repository exactly once, with ties retained and confidence/adoption kept separate. The existing research evidence-order and repository popularity catalogs remain separate views. [Next-round pool](staletoast-next-round-pool.md) retains all unselected repository discovery attempts, unselected paper leads and earlier unresolved source leads.

## Validation and next action

Run current import validation, actual-row promotion/triage checks, portfolio manifest and catalog tests against these totals, then verify priority coverage and source hashes. A rerank changes appraisal order, not scientific confidence or adopted guidance. Appraise C-023 full text and the new candidates' comparator/independence limits before any finding promotion; do not install or run upstream projects from this intake. No push, merge, deployment, outbound contact, provider evaluation API call or persistent sensitive-data collection occurred.

### Verified local results

Current import, promotion, triage and kit-manifest checks pass. The 12 repository-landscape, 5 portfolio-contract and 15 catalog tests pass, as do JavaScript syntax and whitespace checks. Coverage audit confirms 10 unique new paper IDs, 20 unique new repository IDs, all 122 paper and 334 repository priority entries, all 14 unselected repository attempts in the pool, 30 total pool leads, preserved ties and source hashes, and correct rendered observation dates. Two prior cohort assumptions were corrected: README.rst is a valid pinned README path, and research-artifact lifecycle can describe an evaluation-platform category. Historical records and the original import remain unchanged. This is local validation, not remote CI, publication or adoption.
