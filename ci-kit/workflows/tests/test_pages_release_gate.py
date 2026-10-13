import copy
import importlib.util
import unittest
from pathlib import Path

SPEC = importlib.util.spec_from_file_location('pages_release_gate', Path(__file__).resolve().parents[1] / 'pages_release_gate.py')
gate = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(gate)


class PagesReleaseTests(unittest.TestCase):
    def setUp(self):
        self.repo = 'The-825/breadcrumbs'
        self.sha = 'a' * 40
        self.parent = dict(name='Auto-merge agent PRs', path='.github/workflows/automerge.yml',
                           head_repository={'full_name': self.repo}, status='completed', conclusion='success',
                           run_started_at='2026-10-13T10:00:00Z', updated_at='2026-10-13T10:00:20Z')
        self.pull = dict(state='closed', merged_at='2026-10-13T10:00:10Z', merge_commit_sha=self.sha,
                         base={'ref': 'main', 'repo': {'full_name': self.repo}})

    def select(self, parent=None, pulls=None):
        return gate.select_release('workflow_run', 'refs/heads/main', self.repo, self.sha,
                                   self.parent if parent is None else parent,
                                   [self.pull] if pulls is None else pulls)

    def test_successful_observed_main_merge_pins_its_revision(self):
        result = self.select()
        self.assertTrue(result['publish'])
        self.assertEqual(self.sha, result['sha'])

    def test_skipped_gate_cannot_republish_an_older_merge(self):
        old = copy.deepcopy(self.pull)
        old['merged_at'] = '2026-10-13T09:00:00Z'
        self.assertFalse(self.select(pulls=[old])['publish'])
        self.assertFalse(self.select(pulls=[])['publish'])

    def test_failed_or_foreign_parent_and_similar_named_workflow_fail(self):
        for field, value in [('conclusion', 'failure'), ('status', 'in_progress'),
                             ('name', 'CI'), ('path', '.github/workflows/other.yml'),
                             ('head_repository', {'full_name': 'example/fork'})]:
            with self.subTest(field=field):
                parent = copy.deepcopy(self.parent)
                parent[field] = value
                self.assertFalse(self.select(parent=parent)['publish'])

    def test_unmerged_wrong_base_and_changed_main_revision_fail(self):
        for changes in [{'state': 'open'}, {'merged_at': None}, {'merge_commit_sha': 'b' * 40},
                        {'base': {'ref': 'preview', 'repo': {'full_name': self.repo}}},
                        {'base': {'ref': 'main', 'repo': {'full_name': 'example/fork'}}}]:
            with self.subTest(changes=changes):
                pull = dict(self.pull, **changes)
                self.assertFalse(self.select(pulls=[pull])['publish'])

    def test_bad_missing_and_reversed_timestamps_fail(self):
        for value in [None, 'invalid', '2026-10-13T11:00:00', '2026-10-13T11:00:00Z']:
            parent = dict(self.parent, run_started_at=value)
            self.assertFalse(self.select(parent=parent)['publish'])

    def test_manual_and_push_release_only_main(self):
        for event in ['push', 'workflow_dispatch']:
            self.assertTrue(gate.select_release(event, 'refs/heads/main', self.repo, self.sha)['publish'])
            self.assertFalse(gate.select_release(event, 'refs/heads/preview', self.repo, self.sha)['publish'])
        self.assertFalse(gate.select_release('pull_request', 'refs/heads/main', self.repo, self.sha)['publish'])
