import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]


def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


checkpoint = load_module(
    "shared_work_checkpoint_test",
    ROOT / "templates" / "ledger-tools" / "shared_work_checkpoint.py",
)
hook = load_module(
    "work_checkpoint_load_test",
    ROOT / "templates" / "hooks" / "work_checkpoint_load.py",
)


class SharedWorkCheckpointConformanceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.fixture = json.loads(
            (
                ROOT
                / "templates"
                / "ledger-tools"
                / "fixtures"
                / "shared-work-checkpoint-v1.json"
            ).read_text(encoding="utf-8")
        )

    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.ledger = Path(self.temporary.name) / "checkpoint.jsonl"
        self.store = checkpoint.WorkCheckpointStore(self.ledger)
        self.scope = checkpoint.WorkScope(**self.fixture["scope"])
        self.contracts = checkpoint.stage_contracts(
            self.fixture["planning_members"], self.fixture["implementation_members"]
        )
        self.opened = self.store.open(
            self.scope,
            operation_id="open",
            source="operator_request",
            provenance=["task:synthetic"],
            evidence=["rules:synthetic"],
            authority=self.fixture["authority"],
            contracts=self.contracts,
            plan=self.fixture["plan"],
            remaining=["verify"],
            next_action="verify",
            occurred_at="2026-01-01T00:00:00+00:00",
        )

    def tearDown(self):
        self.temporary.cleanup()

    def test_schema_is_strict_and_references_resolve(self):
        schema = json.loads(
            (
                ROOT
                / "templates"
                / "ledger-tools"
                / "shared-work-checkpoint-v1.schema.json"
            ).read_text(encoding="utf-8")
        )
        definitions = schema["$defs"]
        references = []

        def visit(value):
            if isinstance(value, dict):
                if "$ref" in value:
                    references.append(value["$ref"])
                for item in value.values():
                    visit(item)
            elif isinstance(value, list):
                for item in value:
                    visit(item)

        visit(schema)
        self.assertTrue(all(ref.removeprefix("#/$defs/") in definitions for ref in references))
        for record in ("checkpoint", "load_receipt", "release"):
            self.assertFalse(definitions[record]["additionalProperties"])
        self.assertFalse(definitions["plan"]["additionalProperties"])

    def test_model_receipts_are_exact_and_cannot_be_inferred(self):
        self.assertEqual("gpt-6-astra", self.contracts["planning"]["members"][2]["evidence"]["observed"]["model"])
        self.assertEqual("gpt-5.6-sol", self.contracts["implementation"]["members"][1]["evidence"]["observed"]["model"])
        unobserved = json.loads(json.dumps(self.fixture["implementation_members"]))
        unobserved[1]["evidence"]["observed"] = {
            "state": "unknown",
            "model": "gpt-5.6-sol",
            "source": None,
        }
        with self.assertRaises(PermissionError):
            checkpoint.stage_policy_contract("implementation", unobserved)

    def test_hook_reports_uninstrumented_and_loads_only_with_receipt(self):
        missing = hook.load_from_payload({"session_id": "session-1"})
        self.assertEqual("uninstrumented", missing["status"])
        self.assertFalse(missing["claimable"])
        loaded = hook.load_from_payload({
            "session_id": "session-1",
            "work_checkpoint": {
                "ledger_path": str(self.ledger),
                "scope": self.fixture["scope"],
                "receipt_id": "receipt-1",
                "max_bytes": 4096,
            },
        })
        self.assertEqual("loaded", loaded["status"])
        receipt = loaded["manifest"]["load_receipt"]
        self.assertTrue(checkpoint.runtime_instrumentation_status(receipt)["claimable"])
        retried = hook.load_from_payload({
            "session_id": "session-1",
            "work_checkpoint": {
                "ledger_path": str(self.ledger),
                "scope": self.fixture["scope"],
                "receipt_id": "receipt-1",
                "max_bytes": 4096,
            },
        })
        self.assertEqual(receipt["event_id"], retried["manifest"]["load_receipt"]["event_id"])

    def test_failure_retry_is_bounded_and_survives_restart(self):
        head = "a" * 40
        for operation, state in (
            ("r1", "committed"),
            ("r2", "pushed"),
            ("r3", "pr_open"),
            ("r4", "checks_pending"),
        ):
            self.store.release(
                self.scope,
                operation_id=operation,
                state=state,
                head=head,
                source="git" if state in {"committed", "pushed"} else "forge",
                evidence=[f"state:{state}"],
                pr_ref="pr:synthetic" if state not in {"committed", "pushed"} else None,
            )
        failed = self.store.release(
            self.scope,
            operation_id="r5",
            state="checks_failing",
            head=head,
            source="forge",
            evidence=["check:failed"],
            pr_ref="pr:synthetic",
            retry_count=0,
            max_retries=2,
        )
        restarted = checkpoint.WorkCheckpointStore(self.ledger)
        pending = restarted.release(
            self.scope,
            operation_id="r6",
            state="checks_pending",
            head=head,
            source="forge",
            evidence=["check:rerun"],
            pr_ref="pr:synthetic",
            retry_count=1,
            max_retries=2,
        )
        self.assertTrue(failed["failure_checkpoint_id"])
        self.assertEqual(1, pending["retry_count"])
        with self.assertRaises(RuntimeError):
            restarted.release(
                self.scope,
                operation_id="r7",
                state="checks_failing",
                head=head,
                source="forge",
                evidence=["check:failed-again"],
                pr_ref="pr:synthetic",
                retry_count=2,
                max_retries=2,
            )

    def test_cross_scope_recovery_link_is_rejected(self):
        failure = self.store.record(
            self.scope,
            operation_id="failure",
            kind="failure",
            source="ci",
            provenance=["check:synthetic"],
            evidence=["check:failed"],
            remaining=["repair"],
            next_action="repair",
            failure=self.fixture["failure"],
        )
        other = checkpoint.WorkScope(
            "synthetic-work-2", "synthetic-project", "example/repository", "worktree-b"
        )
        self.store.open(
            other,
            operation_id="open-other",
            source="operator_request",
            provenance=["task:synthetic-2"],
            authority=self.fixture["authority"],
            contracts=self.contracts,
            plan=self.fixture["plan"],
            remaining=["verify"],
            next_action="verify",
        )
        with self.assertRaises(ValueError):
            self.store.record(
                other,
                operation_id="workaround-other",
                kind="workaround",
                source="worker",
                provenance=["failure:other"],
                evidence=["patch:other"],
                remaining=["retest"],
                next_action="retest",
                linked_failure_id=failure["event_id"],
                retry_count=1,
                workaround=self.fixture["workaround"],
            )

    def test_completion_and_merge_retries_are_idempotent(self):
        completed = self.store.record(
            self.scope,
            operation_id="complete",
            kind="completion",
            source="worker",
            provenance=["test:all"],
            evidence=["test:passed"],
            remaining=[],
            next_action="",
            occurred_at="2026-01-01T00:01:00+00:00",
        )
        retried_completion = self.store.record(
            self.scope,
            operation_id="complete",
            kind="completion",
            source="worker",
            provenance=["test:all"],
            evidence=["test:passed"],
            remaining=[],
            next_action="",
            occurred_at="2026-01-01T00:02:00+00:00",
        )
        self.assertEqual(completed["event_id"], retried_completion["event_id"])

        release_store = checkpoint.WorkCheckpointStore(Path(self.temporary.name) / "release.jsonl")
        release_scope = checkpoint.WorkScope(
            "release-work", "synthetic-project", "example/repository", "worktree-release"
        )
        release_store.open(
            release_scope,
            operation_id="open-release",
            source="operator_request",
            provenance=["task:release"],
            authority=self.fixture["authority"],
            contracts=self.contracts,
            plan=self.fixture["plan"],
            remaining=["release"],
            next_action="release",
        )
        head = "b" * 40
        for operation, state in (
            ("m1", "committed"), ("m2", "pushed"),
            ("m3", "pr_open"), ("m4", "eligible"),
        ):
            release_store.release(
                release_scope,
                operation_id=operation,
                state=state,
                head=head,
                source="git" if state in {"committed", "pushed"} else "forge",
                evidence=[f"state:{state}"],
                pr_ref="pr:retry" if state not in {"committed", "pushed"} else None,
            )
        release_store.release(
            release_scope,
            operation_id="m5",
            state="approved",
            head=head,
            source="forge",
            evidence=["approval:head"],
            pr_ref="pr:retry",
            approval_head=head,
        )
        merged = release_store.release(
            release_scope,
            operation_id="m6",
            state="merged",
            head=head,
            source="forge",
            evidence=["merge:head"],
            pr_ref="pr:retry",
            merged_head=head,
        )
        retried_merge = release_store.release(
            release_scope,
            operation_id="m6",
            state="merged",
            head=head,
            source="forge",
            evidence=["merge:head"],
            pr_ref="pr:retry",
            merged_head=head,
        )
        self.assertEqual(merged["event_id"], retried_merge["event_id"])

if __name__ == "__main__":
    unittest.main()
