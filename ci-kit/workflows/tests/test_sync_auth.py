"""Offline checks for the sync publisher credential and branch boundary."""
import os
import pathlib
import shutil
import subprocess
import textwrap
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[3]
TEXT = (ROOT / ".github/workflows/sync-ci-kit.yml").read_text(encoding="utf-8")

class SyncAuthTests(unittest.TestCase):
    def test_no_builtin_write_token_or_persisted_checkout_credentials(self):
        self.assertNotIn("secrets.GITHUB_TOKEN", TEXT)
        self.assertNotIn("persist-credentials: true", TEXT)
        self.assertIn("GH_TOKEN: ${{ steps.sync-token.outputs.token }}", TEXT)
        self.assertIn("repositories: ${{ github.event.repository.name }}", TEXT)
        self.assertIn("permission-workflows: write", TEXT)
        self.assertNotIn("skip-token-revoke:", TEXT)

    def test_publishing_is_explicit_and_all_effect_steps_are_gated(self):
        inputs = TEXT.split("      publish_pr:", 1)[1].split("      sync_app_client_id:", 1)[0]
        self.assertIn("default: false", inputs)
        for name in ("Validate publishing configuration", "Create repository-scoped App token", "Open or update the sync PR"):
            section = TEXT.split("      - name: " + name, 1)[1].split("      - name:", 1)[0]
            self.assertIn("if: steps.diff.outputs.changed == 'true' && inputs.publish_pr", section)
        self.assertIn('--force-with-lease="refs/heads/$BRANCH:$expected"', TEXT)

    def test_diff_detects_first_adoption_and_unchanged_files(self):
        bash = "C:/Program Files/Git/bin/bash.exe" if os.name == "nt" else shutil.which("bash")
        if not bash:
            self.skipTest("bash unavailable")
        section = TEXT.split("      - name: Diff against tracked files", 1)[1].split("      - name:", 1)[0]
        script = textwrap.dedent(section.split("        run: |", 1)[1])
        with tempfile.TemporaryDirectory() as tmp:
            root = pathlib.Path(tmp)
            subprocess.run(["git", "init", "-q", tmp], check=True)
            folder = root / ".github/workflows"
            folder.mkdir(parents=True)
            (folder / "greenlight-all.yml").write_text("synthetic: true")
            output = root / "output.txt"
            env = dict(os.environ, GITHUB_OUTPUT=output.as_posix())
            subprocess.run([bash, "-c", script], cwd=tmp, env=env, check=True)
            self.assertEqual(output.read_text().strip(), "changed=true")
            subprocess.run(["git", "add", ".github"], cwd=tmp, check=True)
            subprocess.run(["git", "-c", "user.name=Test", "-c", "user.email=test@example.com", "commit", "-qm", "fixture"], cwd=tmp, check=True)
            output.write_text("")
            subprocess.run([bash, "-c", script], cwd=tmp, env=env, check=True)
            self.assertEqual(output.read_text().strip(), "changed=false")

    def test_pr_lookup_excludes_closed_records(self):
        self.assertIn('--state open --json number', TEXT)
        self.assertNotIn('gh pr view', TEXT)
        self.assertIn('--body-file "$body_file"', TEXT)

    def test_configuration_fails_closed_without_exposing_key(self):
        bash = "C:/Program Files/Git/bin/bash.exe" if os.name == "nt" else shutil.which("bash")
        if not bash:
            self.skipTest("bash unavailable")
        section = TEXT.split("      - name: Validate publishing configuration", 1)[1].split("      - name:", 1)[0]
        script = textwrap.dedent(section.split("        run: |", 1)[1])
        for client,key,branch,ok in [("", "synthetic-key", "chore/sync-ci-kit", False), ("test-client", "", "chore/sync-ci-kit", False), ("test-client", "synthetic-key", "main", False), ("test-client", "synthetic-key", "chore/../main", False), ("test-client", "synthetic-key", "chore/sync-ci-kit", True)]:
            with self.subTest(client=bool(client), key=bool(key), branch=branch):
                env = dict(os.environ, APP_CLIENT_ID=client, APP_PRIVATE_KEY=key, SYNC_BRANCH=branch)
                result = subprocess.run([bash, "-c", script], env=env, capture_output=True, text=True)
                self.assertEqual(result.returncode == 0, ok, result.stderr)
                self.assertNotIn("synthetic-key", result.stdout + result.stderr)

if __name__ == "__main__":
    unittest.main()
