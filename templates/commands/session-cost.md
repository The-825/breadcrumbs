---
description: Print a per-model token and estimated-cost breakdown for a saved session transcript. Depends on a small helper script; a reference implementation is included below.
argument-hint: "[<path-to-transcript-jsonl>]"
allowed-tools: Bash
---

Run `python3 <scripts-dir>/session_cost.py --file <path>` against **$ARGUMENTS**, or against your harness's most recent saved transcript if `$ARGUMENTS` is empty (Claude Code writes session transcripts as JSONL under `~/.claude/projects/<project-slug>/`; if you run a pre-compaction save hook, prefer its output directory).

Behavior:

- If `$ARGUMENTS` is a path, pass it as `--file`.
- Otherwise resolve the newest transcript file from the location above and pass that.
- Print the script's table output verbatim; do not re-format or summarize it.
- Do NOT commit the result anywhere; this is a session-time readout only.

Caveats to surface to the operator once per session (not every run):

- Prices in the helper are hardcoded per-million-token estimates. Verify against your provider's current price sheet before quoting a figure to anyone.
- Transcripts are raw session data and may contain sensitive content. Never paste the output, or the transcript, into a shared channel without reviewing it first.

## Dependency: the helper script

This command depends on `<scripts-dir>/session_cost.py`. Install it once by saving the reference implementation below (stdlib only, no third-party packages), then edit the `PRICES` table to your provider's current rates. The interface contract, if you write your own instead: accept `--file <jsonl path>`, sum token usage per model, print one table row per model plus a total line.

```python
#!/usr/bin/env python3
"""Per-model token and estimated-cost breakdown for a session transcript.

Input: a JSONL transcript where some lines carry {"message": {"model": ...,
"usage": {...}}} (the Claude Code session format). Lines without usage data
are skipped, so partial or mixed files are fine.
"""
import argparse
import json
from collections import defaultdict

# Dollars per million tokens: {model-substring: (input, output, cache_write, cache_read)}.
# PLACEHOLDER rates. Edit to your provider's current price sheet before trusting output.
PRICES = {
    "<fast-model-substring>": (1.00, 5.00, 1.25, 0.10),
    "<default-model-substring>": (3.00, 15.00, 3.75, 0.30),
    "<deep-model-substring>": (15.00, 75.00, 18.75, 1.50),
}


def rate_for(model):
    for key, rates in PRICES.items():
        if key in model:
            return rates
    return None


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--file", required=True, help="path to the session transcript JSONL")
    args = parser.parse_args()

    totals = defaultdict(lambda: [0, 0, 0, 0])
    with open(args.file, encoding="utf-8") as handle:
        for line in handle:
            try:
                entry = json.loads(line)
            except json.JSONDecodeError:
                continue
            message = entry.get("message") or {}
            usage = message.get("usage") or {}
            if not usage:
                continue
            bucket = totals[message.get("model") or "unknown"]
            bucket[0] += usage.get("input_tokens", 0) or 0
            bucket[1] += usage.get("output_tokens", 0) or 0
            bucket[2] += usage.get("cache_creation_input_tokens", 0) or 0
            bucket[3] += usage.get("cache_read_input_tokens", 0) or 0

    header = f"{'model':<42} {'input':>10} {'output':>10} {'cache_w':>10} {'cache_r':>12} {'est_cost':>10}"
    print(header)
    print("-" * len(header))
    grand_total = 0.0
    for model, (inp, out, cache_w, cache_r) in sorted(totals.items()):
        rates = rate_for(model)
        if rates:
            cost = (inp * rates[0] + out * rates[1] + cache_w * rates[2] + cache_r * rates[3]) / 1_000_000
            grand_total += cost
            cost_text = f"${cost:,.2f}"
        else:
            cost_text = "no rate"
        print(f"{model:<42} {inp:>10,} {out:>10,} {cache_w:>10,} {cache_r:>12,} {cost_text:>10}")
    print(f"{'TOTAL':<42} {'':>10} {'':>10} {'':>10} {'':>12} ${grand_total:,.2f}")


if __name__ == "__main__":
    main()
```

If the helper is missing when this command runs, say so and point the operator at this file's install note; do not improvise a different counting method, because inconsistent counting across runs makes the numbers useless for comparison.
