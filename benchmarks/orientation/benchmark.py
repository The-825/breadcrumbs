#!/usr/bin/env python3
"""Build and score the public Breadcrumbs orientation benchmark."""
import argparse
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
DEFAULT_CASES = HERE / "cases.jsonl"


def read_jsonl(path):
    rows = []
    for number, line in enumerate(Path(path).read_text(encoding="utf-8").splitlines(), 1):
        if line.strip():
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError as exc:
                raise ValueError(f"{path}:{number}: {exc}") from exc
    return rows


def estimated_tokens(text):
    return (len(text) + 3) // 4


def prompt_for(case, condition):
    context = case[f"{condition}_context"]
    schema = json.dumps(case["schema"], sort_keys=True)
    return (
        "Use only the supplied synthetic repository context. Return one JSON object "
        f"matching this field schema: {schema}. Do not add fields or prose.\n\n"
        f"TASK\n{case['task']}\n\nCONTEXT\n{context}"
    )


def emit(cases_path, output):
    requests = []
    for case in read_jsonl(cases_path):
        for condition in ("raw", "breadcrumb"):
            prompt = prompt_for(case, condition)
            requests.append({
                "case_id": case["id"],
                "condition": condition,
                "prompt": prompt,
                "estimated_input_tokens": estimated_tokens(prompt),
            })
    payload = "\n".join(json.dumps(row, sort_keys=True) for row in requests) + "\n"
    if output == "-":
        sys.stdout.write(payload)
    else:
        Path(output).write_text(payload, encoding="utf-8")


def evaluate_response(case, row):
    expected = case["expected"]
    answer = row.get("answer")
    valid_json_object = isinstance(answer, dict)
    field_results = {
        key: valid_json_object and answer.get(key) == value
        for key, value in expected.items()
    }
    return {
        "model": row["model"],
        "case_id": row["case_id"],
        "condition": row["condition"],
        "exact_case_pass": valid_json_object and all(field_results.values())
            and set(answer) == set(expected),
        "correct_fields": sum(field_results.values()),
        "total_fields": len(field_results),
        "input_tokens": row.get("usage", {}).get("input_tokens"),
        "output_tokens": row.get("usage", {}).get("output_tokens"),
        "latency_ms": row.get("latency_ms"),
        "error": row.get("error"),
    }


def score(cases_path, responses_path):
    cases = {row["id"]: row for row in read_jsonl(cases_path)}
    responses = read_jsonl(responses_path)
    results = []
    for row in responses:
        case = cases[row["case_id"]]
        results.append(evaluate_response(case, row))
    print(json.dumps({"results": results, "summary": summarize(results)}, indent=2))


def summarize(results):
    groups = {}
    for row in results:
        key = f"{row['model']}::{row['condition']}"
        group = groups.setdefault(key, {
            "model": row["model"], "condition": row["condition"],
            "cases": 0, "exact_case_passes": 0, "correct_fields": 0,
            "total_fields": 0, "input_tokens": 0, "output_tokens": 0,
            "latency_ms": 0, "reported_usage_rows": 0,
        })
        group["cases"] += 1
        group["exact_case_passes"] += int(row["exact_case_pass"])
        group["correct_fields"] += row["correct_fields"]
        group["total_fields"] += row["total_fields"]
        if row["input_tokens"] is not None and row["output_tokens"] is not None:
            group["input_tokens"] += row["input_tokens"]
            group["output_tokens"] += row["output_tokens"]
            group["reported_usage_rows"] += 1
        if row["latency_ms"] is not None:
            group["latency_ms"] += row["latency_ms"]
    return list(groups.values())


def selftest():
    cases = read_jsonl(DEFAULT_CASES)
    assert len(cases) == 4
    requests = [prompt_for(case, condition) for case in cases for condition in ("raw", "breadcrumb")]
    assert len(requests) == 8 and all("synthetic repository context" in item for item in requests)
    assert all(set(case["schema"]) == set(case["expected"]) for case in cases)
    perfect = {"model": "fixture", "case_id": cases[0]["id"], "condition": "breadcrumb",
               "answer": dict(cases[0]["expected"])}
    wrong = {**perfect, "answer": {**cases[0]["expected"], "next_action": "repeat-work"}}
    assert evaluate_response(cases[0], perfect)["exact_case_pass"] is True
    assert evaluate_response(cases[0], wrong)["exact_case_pass"] is False
    print("orientation_benchmark: 4 cases, 8 prompts, schema and scoring checks passed")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cases", default=str(DEFAULT_CASES))
    sub = parser.add_subparsers(dest="command", required=True)
    emit_parser = sub.add_parser("emit")
    emit_parser.add_argument("--output", default="-")
    score_parser = sub.add_parser("score")
    score_parser.add_argument("responses")
    sub.add_parser("selftest")
    args = parser.parse_args()
    if args.command == "emit":
        emit(args.cases, args.output)
    elif args.command == "score":
        score(args.cases, args.responses)
    else:
        selftest()


if __name__ == "__main__":
    main()
