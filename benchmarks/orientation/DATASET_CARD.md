# Breadcrumbs orientation benchmark

## Dataset summary

This synthetic dataset compares two presentations of the same repository-continuity
facts: an unstructured event history and a compact Breadcrumbs cue packet. Each case asks
a model to recover a small authoritative state as JSON.

## Intended use

Use it to compare orientation accuracy, provider-reported token use, and latency across
model tiers and context conditions. Keep each measure separate.

## Data

The four cases cover a moving main branch, survival across compaction, a superseded
decision, and audience-scoped context. All names, revisions, jobs, events, and policies
are synthetic.

## Limitations

The dataset is small, templated, English-only, and repository-oriented. It does not
represent production traces, private memory, broad reasoning quality, or final-task
performance. Exact-field scoring rewards instruction following and state recovery, not
general intelligence. Results are valid only for the recorded model, prompt, provider,
and run date.

## Privacy and governance

No UCR, Jarvis, personal, client, or production data is included. Raw model responses
remain local until separately reviewed and approved for publication.

## License

MIT, matching the repository.
