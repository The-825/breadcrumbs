#!/usr/bin/env python3
"""Run orientation prompts through Hugging Face Inference Providers.

Requires HF_TOKEN with the Inference Providers permission. Calls may consume free
credits or incur charges. The runner refuses live calls without --confirm-billable.
"""
import argparse
import json
import os
import time
import urllib.error
import urllib.request
from pathlib import Path

ENDPOINT = "https://router.huggingface.co/v1/chat/completions"


def read_jsonl(path):
    return [json.loads(line) for line in Path(path).read_text(encoding="utf-8").splitlines() if line.strip()]


def call(token, model, prompt, timeout):
    body = json.dumps({
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0,
        "max_tokens": 160,
        "stream": False,
        "response_format": {"type": "json_object"},
    }).encode("utf-8")
    request = urllib.request.Request(
        ENDPOINT, data=body, method="POST",
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
    )
    started = time.perf_counter()
    with urllib.request.urlopen(request, timeout=timeout) as response:
        payload = json.loads(response.read().decode("utf-8"))
    elapsed = round((time.perf_counter() - started) * 1000)
    content = payload["choices"][0]["message"]["content"]
    usage = payload.get("usage", {})
    return json.loads(content), {
        "input_tokens": usage.get("prompt_tokens"),
        "output_tokens": usage.get("completion_tokens"),
    }, elapsed


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("requests")
    parser.add_argument("--model", action="append", required=True,
                        help="label=model-id, supplied once for light and once for strong")
    parser.add_argument("--output", required=True)
    parser.add_argument("--timeout", type=int, default=90)
    parser.add_argument("--max-calls", type=int, default=16)
    parser.add_argument("--confirm-billable", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    models = [item.split("=", 1) for item in args.model]
    requests = read_jsonl(args.requests)
    planned = len(models) * len(requests)
    if planned > args.max_calls:
        raise SystemExit(f"refusing {planned} calls; --max-calls is {args.max_calls}")
    if args.dry_run:
        print(json.dumps({"models": models, "requests": len(requests), "planned_calls": planned}, indent=2))
        return
    if not args.confirm_billable:
        raise SystemExit("live Hugging Face calls require --confirm-billable")
    token = os.environ.get("HF_TOKEN")
    if not token:
        raise SystemExit("HF_TOKEN is not set")
    rows = []
    for label, model in models:
        for request_row in requests:
            row = {"model": label, "model_id": model, "case_id": request_row["case_id"],
                   "condition": request_row["condition"]}
            try:
                row["answer"], row["usage"], row["latency_ms"] = call(
                    token, model, request_row["prompt"], args.timeout
                )
            except (urllib.error.URLError, ValueError, KeyError, json.JSONDecodeError) as exc:
                row["error"] = f"{type(exc).__name__}: {exc}"
            rows.append(row)
            Path(args.output).write_text(
                "\n".join(json.dumps(item, sort_keys=True) for item in rows) + "\n",
                encoding="utf-8",
            )


if __name__ == "__main__":
    main()
