"""Render the reusable CI-kit workflow with safe and hostile caller values."""

import os
import pathlib
import shutil
import subprocess
import sys
import tempfile
import textwrap
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[3]
WORKFLOW = ROOT / ".github/workflows/sync-ci-kit.yml"


def renderer_script():
    lines = WORKFLOW.read_text(encoding="utf-8").splitlines()
    start = next(i for i, line in enumerate(lines) if "python3 - <<'PY'" in line)
    end = next(i for i in range(start + 1, len(lines)) if lines[i].strip() == "PY")
    return textwrap.dedent("\n".join(lines[start + 1:end]))


class SyncRendererTests(unittest.TestCase):
    def render(self, **overrides):
        with tempfile.TemporaryDirectory() as tmp:
            root = pathlib.Path(tmp)
            source = root / "_cikit-src/ci-kit/workflows"
            source.mkdir(parents=True)
            for name in ("greenlight-all.yml", "greenlight-command.yml"):
                shutil.copyfile(ROOT / "ci-kit/workflows" / name, source / name)
            env = os.environ.copy()
            env.update({
                "APPROVAL_LABEL": "review #1",
                "AGENT_PREFIX": "claude/,codex/",
                "MERGE_GATE_WORKFLOW": "automerge.yml",
                "APPROVED_LOGINS_JSON": '["operator"]',
                "GITHUB_OUTPUT": str(root / "output.txt"),
            })
            env.update(overrides)
            result = subprocess.run(
                [sys.executable, "-c", renderer_script()], cwd=root, env=env,
                capture_output=True, text=True,
            )
            rendered = {
                name: (root / ".github/workflows" / name).read_text(encoding="utf-8")
                for name in ("greenlight-all.yml", "greenlight-command.yml")
                if (root / ".github/workflows" / name).exists()
            }
            return result, rendered

    def test_valid_values_render_without_yaml_injection(self):
        result, rendered = self.render()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(len(rendered), 2)
        for text in rendered.values():
            self.assertIn('APPROVAL_LABEL: "review #1"', text)
            self.assertIn("MERGE_GATE_WORKFLOW: automerge.yml", text)
        self.assertIn("AGENT_PREFIX: claude/,codex/", rendered["greenlight-all.yml"])

    def test_invalid_caller_values_fail_before_rendering(self):
        for value in (
            {"AGENT_PREFIX": "claude/,"},
            {"AGENT_PREFIX": "claude/\nMALICIOUS: true"},
            {"APPROVAL_LABEL": "review\nMALICIOUS: true"},
            {"APPROVAL_LABEL": "$" + "{{ github.token }}"},
            {"MERGE_GATE_WORKFLOW": "automerge.yml\nMALICIOUS: true"},
            {"APPROVED_LOGINS_JSON": '["operator\u0027s"]'},
            {"APPROVED_LOGINS_JSON": '["operator"]\nMALICIOUS: true'},
        ):
            with self.subTest(value=value):
                result, rendered = self.render(**value)
                self.assertNotEqual(result.returncode, 0)
                self.assertFalse(rendered)


if __name__ == "__main__":
    unittest.main()
