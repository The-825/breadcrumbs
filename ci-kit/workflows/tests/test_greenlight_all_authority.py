"""The manual greenlight sweep only runs for its configured operator."""

import json
import os
import pathlib
import re
import shutil
import subprocess
import sys
import tempfile
import textwrap
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[3]
SOURCE = ROOT / "ci-kit/workflows/greenlight-all.yml"
RENDERER = ROOT / ".github/workflows/sync-ci-kit.yml"


def _allowlist_from_job(text):
    match = re.search(
        r"name: Label green agent PRs\s+"
        r"#.*?if: \|\s+"
        r"contains\(fromJSON\('([^']+)'\), github\.actor\) &&\s+"
        r"github\.actor == github\.triggering_actor",
        text,
        flags=re.DOTALL,
    )
    if not match:
        raise AssertionError("manual sweep must gate both original and re-run actors")
    return json.loads(match.group(1))


class GreenlightAllAuthorityTests(unittest.TestCase):
    def test_template_rejects_unapproved_dispatch_and_replay(self):
        allowed = _allowlist_from_job(SOURCE.read_text(encoding="utf-8"))
        self.assertEqual(allowed, ["your-github-login"])
        for actor, triggering_actor, expected in (
            ("your-github-login", "your-github-login", True),
            ("writer", "writer", False),
            ("your-github-login", "writer", False),
        ):
            with self.subTest(actor=actor, triggering_actor=triggering_actor):
                self.assertEqual(
                    actor in allowed and actor == triggering_actor, expected
                )

    def test_renderer_binds_sweep_to_caller_allowlist(self):
        lines = RENDERER.read_text(encoding="utf-8").splitlines()
        start = next(i for i, line in enumerate(lines) if "python3 - <<'PY'" in line)
        end = next(i for i in range(start + 1, len(lines)) if lines[i].strip() == "PY")
        script = textwrap.dedent("\n".join(lines[start + 1:end]))
        with tempfile.TemporaryDirectory() as tmp:
            root = pathlib.Path(tmp)
            source = root / "_cikit-src/ci-kit/workflows"
            source.mkdir(parents=True)
            for name in ("greenlight-all.yml", "greenlight-command.yml"):
                shutil.copyfile(ROOT / "ci-kit/workflows" / name, source / name)
            env = os.environ.copy()
            env.update({
                "APPROVAL_LABEL": "greenlight",
                "AGENT_PREFIX": "codex/",
                "MERGE_GATE_WORKFLOW": "automerge.yml",
                "APPROVED_LOGINS_JSON": '["operator"]',
                "GITHUB_OUTPUT": str(root / "output.txt"),
            })
            result = subprocess.run(
                [sys.executable, "-c", script], cwd=root, env=env,
                capture_output=True, text=True,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            sweep = (root / ".github/workflows/greenlight-all.yml").read_text()
            command = (root / ".github/workflows/greenlight-command.yml").read_text()
            self.assertEqual(_allowlist_from_job(sweep), ["operator"])
            self.assertIn("fromJSON('[\"operator\"]')", command)
            self.assertNotIn("your-github-login", sweep)


if __name__ == "__main__":
    unittest.main()
