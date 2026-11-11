"""Tests for the synthetic outcome-evidence check.

They probe the integrity and trust boundary from outside: tampered registries,
hostile values, and the real checkpoint store. The twelve-case table below is
written out by hand and is deliberately not read from expected.json.
"""

import contextlib
import copy
import hashlib
import inspect
import io
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import benchmark

HERE = Path(__file__).resolve().parent

MAIN_TABLE = {
    "case-01": ("passed", "all_requirements_matched", "none", "accepted"),
    "case-02": ("passed", "all_requirements_matched", "none", "accepted"),
    "case-03": ("passed", "all_requirements_matched", "none", "accepted"),
    "case-04": ("passed", "all_requirements_matched", "none", "accepted"),
    "case-05": ("unknown", "no_observation_pointer", "none", "accepted"),
    "case-06": ("unknown", "non_proof_category:obs-06", "none", "accepted"),
    "case-07": ("unknown", "non_proof_category:obs-07", "none", "accepted"),
    "case-08": ("passed", "all_requirements_matched", "authorized", "accepted"),
    "case-09": ("passed", "all_requirements_matched", "authorized", "accepted"),
    "case-10": ("unknown", "no_observation_pointer", "none", "accepted"),
    "case-11": ("unknown", "unresolved_observation_pointer:obs-11-missing", "none", "accepted"),
    "case-12": ("unknown", "no_observation_pointer", "none", "rejected"),
}


def load(name):
    return json.loads((HERE / name).read_text(encoding="utf-8"))


def docs():
    return load("cases.json"), load("observations.json")


def audit(cases_doc, obs_doc):
    return {item["case_id"]: item for item in benchmark.audit_documents(cases_doc, obs_doc)}


def obs_by_id(obs_doc, oid):
    return next(row for row in obs_doc["observations"] if row["observation_id"] == oid)


def case_by_id(cases_doc, cid):
    return next(row for row in cases_doc["cases"] if row["case_id"] == cid)


def corr_by_case(cases_doc, cid):
    return next(row for row in cases_doc["corrections"] if row["case_id"] == cid)


class MainFixtureTests(unittest.TestCase):
    def test_twelve_cases_produce_the_exact_hand_written_table(self):
        report = benchmark.run()
        self.assertEqual(len(report["cases"]), 12)
        got = {
            item["case_id"]: (
                item["audited_outcome"]["status"],
                item["audited_outcome"]["reason"],
                item["correction"]["status"],
                item["baseline_checkpoint"]["recording"],
            )
            for item in report["cases"]
        }
        self.assertEqual(got, MAIN_TABLE)
        self.assertEqual(report["fixture_verification"], {"passed": True, "mismatches": []})

    def test_unsupported_completions_and_missing_stay_unknown(self):
        results = audit(*docs())
        for cid in ("case-05", "case-06", "case-07", "case-10", "case-11", "case-12"):
            self.assertEqual(results[cid]["audited_outcome"]["status"], "unknown", cid)
            self.assertEqual(results[cid]["correction"]["status"], "none", cid)

    def test_corrections_retain_raw_failure(self):
        results = audit(*docs())
        for cid, code in (("case-08", "strict_string_mismatch"), ("case-09", "format_mismatch")):
            item = results[cid]
            self.assertEqual(item["raw_verdict"], "failed")
            self.assertEqual(item["correction"]["status"], "authorized")
            self.assertEqual(item["correction"]["raw_verdict"], "failed")
            self.assertEqual(item["correction"]["corrected_verdict"], "passed")
            self.assertEqual(item["correction"]["code"], code)
            self.assertEqual(item["correction"]["support_observation_ids"], [f"obs-{cid[-2:]}"])

    def test_raw_verdict_preserved_and_inputs_unchanged(self):
        cases_doc, obs_doc = docs()
        before = (copy.deepcopy(cases_doc), copy.deepcopy(obs_doc))
        results = audit(cases_doc, obs_doc)
        self.assertEqual((cases_doc, obs_doc), before)
        for case in cases_doc["cases"]:
            self.assertEqual(results[case["case_id"]]["raw_verdict"], case["raw_verdict"])

    def test_fixture_files_are_not_modified_by_a_run(self):
        names = ("cases.json", "observations.json", "expected.json", "benchmark.py")
        before = {n: hashlib.sha256((HERE / n).read_bytes()).hexdigest() for n in names}
        benchmark.run()
        after = {n: hashlib.sha256((HERE / n).read_bytes()).hexdigest() for n in names}
        self.assertEqual(before, after)
        self.assertEqual(list(HERE.glob("*.jsonl")), [])

    def test_untrusted_pasted_category_does_not_change_the_audit(self):
        cases_doc, obs_doc = docs()
        base = audit(cases_doc, obs_doc)
        for cid in ("case-05", "case-10", "case-11"):
            for kind in ("environment_state", "artifact", "none"):
                case_by_id(cases_doc, cid)["claimed_evidence_kind"] = kind
                again = audit(cases_doc, obs_doc)
                self.assertEqual(again[cid]["audited_outcome"], base[cid]["audited_outcome"])
                self.assertEqual(again[cid]["audited_outcome"]["status"], "unknown")

    def test_audit_function_cannot_see_expectations(self):
        for fn in (benchmark.audit_case, benchmark.audit_documents):
            names = set(inspect.signature(fn).parameters)
            self.assertFalse(any("expect" in n for n in names), fn.__name__)
        cases_doc, obs_doc = docs()
        baseline = audit(cases_doc, obs_doc)
        report = benchmark.run()
        self.assertEqual(
            {i["case_id"]: i["audited_outcome"] for i in report["cases"]},
            {k: v["audited_outcome"] for k, v in baseline.items()},
        )

    def test_wrong_expectations_fail_verification_without_changing_audit(self):
        expected = load("expected.json")
        expected["cases"]["case-05"]["audited_status"] = "passed"
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "expected.json"
            path.write_text(json.dumps(expected), encoding="utf-8")
            report = benchmark.run(expected_path=path)
        self.assertFalse(report["fixture_verification"]["passed"])
        self.assertEqual(report["cases"][4]["audited_outcome"]["status"], "unknown")


class ObservationBoundaryTests(unittest.TestCase):
    def setUp(self):
        self.cases_doc, self.obs_doc = docs()

    def status(self, cid="case-01"):
        item = audit(self.cases_doc, self.obs_doc)[cid]
        return item["audited_outcome"]["status"], item["audited_outcome"]["reason"]

    def test_unresolved_pointer(self):
        case_by_id(self.cases_doc, "case-01")["requirements"][0]["observation_ids"] = ["obs-nope"]
        self.assertEqual(self.status(), ("unknown", "unresolved_observation_pointer:obs-nope"))

    def test_one_unresolved_pointer_taints_an_otherwise_good_one(self):
        case_by_id(self.cases_doc, "case-01")["requirements"][0]["observation_ids"] = ["obs-01", "obs-nope"]
        self.assertEqual(self.status()[0], "unknown")

    def test_wrong_case_run_and_requirement(self):
        for field, bad, label in (
            ("case_id", "case-02", "case_id"),
            ("run_id", "run-02", "run_id"),
            ("requirement_id", "req-02", "requirement_id"),
        ):
            with self.subTest(field=field):
                cases_doc, obs_doc = docs()
                obs_by_id(obs_doc, "obs-01")[field] = bad
                item = audit(cases_doc, obs_doc)["case-01"]["audited_outcome"]
                self.assertEqual(item["status"], "unknown")
                self.assertEqual(item["reason"], f"observation_scope_mismatch_{label}:obs-01")

    def test_pointing_at_another_cases_matching_observation_is_not_proof(self):
        # obs-03 satisfies an identical-looking string requirement, but for case-03.
        case_by_id(self.cases_doc, "case-07")["requirements"][0]["observation_ids"] = ["obs-03"]
        self.assertEqual(self.status("case-07"), ("unknown", "observation_scope_mismatch_case_id:obs-03"))

    def test_unknown_observer(self):
        obs_by_id(self.obs_doc, "obs-01")["observer"] = "rogue-observer"
        self.assertEqual(self.status(), ("unknown", "observer_not_allowlisted:obs-01"))

    def test_allowlist_is_the_trust_boundary(self):
        self.obs_doc["observer_allowlist"] = ["synthetic-observer-b"]
        results = audit(self.cases_doc, self.obs_doc)
        self.assertEqual(results["case-01"]["audited_outcome"]["status"], "unknown")  # observer-a
        self.assertEqual(results["case-02"]["audited_outcome"]["status"], "passed")  # observer-b

    def test_malformed_observer_identifier_is_refused_not_ignored(self):
        obs_by_id(self.obs_doc, "obs-01")["observer"] = "bad observer\n"
        with self.assertRaises(benchmark.FixtureError):
            audit(self.cases_doc, self.obs_doc)

    def test_duplicate_observation_ids_refused(self):
        self.obs_doc["observations"].append(copy.deepcopy(self.obs_doc["observations"][0]))
        with self.assertRaisesRegex(benchmark.FixtureError, "duplicate observation_id"):
            audit(self.cases_doc, self.obs_doc)

    def test_duplicate_requirement_ids_refused(self):
        reqs = case_by_id(self.cases_doc, "case-01")["requirements"]
        reqs.append(copy.deepcopy(reqs[0]))
        with self.assertRaisesRegex(benchmark.FixtureError, "duplicate requirement_id"):
            audit(self.cases_doc, self.obs_doc)

    def test_duplicate_case_and_run_ids_refused(self):
        dup = copy.deepcopy(self.cases_doc)
        dup["cases"][1]["case_id"] = "case-01"
        with self.assertRaisesRegex(benchmark.FixtureError, "duplicate case_id"):
            audit(dup, self.obs_doc)
        dup = copy.deepcopy(self.cases_doc)
        dup["cases"][1]["run_id"] = "run-01"
        with self.assertRaisesRegex(benchmark.FixtureError, "duplicate run_id"):
            audit(dup, self.obs_doc)

    def test_conflicting_observations_are_unknown(self):
        second = copy.deepcopy(obs_by_id(self.obs_doc, "obs-01"))
        second.update(observation_id="obs-01b", observed_value=False, observer="synthetic-observer-b")
        self.obs_doc["observations"].append(second)
        case_by_id(self.cases_doc, "case-01")["requirements"][0]["observation_ids"] = ["obs-01", "obs-01b"]
        self.assertEqual(self.status(), ("unknown", "conflicting_observations"))

    def test_agreeing_observations_pass(self):
        second = copy.deepcopy(obs_by_id(self.obs_doc, "obs-01"))
        second.update(observation_id="obs-01b", observer="synthetic-observer-b")
        self.obs_doc["observations"].append(second)
        case_by_id(self.cases_doc, "case-01")["requirements"][0]["observation_ids"] = ["obs-01", "obs-01b"]
        self.assertEqual(self.status()[0], "passed")

    def test_observation_for_unknown_case_refused(self):
        self.obs_doc["observations"][0]["case_id"] = "case-99"
        with self.assertRaisesRegex(benchmark.FixtureError, "unknown case"):
            audit(self.cases_doc, self.obs_doc)

    def test_malformed_state_values_are_unknown(self):
        for bad in ([True], {"v": True}, 1.0, "true", "True"):
            with self.subTest(bad=bad):
                obs_by_id(self.obs_doc, "obs-01")["observed_value"] = bad
                self.assertEqual(self.status(), ("unknown", "observed_value_type_mismatch:obs-01"))

    def test_expected_bool_is_not_satisfied_by_integer_one(self):
        obs_by_id(self.obs_doc, "obs-01")["observed_value"] = 1
        self.assertEqual(self.status(), ("unknown", "observed_value_type_mismatch:obs-01"))

    def test_expected_int_is_not_satisfied_by_bool(self):
        # case-02 requires the int 0; False == 0 in Python and must not count.
        obs_by_id(self.obs_doc, "obs-02")["observed_value"] = False
        self.assertEqual(self.status("case-02"), ("unknown", "observed_value_type_mismatch:obs-02"))
        obs_by_id(self.obs_doc, "obs-02")["observed_value"] = 0
        self.assertEqual(self.status("case-02")[0], "passed")

    def test_missing_value_differs_from_explicit_null(self):
        del obs_by_id(self.obs_doc, "obs-04")["observed_value"]
        self.assertEqual(self.status("case-04"), ("unknown", "observed_value_missing:obs-04"))
        obs_by_id(self.obs_doc, "obs-04")["observed_value"] = None
        self.assertEqual(self.status("case-04")[0], "passed")

    def test_null_does_not_satisfy_a_non_null_requirement(self):
        obs_by_id(self.obs_doc, "obs-01")["observed_value"] = None
        self.assertEqual(self.status(), ("unknown", "observed_value_type_mismatch:obs-01"))
        obs_by_id(self.obs_doc, "obs-04")["observed_value"] = ""
        self.assertEqual(self.status("case-04")[0], "unknown")

    def test_typed_contradiction_fails_and_outranks_unknown(self):
        obs_by_id(self.obs_doc, "obs-01")["observed_value"] = False
        self.assertEqual(self.status(), ("failed", "observed_state_differs_from_required"))
        case = case_by_id(self.cases_doc, "case-01")
        extra = copy.deepcopy(case["requirements"][0])
        extra.update(requirement_id="req-01b", observation_ids=[])
        case["requirements"].append(extra)
        self.assertEqual(self.status()[0], "failed")

    def test_one_unmet_requirement_blocks_a_pass(self):
        case = case_by_id(self.cases_doc, "case-01")
        extra = copy.deepcopy(case["requirements"][0])
        extra.update(requirement_id="req-01b", observation_ids=[])
        case["requirements"].append(extra)
        self.assertEqual(self.status(), ("unknown", "no_observation_pointer"))

    def test_tool_success_alone_is_never_outcome_proof(self):
        obs_by_id(self.obs_doc, "obs-01")["category"] = "tool_call"
        self.assertEqual(self.status(), ("unknown", "non_proof_category:obs-01"))
        for category in ("statement", "agent_memory", "final_answer"):
            obs_by_id(self.obs_doc, "obs-01")["category"] = category
            self.assertEqual(self.status()[0], "unknown", category)

    def test_unlisted_category_refused(self):
        obs_by_id(self.obs_doc, "obs-01")["category"] = "vibes"
        with self.assertRaises(benchmark.FixtureError):
            audit(self.cases_doc, self.obs_doc)

    def test_bad_enums_and_unknown_fields_refused(self):
        for mutate in (
            lambda c, o: c["cases"][0].update(raw_verdict="success"),
            lambda c, o: c["cases"][0]["requirements"][0].update(value_type="float"),
            lambda c, o: c["cases"][0]["requirements"][0].update(required_value=1),
            lambda c, o: c["cases"][0].update(extra="x"),
            lambda c, o: o["observations"][0].update(extra="x"),
            lambda c, o: c["cases"][0].update(claimed_progress_percent=True),
            lambda c, o: c.update(schema="other"),
        ):
            cases_doc, obs_doc = docs()
            mutate(cases_doc, obs_doc)
            with self.assertRaises(benchmark.FixtureError):
                audit(cases_doc, obs_doc)


class CorrectionTests(unittest.TestCase):
    def setUp(self):
        self.cases_doc, self.obs_doc = docs()

    def correction(self, cid="case-08"):
        return audit(self.cases_doc, self.obs_doc)[cid]["correction"]

    def test_unsupported_code_rejected(self):
        for code in ("looks_right", "", None, ["format_mismatch"]):
            with self.subTest(code=code):
                corr_by_case(self.cases_doc, "case-08")["code"] = code
                result = self.correction()
                self.assertEqual(result["status"], "rejected")
                self.assertEqual(result["reason"], "unsupported_correction_code")

    def test_missing_or_malformed_support_rejected(self):
        for support in ("drop", [], "obs-08", [8], ["obs-08", "obs-08"]):
            with self.subTest(support=support):
                cases_doc, obs_doc = docs()
                record = corr_by_case(cases_doc, "case-08")
                if support == "drop":
                    del record["support_observation_ids"]
                else:
                    record["support_observation_ids"] = support
                result = audit(cases_doc, obs_doc)["case-08"]["correction"]
                self.assertEqual(result["status"], "rejected")
                self.assertEqual(result["reason"], "missing_or_malformed_support_pointer")

    def test_support_must_be_a_satisfying_observation(self):
        corr_by_case(self.cases_doc, "case-08")["support_observation_ids"] = ["obs-09"]
        result = self.correction()
        self.assertEqual(result["status"], "rejected")
        self.assertTrue(result["reason"].startswith("support_pointer_not_a_satisfying_observation"))

    def test_extra_irrelevant_support_pointer_rejected(self):
        corr_by_case(self.cases_doc, "case-08")["support_observation_ids"] = ["obs-08", "obs-01"]
        self.assertEqual(self.correction()["status"], "rejected")

    def test_correction_needs_real_observed_support(self):
        for mutate in (
            lambda: obs_by_id(self.obs_doc, "obs-08").update(category="statement"),
            lambda: obs_by_id(self.obs_doc, "obs-08").update(observer="rogue-observer"),
            lambda: obs_by_id(self.obs_doc, "obs-08").update(observed_value="done"),
            lambda: obs_by_id(self.obs_doc, "obs-08").pop("observed_value"),
        ):
            self.setUp()
            mutate()
            result = self.correction()
            self.assertEqual(result["status"], "rejected")
            self.assertTrue(result["reason"].startswith("observed_state_not_supported"))

    def test_correction_cannot_launder_a_raw_pass_or_change_the_raw_value(self):
        record = corr_by_case(self.cases_doc, "case-08")
        record["raw_verdict"] = "passed"
        self.assertEqual(self.correction()["reason"], "raw_verdict_mismatch")
        record["raw_verdict"] = "failed"
        record["run_id"] = "run-09"
        self.assertEqual(self.correction()["reason"], "correction_scope_mismatch_run_id")
        record["run_id"] = "run-08"
        record["corrected_verdict"] = "unknown"
        self.assertEqual(self.correction()["reason"], "only_failed_to_passed_is_supported")
        case_by_id(self.cases_doc, "case-08")["raw_verdict"] = "passed"
        record.update(raw_verdict="passed", corrected_verdict="passed")
        self.assertEqual(self.correction()["reason"], "only_a_raw_failed_verdict_is_correctable")

    def test_authorized_correction_leaves_raw_failure_in_place(self):
        before = copy.deepcopy(self.cases_doc)
        item = audit(self.cases_doc, self.obs_doc)["case-08"]
        self.assertEqual(self.cases_doc, before)
        self.assertEqual(item["raw_verdict"], "failed")
        self.assertEqual(item["correction"]["status"], "authorized")

    def test_correction_record_structure_errors_refused(self):
        for mutate in (
            lambda c: c["corrections"].append(copy.deepcopy(c["corrections"][0])),
            lambda c: c["corrections"][0].update(case_id="case-99"),
            lambda c: c["corrections"][0].update(correction_id="bad id"),
            lambda c: c["corrections"][0].update(unexpected=1),
        ):
            cases_doc, obs_doc = docs()
            mutate(cases_doc)
            with self.assertRaises(benchmark.FixtureError):
                audit(cases_doc, obs_doc)

    def test_a_contradicted_state_never_authorizes_a_correction(self):
        obs_by_id(self.obs_doc, "obs-08")["observed_value"] = "Not done"
        result = self.correction()
        self.assertEqual(result["status"], "rejected")
        self.assertIn("observed_state_differs_from_required", result["reason"])


class BaselineTests(unittest.TestCase):
    def test_baseline_really_calls_the_shipped_store(self):
        module = benchmark.load_checkpoint()
        original = module.WorkCheckpointStore.record
        calls = []

        def spy(self, scope, **kwargs):
            calls.append(kwargs)
            return original(self, scope, **kwargs)

        with mock.patch.object(module.WorkCheckpointStore, "record", spy):
            report = benchmark.run()
        self.assertEqual(len(calls), 12)
        self.assertTrue(all(c["kind"] == "completion" for c in calls))
        empty = [c for c in calls if c["provenance"] == ["case:case-12"]]
        self.assertEqual(empty[0]["evidence"], [])
        self.assertEqual(report["cases"][11]["baseline_checkpoint"]["recording"], "rejected")

    def test_store_refuses_completion_without_evidence_independently(self):
        module = benchmark.load_checkpoint()
        fixture = load_checkpoint_fixture()
        with tempfile.TemporaryDirectory() as tmp:
            store = module.WorkCheckpointStore(Path(tmp) / "w.jsonl")
            scope = module.WorkScope(**fixture["scope"])
            contracts = module.stage_contracts(
                fixture["planning_members"], fixture["implementation_members"]
            )
            store.open(
                scope, operation_id="o", source="s", provenance=["p"],
                authority=fixture["authority"], contracts=contracts, plan=fixture["plan"],
                remaining=["x"], next_action="y", occurred_at="2026-01-01T00:00:00+00:00",
            )
            with self.assertRaises(ValueError):
                store.record(
                    scope, operation_id="c", kind="completion", source="s",
                    provenance=["p"], evidence=[], remaining=[], next_action="",
                )
        self.assertEqual(
            benchmark.run()["cases"][11]["baseline_checkpoint"]["detail"].split(":")[0], "ValueError"
        )

    def test_acceptance_is_reported_apart_from_the_outcome(self):
        by_id = {i["case_id"]: i for i in benchmark.run()["cases"]}
        for cid in ("case-05", "case-06", "case-07", "case-10", "case-11"):
            self.assertEqual(by_id[cid]["baseline_checkpoint"]["recording"], "accepted")
            self.assertEqual(by_id[cid]["audited_outcome"]["status"], "unknown")
        self.assertIn("not an outcome verdict", benchmark.run()["baseline_note"])

    def test_baseline_source_hash_matches_the_shipped_file(self):
        report = benchmark.run()
        shipped = (benchmark.CHECKPOINT_PATH).read_bytes()
        self.assertEqual(report["baseline_source"]["sha256"], hashlib.sha256(shipped).hexdigest())
        self.assertEqual(
            report["baseline_source"]["fixture_sha256"],
            hashlib.sha256(benchmark.CHECKPOINT_FIXTURE_PATH.read_bytes()).hexdigest(),
        )
        counts = report["record_counts"]
        self.assertEqual(
            (counts["cases"], counts["requirements"], counts["observations"], counts["corrections"]),
            (12, 12, 8, 2),
        )
        self.assertEqual(report["unreferenced_observation_ids"], [])

    def test_cached_baseline_refuses_a_different_source(self):
        benchmark.load_checkpoint()
        with tempfile.TemporaryDirectory() as tmp:
            changed = Path(tmp) / "checkpoint.py"
            changed.write_bytes(benchmark.CHECKPOINT_PATH.read_bytes() + b"\n# different source\n")
            with mock.patch.object(benchmark, "CHECKPOINT_PATH", changed):
                with self.assertRaisesRegex(benchmark.FixtureError, "baseline source changed"):
                    benchmark.load_checkpoint()

    def test_report_snapshot_mismatch_refuses_cached_baseline(self):
        benchmark.load_checkpoint()
        with self.assertRaisesRegex(benchmark.FixtureError, "baseline source changed"):
            benchmark.load_checkpoint(expected_sha="0" * 64)

    def test_failed_import_removes_partial_cache_and_restores_bytecode_setting(self):
        before = sys.dont_write_bytecode
        with mock.patch.dict(sys.modules):
            sys.modules.pop(benchmark._CHECKPOINT_MODULE, None)
            with mock.patch("importlib.machinery.SourceFileLoader.exec_module", side_effect=RuntimeError("synthetic import failure")):
                with self.assertRaisesRegex(RuntimeError, "synthetic import failure"):
                    benchmark.load_checkpoint()
            self.assertNotIn(benchmark._CHECKPOINT_MODULE, sys.modules)
            self.assertEqual(sys.dont_write_bytecode, before)

    def test_source_change_during_import_removes_partial_cache(self):
        original = benchmark.CHECKPOINT_PATH.read_bytes()
        before = sys.dont_write_bytecode
        with mock.patch.dict(sys.modules):
            sys.modules.pop(benchmark._CHECKPOINT_MODULE, None)
            with mock.patch.object(benchmark, "_read", side_effect=[original, original + b"\n# changed\n"]):
                with self.assertRaisesRegex(benchmark.FixtureError, "baseline source changed during import"):
                    benchmark.load_checkpoint()
            self.assertNotIn(benchmark._CHECKPOINT_MODULE, sys.modules)
            self.assertEqual(sys.dont_write_bytecode, before)

    def test_input_hashes_retain_roles_when_filenames_collide(self):
        with tempfile.TemporaryDirectory() as tmp:
            paths = []
            originals = (benchmark.CASES_PATH, benchmark.OBSERVATIONS_PATH, benchmark.EXPECTED_PATH)
            for index, original in enumerate(originals):
                folder = Path(tmp) / str(index)
                folder.mkdir()
                target = folder / "input.json"
                target.write_bytes(original.read_bytes())
                paths.append(target)
            report = benchmark.run(*paths)
        for role, original in zip(("cases", "observations", "expected"), originals):
            self.assertEqual(report["inputs"][role]["sha256"], hashlib.sha256(original.read_bytes()).hexdigest())
        self.assertEqual(set(report["inputs"]), {"benchmark", "cases", "observations", "expected"})

    def test_shipped_checkpoint_files_are_not_touched(self):
        paths = (benchmark.CHECKPOINT_PATH, benchmark.CHECKPOINT_FIXTURE_PATH)
        before = [p.read_bytes() for p in paths]
        benchmark.run()
        self.assertEqual(before, [p.read_bytes() for p in paths])


def load_checkpoint_fixture():
    return json.loads(benchmark.CHECKPOINT_FIXTURE_PATH.read_text(encoding="utf-8"))


class DeterminismAndCliTests(unittest.TestCase):
    def test_two_runs_are_identical_and_leak_no_temp_paths(self):
        first, second = benchmark.run(), benchmark.run()
        self.assertEqual(
            json.dumps(first, sort_keys=True), json.dumps(second, sort_keys=True)
        )
        text = json.dumps(first)
        self.assertNotIn(tempfile.gettempdir(), text)
        self.assertNotIn("outcome_evidence_", text)

    def run_cli(self, *args):
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = benchmark.main(list(args))
        return code, out.getvalue(), err.getvalue()

    def test_cli_default_is_json_on_stdout_with_exit_zero(self):
        code, out, err = self.run_cli()
        self.assertEqual(code, 0)
        self.assertEqual(err, "")
        self.assertTrue(json.loads(out)["fixture_verification"]["passed"])
        self.assertEqual(out, self.run_cli()[1])

    def test_cli_exits_nonzero_on_malformed_input(self):
        bad = {
            "not json": b"{",
            "duplicate key": b'{"schema": "a", "schema": "b"}',
            "nan constant": b'{"schema": NaN}',
            "bom": b"\xef\xbb\xbf{}",
        }
        for label, data in bad.items():
            with self.subTest(label), tempfile.TemporaryDirectory() as tmp:
                path = Path(tmp) / "cases.json"
                path.write_bytes(data)
                code, out, err = self.run_cli("--cases", str(path))
                self.assertEqual(code, 2)
                self.assertEqual(out, "")
                self.assertIn("error:", err)

    def test_cli_exits_nonzero_for_missing_file(self):
        self.assertEqual(self.run_cli("--cases", str(HERE / "absent.json"))[0], 2)

    def test_cli_exits_one_when_fixture_expectations_fail(self):
        expected = load("expected.json")
        expected["cases"]["case-12"]["baseline_recording"] = "accepted"
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "expected.json"
            path.write_text(json.dumps(expected), encoding="utf-8")
            code, out, _ = self.run_cli("--expected", str(path))
        self.assertEqual(code, 1)
        mismatches = json.loads(out)["fixture_verification"]["mismatches"]
        self.assertEqual(mismatches, ["case-12: baseline_recording expected accepted got rejected"])

    def test_expectation_set_must_match_case_set(self):
        expected = load("expected.json")
        del expected["cases"]["case-01"]
        expected["cases"]["case-77"] = copy.deepcopy(expected["cases"]["case-02"])
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "expected.json"
            path.write_text(json.dumps(expected), encoding="utf-8")
            report = benchmark.run(expected_path=path)
        self.assertEqual(
            report["fixture_verification"]["mismatches"],
            ["case-01: no expectation", "case-77: expectation has no case"],
        )


if __name__ == "__main__":
    unittest.main()
