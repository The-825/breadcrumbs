#!/usr/bin/env python3
"""Golden-query regression exam for memory_engine.py.

Assumes the sibling memory_engine.py and a JSON corpus shaped like
memory_engine_golden.json. The corpus is synthetic and public-safe. Each case
names strings that must appear and strings that must not appear in the composed
context. A repeated case must render identically every time.
"""
import argparse
import importlib.util
import json
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
DEFAULT_CORPUS = HERE / "memory_engine_golden.json"


def load_engine():
    spec = importlib.util.spec_from_file_location(
        "memory_engine", HERE / "memory_engine.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.MemoryEngine


def build_case(engine, case):
    for episode in case.get("episodes", []):
        engine.log_episode(
            episode["action"], episode["outcome"], episode.get("tags", [])
        )
    for fact in case.get("facts", []):
        engine.store_fact(
            fact["category"], fact["key"], fact["value"],
            valid_from=fact.get("valid_from"),
            valid_until=fact.get("valid_until"),
            scope=fact.get("scope", "internal"),
        )
        if fact.get("status") == "verified":
            engine.verify_fact(
                fact["category"], fact["key"], fact["evidence"]
            )
        if "recorded_at" in fact or "verified_at" in fact:
            facts = engine._read(engine.facts)
            row = facts[fact["category"]][fact["key"]]
            if "recorded_at" in fact:
                row["recorded_at"] = fact["recorded_at"]
            if "verified_at" in fact:
                row["verified_at"] = fact["verified_at"]
            engine._write(engine.facts, facts)


def run(corpus_path=DEFAULT_CORPUS):
    cases = json.loads(Path(corpus_path).read_text(encoding="utf-8"))
    MemoryEngine = load_engine()
    checks = []
    for case in cases:
        with tempfile.TemporaryDirectory(prefix="memory_exam_") as tmp:
            engine = MemoryEngine(tmp)
            build_case(engine, case)
            repeats = max(1, int(case.get("repeat", 1)))
            outputs = [engine.build_context(
                case.get("query", ""), **case.get("params", {})
            ) for _ in range(repeats)]
            output = outputs[0]
            for expected in case.get("expect", []):
                checks.append((case["id"], "expected", expected,
                               expected in output))
            for forbidden in case.get("forbid", []):
                checks.append((case["id"], "forbidden", forbidden,
                               forbidden not in output))
            if repeats > 1:
                checks.append((case["id"], "deterministic", "identical output",
                               len(set(outputs)) == 1))
    for case_id, kind, needle, passed in checks:
        print(f"  {'PASS' if passed else 'FAIL'} {case_id}: {kind} {needle!r}")
    failed = [check for check in checks if not check[3]]
    print(f"memory_engine_exam: {len(checks) - len(failed)}/{len(checks)} checks passed")
    return 1 if failed else 0


def selftest():
    return run(DEFAULT_CORPUS)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("corpus", nargs="?", default=str(DEFAULT_CORPUS))
    parser.add_argument("--selftest", action="store_true")
    args = parser.parse_args()
    raise SystemExit(selftest() if args.selftest else run(args.corpus))
