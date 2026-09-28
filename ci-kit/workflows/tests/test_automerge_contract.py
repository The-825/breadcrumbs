"""Exercise both merge workflows with mocked GitHub state and a moving head."""

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

async function scenario(ref, draft, labeled, moveHead) {
  let currentHead = 'sha-checked';
  let merged = false;
  let attemptedSha = null;
  const pr = {
    number: 12, draft, state: 'open', head: { ref, sha: currentHead },
    labels: labeled ? [{ name: 'greenlight' }] : [],
  };
  const github = {
    paginate: async () => [{ filename: '.github/workflows/automerge.yml',
      status: 'modified' }],
    rest: {
      pulls: {
        get: async () => ({ data: pr }),
        listFiles: async () => ({}),
        merge: async ({ sha }) => {
          attemptedSha = sha;
          if (sha !== currentHead) throw new Error('head changed');
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
  try {
    await run(github, context, { info: () => {} }, runtimeRequire);
  } catch (e) {
    if (!moveHead || e.message !== 'head changed') throw e;
  }
  return { merged, attemptedSha };
}

(async () => {
  for (const ref of ['claude/example', 'codex/example']) {
    const ready = await scenario(ref, false, true, false);
    if (!ready.merged || ready.attemptedSha !== 'sha-checked')
      throw new Error(ref + ' failed eligible merge');
    const raced = await scenario(ref, false, true, true);
    if (raced.merged || raced.attemptedSha !== 'sha-checked')
      throw new Error(ref + ' merged a changed head');
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
