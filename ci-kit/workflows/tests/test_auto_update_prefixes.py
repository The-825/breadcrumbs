"""Run the branch updater's jq expressions against safe and unsafe prefixes."""

import json
import pathlib
import re
import subprocess
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[3]
SOURCE = (ROOT / "ci-kit/workflows/auto-update-branches.yml").read_text(encoding="utf-8")


def expression(start):
    match = re.search(re.escape(start) + r"(?P<body>.*?)'\)", SOURCE, re.DOTALL)
    if not match:
        raise AssertionError(f"missing jq expression after {start}")
    return match.group("body")


VALIDATE = expression('prefixes=$(jq -n -c --arg prefixes "$AGENT_PREFIXES" \'')
FILTER = expression('| jq -r --arg repo "$REPO" --argjson prefixes "$prefixes" \'')


class AutoUpdatePrefixTests(unittest.TestCase):
    def test_empty_namespace_cannot_select_every_pr(self):
        for value in ("", "claude/,", ",codex/", "claude/,,codex/"):
            with self.subTest(value=value):
                result = subprocess.run(
                    ["jq", "-n", "-c", "--arg", "prefixes", value, VALIDATE],
                    capture_output=True, text=True,
                )
                self.assertNotEqual(result.returncode, 0)

    def test_only_same_repo_permitted_namespaces_are_selected(self):
        result = subprocess.run(
            ["jq", "-n", "-c", "--arg", "prefixes", "claude/,codex/", VALIDATE],
            check=True, capture_output=True, text=True,
        )
        candidates = [
            {"number": i, "head": {"ref": ref, "repo": {"full_name": repo}}}
            for i, ref, repo in (
                (1, "claude/one", "The-825/test"),
                (2, "codex/two", "The-825/test"),
                (3, "codexy/three", "The-825/test"),
                (4, "agent/four", "The-825/test"),
                (5, "claude/fork", "other/test"),
            )
        ]
        selected = subprocess.run(
            ["jq", "-r", "--arg", "repo", "The-825/test", "--argjson",
             "prefixes", result.stdout.strip(), FILTER],
            input=json.dumps(candidates), check=True, capture_output=True, text=True,
        )
        self.assertEqual(selected.stdout.splitlines(), ["1", "2"])


if __name__ == "__main__":
    unittest.main()
