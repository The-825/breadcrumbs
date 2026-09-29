"""Exercise both merge workflows with mocked GitHub state, a moving head, and greenlight freshness."""

import pathlib
import subprocess
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[3]
WORKFLOWS = (
    ROOT / "ci-kit/workflows/automerge.yml",
    ROOT / ".github/workflows/automerge.yml",
)

HARNESS = r"""
const fs = require('fs');
const lines = fs.readFileSync(process.argv[1], 'utf8').split(/\r?\n/);
const start = lines.findIndex(line => line.trim() === 'script: |');
if (start < 0) throw new Error('No github-script block');
const body = [];
for (const line of lines.slice(start + 1)) {
  if (line.trim() && !line.startsWith('            ')) break;
  body.push(line.slice(12));
}
const run = new Function('github', 'context', 'core', 'require',
  'return (async () => {\n' + body.join('\n') + '\n})()');

const T = (s) => `2026-09-29T10:00:${String(s).padStart(2, '0')}Z`;
const DEFAULT_TIMELINE = { runs: [T(10)], labeledAt: [T(20)], forcePushes: [], filler: 0 };

async function scenario(ref, draft, labeled, moveHead, mergeErrorStatus = null,
                        timeline = DEFAULT_TIMELINE) {
  let currentHead = 'sha-checked';
  let merged = false;
  let attemptedSha = null;
  let warnings = 0;
  const pr = {
    number: 12, draft, state: 'open', head: { ref, sha: currentHead },
    labels: labeled ? [{ name: 'greenlight' }] : [],
  };
  const github = {
    paginate: async (fn, params) => {
      if (fn === 'runs') {
        if (params.head_sha !== 'sha-checked') throw new Error('wrong run SHA');
        return [...timeline.runs.map(created_at => ({ head_sha: 'sha-checked',
          event: 'pull_request', pull_requests: [{ number: 12 }], created_at })),
          // A run for the same SHA from another PR must not anchor the head.
          { head_sha: 'sha-checked', event: 'pull_request',
            pull_requests: [{ number: 99 }], created_at: T(1) },
          // A push-triggered run is not evidence of this PR's head.
          { head_sha: 'sha-checked', event: 'push',
            pull_requests: [{ number: 12 }], created_at: T(2) }];
      }
      if (fn === 'timeline') return [
        ...Array.from({ length: timeline.filler }, () => ({ event: 'commented',
          created_at: T(0) })),
        // committed items carry pusher-controlled dates and no created_at.
        { event: 'committed', committer: { date: '2020-01-01T00:00:00Z' } },
        { event: 'labeled', label: { name: 'not-greenlight-yet' }, created_at: T(59) },
        ...timeline.labeledAt.map(created_at => ({ event: 'labeled',
          label: { name: 'greenlight' }, created_at })),
        ...timeline.forcePushes.map(created_at => ({ event: 'head_ref_force_pushed',
          created_at })),
      ];
      return [{ filename: '.github/workflows/automerge.yml', status: 'modified' }];
    },
    rest: {
      actions: { listWorkflowRunsForRepo: 'runs' },
      issues: { listEventsForTimeline: 'timeline' },
      pulls: {
        get: async () => ({ data: { ...pr,
          head: { ...pr.head, sha: currentHead } } }),
        listFiles: async () => ({}),
        merge: async ({ sha }) => {
          attemptedSha = sha;
          if (mergeErrorStatus) throw Object.assign(
            new Error('merge failed'), { status: mergeErrorStatus });
          if (sha !== currentHead) throw Object.assign(
            new Error('head changed'), { status: 409 });
          merged = true;
        },
      },
      checks: { listForRef: async ({ ref, check_name }) => {
        if (ref !== 'sha-checked') throw new Error('wrong check SHA');
        if (moveHead) currentHead = 'sha-new';
        return { data: { check_runs: [{ id: 1, name: check_name,
          status: 'completed', conclusion: 'success' }] } };
      } },
    },
  };
  const context = { repo: { owner: 'The-825', repo: 'breadcrumbs' },
    eventName: 'pull_request', payload: { pull_request: { number: 12 } } };
  const runtimeRequire = name => {
    if (name === 'child_process') return { execFileSync: () => {
      throw new Error('GATED');
    } };
    if (name === 'fs') return { writeFileSync: () => {} };
    return require(name);
  };
  await run(github, context, { info: () => {},
    warning: () => { warnings += 1; } }, runtimeRequire);
  return { merged, attemptedSha, warnings };
}

(async () => {
  for (const ref of ['claude/example', 'codex/example']) {
    const ready = await scenario(ref, false, true, false);
    if (!ready.merged || ready.attemptedSha !== 'sha-checked')
      throw new Error(ref + ' failed eligible merge');
    const raced = await scenario(ref, false, true, true);
    if (raced.merged || raced.attemptedSha !== 'sha-checked' || raced.warnings !== 1)
      throw new Error(ref + ' failed to skip a changed head');
    for (const status of [405, 409]) {
      try {
        await scenario(ref, false, true, false, status);
        throw new Error('unrelated merge error was swallowed');
      } catch (e) {
        if (e.status !== status) throw e;
      }
    }
    try {
      await scenario(ref, false, true, true, 422);
      throw new Error('moved-head validation error was swallowed');
    } catch (e) {
      if (e.status !== 422) throw e;
    }
  }
  for (const [ref, draft, labeled] of [
    ['other/example', false, true],
    ['codex/example', true, true],
    ['codex/example', false, false],
  ]) {
    const skipped = await scenario(ref, draft, labeled, false);
    if (skipped.merged || skipped.attemptedSha !== null)
      throw new Error(ref + ' bypassed branch, draft, or label gate');
  }
  // Greenlight must postdate the head, judged on server timestamps only.
  const freshness = [
    ['label after the head run', { runs: [T(10)], labeledAt: [T(20)] }, true],
    ['commit dated early, pushed after the label', { runs: [T(30)], labeledAt: [T(20)] }, false],
    ['label tied with the head run', { runs: [T(20)], labeledAt: [T(20)] }, false],
    ['force push after the label', { runs: [T(10)], labeledAt: [T(20)], forcePushes: [T(25)] }, false],
    ['label removed, push, label re-added', { runs: [T(30)], labeledAt: [T(20), T(40)] }, true],
    ['re-added label still before a later force push', { runs: [T(10)], labeledAt: [T(20), T(30)], forcePushes: [T(35)] }, false],
    ['no run for the head SHA', { runs: [], labeledAt: [T(20)] }, false],
    ['unparseable run time', { runs: ['not-a-time'], labeledAt: [T(20)] }, false],
    ['label only as a similar name', { runs: [T(10)], labeledAt: [] }, false],
    ['more than 100 timeline events', { runs: [T(10)], labeledAt: [T(20)], filler: 150 }, true],
  ];
  for (const [name, spec, expected] of freshness) {
    const result = await scenario('claude/example', false, true, false, null,
      { forcePushes: [], filler: 0, ...spec });
    if (result.merged !== expected)
      throw new Error(`freshness: ${name}: expected merged=${expected}`);
  }
})().catch(e => { console.error(e); process.exitCode = 1; });
"""


class AutoMergeContractTests(unittest.TestCase):
    def test_merge_paths_bind_checked_sha(self):
        for workflow in WORKFLOWS:
            with self.subTest(workflow=workflow):
                subprocess.run(
                    ["node", "-e", HARNESS, str(workflow)],
                    cwd=ROOT, check=True, capture_output=True, text=True,
                )


if __name__ == "__main__":
    unittest.main()
