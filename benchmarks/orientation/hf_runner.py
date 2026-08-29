#!/usr/bin/env python3
"""Run orientation prompts through Hugging Face Inference Providers.

Requires HF_TOKEN with the Inference Providers permission. Calls may consume free
credits or incur charges. The runner refuses live calls without --confirm-billable.
"""
import argparse
import hashlib
import json
import os
import time
import urllib.error
import urllib.request
from pathlib import Path

ENDPOINT = "https://router.huggingface.co/v1/chat/completions"


class TransportParseError(ValueError):
    def __init__(self, message, raw, content_type):
        super().__init__(message)
        self.diagnostics = {
            "content_type": content_type or "unknown",
            "response_bytes": len(raw),
            "response_sha256": hashlib.sha256(raw).hexdigest(),
        }


class ModelAnswerParseError(ValueError):
    def __init__(self, message, content):
        super().__init__(message)
        encoded = content.encode("utf-8", errors="replace")
        stripped = content.strip()
        self.diagnostics = {
            "content_chars": len(content),
            "content_sha256": hashlib.sha256(encoded).hexdigest(),
            "starts_with_code_fence": stripped.startswith("```"),
            "starts_with_json_object": stripped.startswith("{"),
        }


def read_jsonl(path):
    return [json.loads(line) for line in Path(path).read_text(encoding="utf-8").splitlines() if line.strip()]


def request_payload(model, prompt):
    return {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 1.0,
        "top_p": 0.95,
        "max_tokens": 256,
        "stream": False,
        "response_format": {"type": "json_object"},
        "chat_template_kwargs": {"enable_thinking": False},
    }


def parse_transport_payload(raw, content_type=""):
    text = raw.decode("utf-8", errors="replace").strip()
    if not text:
        raise TransportParseError("empty provider response", raw, content_type)
    try:
        return json.loads(text)
    except json.JSONDecodeError as json_error:
        json_error_message = str(json_error)

    data_lines = [
        line[5:].strip()
        for line in text.splitlines()
        if line.startswith("data:") and line[5:].strip() != "[DONE]"
    ]
    if not data_lines:
        raise TransportParseError(
            f"provider response was not JSON: {json_error_message}", raw, content_type
        )

    content_parts = []
    usage = {}
    try:
        for line in data_lines:
            event = json.loads(line)
            usage = event.get("usage") or usage
            choices = event.get("choices") or []
            if choices:
                delta = choices[0].get("delta") or {}
                content_parts.append(delta.get("content") or "")
    except (json.JSONDecodeError, TypeError, AttributeError) as exc:
        raise TransportParseError(f"invalid provider event stream: {exc}", raw, content_type) from exc
    if not content_parts:
        raise TransportParseError("provider event stream contained no message content", raw, content_type)
    return {"choices": [{"message": {"content": "".join(content_parts)}}], "usage": usage}


def parse_model_answer(content):
    if not isinstance(content, str) or not content.strip():
        raise ModelAnswerParseError("model returned empty message content", content or "")
    stripped = content.strip()
    if stripped.startswith("```"):
        lines = stripped.splitlines()
        if lines and lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        stripped = "\n".join(lines).strip()
    try:
        answer = json.loads(stripped)
    except json.JSONDecodeError as direct_error:
        object_start = stripped.find("{")
        if object_start < 0:
            raise ModelAnswerParseError(
                f"model message contained no JSON object: {direct_error}", content
            ) from direct_error
        try:
            answer, _ = json.JSONDecoder().raw_decode(stripped[object_start:])
        except json.JSONDecodeError as embedded_error:
            raise ModelAnswerParseError(
                f"model message JSON could not be decoded: {embedded_error}", content
            ) from embedded_error
    if not isinstance(answer, dict):
        raise ModelAnswerParseError("model answer was not a JSON object", content)
    return answer


def call(token, model, prompt, timeout):
    body = json.dumps(request_payload(model, prompt)).encode("utf-8")
    request = urllib.request.Request(
        ENDPOINT, data=body, method="POST",
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
    )
    started = time.perf_counter()
    with urllib.request.urlopen(request, timeout=timeout) as response:
        raw = response.read()
        payload = parse_transport_payload(raw, response.headers.get("Content-Type", ""))
    elapsed = round((time.perf_counter() - started) * 1000)
    content = payload["choices"][0]["message"]["content"]
    usage = payload.get("usage", {})
    return parse_model_answer(content), {
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
    parser.add_argument("--preflight", action="store_true",
                        help="run exactly the first request against exactly one model and fail fast")
    args = parser.parse_args()
    models = [item.split("=", 1) for item in args.model]
    requests = read_jsonl(args.requests)
    if args.preflight:
        if len(models) != 1:
            raise SystemExit("--preflight requires exactly one --model")
        requests = requests[:1]
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
                if isinstance(exc, TransportParseError):
                    row["diagnostics"] = exc.diagnostics
                elif isinstance(exc, ModelAnswerParseError):
                    row["diagnostics"] = exc.diagnostics
            rows.append(row)
            Path(args.output).write_text(
                "\n".join(json.dumps(item, sort_keys=True) for item in rows) + "\n",
                encoding="utf-8",
            )
            if args.preflight and row.get("error"):
                raise SystemExit(f"preflight failed: {row['error']}")


if __name__ == "__main__":
    main()
