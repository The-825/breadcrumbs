# Breadcrumbs orientation benchmark

This public, synthetic benchmark tests one bounded question: can Breadcrumbs cues help
different model tiers reach the same authoritative starting state with less orientation
cost? It does not test whether the models produce equally strong final work.

## What ships

- `cases.jsonl`: four synthetic continuity failures, each presented as an unstructured
  history and as a compact Breadcrumbs cue packet.
- `benchmark.py`: emits matched prompts and scores exact fields without combining unlike
  measures into one rating.
- `hf_runner.py`: an optional Hugging Face Inference Providers runner. It uses only the
  Python standard library, caps calls, checkpoints every result, and refuses live calls
  unless `--confirm-billable` is present.
- `run-plan.json`: the pinned first comparison and its unrun status.
- `DATASET_CARD.md`: the public-safe scope, intended use, and limitations for a later
  Hugging Face dataset publication, which remains separately approval-gated.

No private Jarvis memory, UCR data, production trace, personal record, or repository
secret belongs in this benchmark.

## Measures

Report these separately for every model and condition:

1. Exact case passes and correct fields
2. Input and output tokens reported by the provider
3. Latency
4. Provider errors or invalid JSON

Do not collapse them into one score. A smaller prompt with a wrong answer is not a win,
and a correct answer that costs more may still be appropriate for a harder task.

## Offline preparation

```powershell
python benchmarks/orientation/benchmark.py selftest
python benchmarks/orientation/benchmark.py emit --output requests.jsonl
python benchmarks/orientation/hf_runner.py requests.jsonl `
  --model light=REPLACE_WITH_MODEL_ID `
  --model strong=REPLACE_WITH_MODEL_ID `
  --output responses.jsonl `
  --dry-run
```

The dry run makes no network calls. It should report 16 planned calls: four cases,
two context conditions, and two model tiers.

Before any matrix run, make one provider call with one model and fail fast if the
transport, authentication, or account capacity is not usable:

```powershell
python benchmarks/orientation/hf_runner.py requests.jsonl `
  --model light=REPLACE_WITH_CURRENT_LIGHT_MODEL_ID `
  --output preflight.jsonl `
  --max-calls 1 `
  --preflight `
  --confirm-billable
```

Inspect and score the preflight result before authorizing a larger run. A successful
offline dry run does not establish live response compatibility or available credits.
The Granite 4.2 profile runs with thinking disabled and the model-card sampling defaults
so the output budget measures the requested orientation answer rather than an unobserved
reasoning trace.

## Live Hugging Face run

Live inference requires a Hugging Face account, remaining Inference Providers credits,
and a fine-grained token with permission to call Inference Providers. Set the token in
the local environment as `HF_TOKEN`. Never write it into this repository.

After checking current model availability, licensing, context limits, and pricing, run:

```powershell
python benchmarks/orientation/hf_runner.py requests.jsonl `
  --model light=REPLACE_WITH_CURRENT_LIGHT_MODEL_ID `
  --model strong=REPLACE_WITH_CURRENT_STRONG_MODEL_ID `
  --output responses.jsonl `
  --max-calls 16 `
  --confirm-billable

python benchmarks/orientation/benchmark.py score responses.jsonl > results.json
```

The `--confirm-billable` flag is an execution-time acknowledgement, not standing
authority. Keep raw responses local until their content and publication scope are
reviewed. Publishing a dataset or result card is a separate decision.

## Interpretation boundary

A result supports only the tested model versions, prompts, provider routes, synthetic
cases, and run date. It does not establish general model superiority, production-memory
quality, cross-vendor continuity, or a collaboration benefit. A model, prompt, provider,
or dataset change requires a new run.
