# Outcome-evidence experiment

Experimental, synthetic, offline. This checks whether a claim of task success is backed by a separately supplied, typed, synthetic observation. It is not authentication of any real observer, not production enforcement, and not a measure of how well any agent or checkpoint system performs.

Assumes Python 3.9+ and the standard library only. It makes no network calls, runs no model, spawns no subprocess and evaluates no input as code. It reads the shipped `templates/ledger-tools/shared_work_checkpoint.py` and its fixture, so run it from a full checkout of this repository. The audit functions import as a library; the checkpoint comparison is part of the CLI report.

## The question

A checkpoint store can record "completed" with a line of free text. A line of text cannot tell a self-report from an observed result. This experiment asks one narrow thing: given twelve invented records, does a stricter audit keep unsupported completions at `unknown` and authorize a correction only when a supplied synthetic state observation and a permitted code are present?

Sources: the design follows a plan drawn from the paper [arXiv 2610.01491v1](https://arxiv.org/abs/2610.01491v1), as assessed in the pinned [StaleToast review](https://github.com/The-825/staletoast/blob/3d4715691857f8cf8d171377bdf1681236d25e0f/docs/staletoast-system-fit-appraisals-2026-11-03.md) (entry C-125). Nothing is copied from the paper or any code of its authors. The paper's results are about web-agent evaluation and are not evidence about this code.

## Run it

```
python3 benchmarks/outcome-evidence/benchmark.py                  # JSON report on stdout
python3 benchmarks/outcome-evidence/benchmark.py --selftest       # runs the tests
python3 -m unittest discover -s benchmarks/outcome-evidence -p test_benchmark.py
```

Exit codes: `0` fixture expectations met, `1` an expectation was not met, `2` malformed or unreadable input. Nothing is written except short-lived temporary directories for the baseline, which are deleted before the report prints. There is no persistence option. The report holds no timestamps or temporary paths, so two runs on the same checkout are byte-identical. Input hashes are recorded by role (cases, observations, expectations and benchmark) over raw file bytes, so matching filenames cannot overwrite an input hash. A different line-ending checkout produces different hashes. If the baseline source changes after it was loaded, start a fresh process; the cached module is refused. Use a fresh Python process after changing the benchmark itself. Report hashes assume source files stay fixed during execution.

## What ships

| File | Role |
| --- | --- |
| `benchmark.py` | Audit library, baseline harness and CLI. |
| `cases.json` | Twelve cases plus a separate `corrections` list. No expected verdicts. |
| `observations.json` | The observation registry and the observer allowlist. |
| `expected.json` | Expectations, read only after the audit to verify the fixture. |
| `test_benchmark.py` | Fixture table and adversarial tests. |

## Contract

- **Raw verdict is preserved.** Each case carries `raw_verdict` (`passed`, `failed`, `unknown`). The report echoes it unchanged next to a separate `audited_outcome` with a status, a reason code and observation pointers.
- **A case is judged from the registry only.** A requirement names its observation IDs. They resolve only in the separate registry. The case's own `claimed_evidence_kind` is an untrusted label and is never consulted.
- **An observation counts only if** its ID is unique, its observer is on the explicit allowlist, its `case_id`, `run_id` and `requirement_id` match the requirement it supports, its category is `environment_state`, `artifact` or `action_result`, and its value has exactly the type the requirement declares (`bool`, `int`, `string` or `null`).
- **Strict typing.** `1` does not satisfy `true`, `False` does not satisfy `0`, `null` satisfies only a `null` requirement, and a missing `observed_value` key is different from an explicit `null`. A tool call, statement, agent memory or final answer never counts, even when its value matches.
- **Result rules.** All requirements met gives `passed`. A typed value that contradicts a requirement gives `failed`, which outranks `unknown`. Everything else gives `unknown`: no pointer, unresolved pointer, wrong scope, unlisted observer, non-proof category, missing or mistyped value, conflicting observations.
- **Corrections are separate records.** A record carries the raw and corrected verdicts, a code from `format_mismatch` or `strict_string_mismatch`, and support pointers. It is authorized only when the raw verdict was `failed`, the corrected verdict is `passed`, the code is permitted, and every requirement has a support pointer to an observation that actually satisfied it. The case, the raw verdict and the baseline record are never overwritten. A rejected correction reports why.
- **Structural defects stop the run** instead of being skipped: duplicate observation, case, run or requirement IDs, malformed identifiers, unknown enums or fields, repeated JSON keys, and an observation naming an unknown case. Observations that no requirement references are listed in `unreferenced_observation_ids`.
- **Expectations never reach the decision.** `audit_case` and `audit_documents` take no expectation argument. `expected.json` is compared with finished results by `verify_expectations`. The `required_value` in each case is the task condition, not a grader verdict.

## The twelve cases

Four typed observed-state successes (a bool, an int zero, a string and an explicit null). Three statement or agent-memory-only completions. Two raw automated failures whose independently supplied state supports a correction. Two claims of full progress with no state evidence. One case with no evidence at all.

Fixture result: the five unsupported completions and the missing-evidence case stay `unknown`; the two corrections keep their raw `failed` verdict and carry an observation pointer and a code; the four supplied-state cases are assessed against explicit requirements.

## Baseline comparison

For every case the harness imports the shipped `WorkCheckpointStore`, opens a fresh synthetic scope in a temporary directory using that tool's own fixture contracts, authority and plan, and tries to record a `completion` checkpoint with the case's evidence text (empty for the missing case). The report shows `accepted` or `rejected` as recording behavior and prints the SHA-256 of the module and its fixture.

Acceptance is not task success. The store is documented as bounded control evidence, and this comparison does not claim a defect in it. The production checkpoint contract is unmodified and this experiment adds no schema change.

## Limits and non-goals

- Observation trust is a caller-supplied fixture assumption. Nothing here signs, attests or authenticates an observer, and a forged registry would pass.
- The registry stands in for an environment that no code here inspects.
- Twelve invented records demonstrate that rules behave as written. They support no claim about accuracy, efficiency, cost, productivity or generalization.
- No effect size, false-negative rate or benefit is measured or implied.
- Not a replacement for human review, not a gate for release, and no change to the checkpoint tool, schema or ledger.
- The correction codes are an arbitrary small synthetic set. The evidence-category rank is a routing aid and does not prove that an observation is authentic.
- Narrower than a production API on purpose: where input is ambiguous, the code refuses with a reason rather than guessing.
