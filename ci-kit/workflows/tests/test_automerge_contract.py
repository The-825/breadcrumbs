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
                        timeline = DEFAULT_TIMELINE, headRepo = 'The-825/breadcrumbs', baseRef = 'main',
                        opts = {}) {
  let currentHead = 'sha-checked';
  let merged = false;
  let attemptedSha = null;
  let warnings = 0;
  let mergeCalls = 0;
  let mergeTried = false;
  let postGets = 0;
  const sleeps = [];
  const pr = {
    number: 12, draft, state: 'open',
    base: { ref: baseRef, repo: { full_name: 'The-825/breadcrumbs' } },
    head: { ref, sha: currentHead, repo: { full_name: headRepo } },
    labels: labeled ? [{ name: opts.label || 'greenlight' }] : [],
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
          label: { name: timeline.eventLabel || opts.label || 'greenlight' }, created_at })),
        ...timeline.forcePushes.map(created_at => ({ event: 'head_ref_force_pushed',
          created_at })),
      ];
      return [{ filename: '.github/workflows/automerge.yml', status: 'modified' }];
    },
    rest: {
      actions: { listWorkflowRunsForRepo: 'runs' },
      issues: { listEventsForTimeline: 'timeline' },
      pulls: {
        get: async () => {
          // After a failed merge, opts.afterMerge scripts each fresh read; the
          // last entry repeats.
          const extra = mergeTried && opts.afterMerge
            ? opts.afterMerge[Math.min(postGets++, opts.afterMerge.length - 1)] : {};
          return { data: { ...pr, head: { ...pr.head, sha: currentHead }, ...extra } };
        },
        listFiles: async () => ({}),
        merge: async ({ sha }) => {
          attemptedSha = sha;
          mergeCalls += 1;
          mergeTried = true;
          if (mergeErrorStatus) throw Object.assign(
            new Error(opts.mergeMessage || 'merge failed'), { status: mergeErrorStatus });
          if (sha !== currentHead) throw Object.assign(
            new Error('head changed'), { status: 409 });
          merged = true;
        },
      },
      checks: { listForRef: async ({ ref, check_name }) => {
        if (ref !== 'sha-checked') throw new Error('wrong check SHA');
        if (moveHead) currentHead = 'sha-new';
        return { data: { check_runs: opts.missingCheck ? [] : [{ id: 1, name: check_name,
          status: opts.checkStatus || 'completed', conclusion: opts.checkConclusion || 'success' }] } };
      } },
    },
  };
  const context = { repo: { owner: 'The-825', repo: 'breadcrumbs' },
    eventName: 'pull_request_target', payload: { pull_request: { number: 12 } } };
  const runtimeRequire = name => {
    if (name === 'child_process') return { execFileSync: () => {
      throw new Error('GATED');
    } };
    if (name === 'fs') return { writeFileSync: () => {} };
    // Injected instant delay: records requested waits, never really waits.
    if (name === 'timers/promises') return { setTimeout: async (ms) => { sleeps.push(ms); } };
    return require(name);
  };
  try {
    await run(github, context, { info: () => {},
      warning: () => { warnings += 1; } }, runtimeRequire);
  } catch (e) {
    // Expose the counters on the rethrown error so failure cases can assert them.
    e.mergeCalls = mergeCalls;
    e.sleeps = sleeps;
    throw e;
  }
  return { merged, attemptedSha, warnings, mergeCalls, sleeps };
}

const SAME = 'sha-checked';
const prState = (sha, extra = {}) => ({
  head: { ref: 'claude/example', sha, repo: { full_name: 'The-825/breadcrumbs' } }, ...extra });
const OPEN = prState(SAME);
const MERGED = prState(SAME, { merged: true, state: 'closed', merge_commit_sha: 'sha-merge' });
const IN_PROGRESS = 'Merge already in progress';

// Resolves to { ok, status, result }; a rethrown merge error keeps its status.
async function outcome(status, message, afterMerge, moveHead = false) {
  try {
    const result = await scenario('claude/example', false, true, moveHead, status,
      DEFAULT_TIMELINE, 'The-825/breadcrumbs', 'main', { mergeMessage: message, afterMerge });
    return { ok: true, result };
  } catch (e) {
    return { ok: false, status: e.status, error: e };
  }
}

async function reconciliation() {
  const expectOk = (name, o, sleeps, warnings = 0) => {
    if (!o.ok) throw new Error(`${name}: expected success, got ${o.error}`);
    if (o.result.mergeCalls !== 1) throw new Error(`${name}: merge was retried`);
    if (o.result.sleeps.length !== sleeps) throw new Error(`${name}: sleeps ${o.result.sleeps.length}`);
    if (o.result.warnings !== warnings) throw new Error(`${name}: warnings ${o.result.warnings}`);
  };
  // A failure must rethrow the original status, never retry the merge, and
  // poll at most the bound (5 reads) with the injected 3000 ms delay.
  const expectFail = (name, o, status, sleeps) => {
    if (o.ok || o.status !== status) throw new Error(`${name}: expected rethrown ${status}`);
    if (o.error.mergeCalls !== 1) throw new Error(`${name}: merge was retried`);
    if (sleeps !== undefined && o.error.sleeps.length !== sleeps)
      throw new Error(`${name}: expected ${sleeps} waits, got ${o.error.sleeps.length}`);
    if (!o.error.sleeps.every(ms => ms === 3000)) throw new Error(`${name}: unexpected delay`);
  };

  // Sibling run already merged the exact checked head: success, no polling.
  expectOk('405 already merged same head', await outcome(405, IN_PROGRESS, [MERGED]), 0);
  expectOk('409 already merged same head', await outcome(409, 'conflict', [MERGED]), 0);
  expectOk('unrelated 405 text but merged same head', await outcome(405, 'not mergeable', [MERGED]), 0);
  // Transient open, then confirmed: read-only polling, still one merge call.
  expectOk('transient open to confirmed',
    await outcome(405, IN_PROGRESS, [OPEN, OPEN, MERGED]), 2);
  // Unresolved: bounded polling then the original 405 stays visible.
  const unresolved = await outcome(405, IN_PROGRESS, [OPEN]);
  expectFail('unresolved', unresolved, 405, 5);
  // Same head merged but no merge commit: not confirmed.
  expectFail('merged without merge_commit_sha',
    await outcome(405, IN_PROGRESS, [prState(SAME, { merged: true, state: 'closed', merge_commit_sha: '' })]), 405, 0);
  expectFail('merged with null merge_commit_sha',
    await outcome(409, 'conflict', [prState(SAME, { merged: true, state: 'closed', merge_commit_sha: null })]), 409, 0);
  // A different-head merge or a closed-unmerged PR is never success.
  const otherMerged = prState('sha-other', { merged: true, state: 'closed', merge_commit_sha: 'sha-merge' });
  const closed = prState(SAME, { merged: false, state: 'closed', merge_commit_sha: null });
  expectFail('405 different-head merge', await outcome(405, IN_PROGRESS, [otherMerged]), 405, 0);
  expectFail('409 different-head merge', await outcome(409, 'conflict', [otherMerged]), 409, 0);
  expectFail('405 closed unmerged', await outcome(405, IN_PROGRESS, [closed]), 405, 0);
  expectFail('409 closed unmerged', await outcome(409, 'conflict', [closed]), 409, 0);
  expectFail('closed unmerged mid-poll', await outcome(405, IN_PROGRESS, [OPEN, closed]), 405, 1);
  expectFail('different head mid-poll', await outcome(405, IN_PROGRESS, [OPEN, prState('sha-other')]), 405, 1);
  // 405 with a different message while open stays a failure and is not polled.
  expectFail('unrelated 405 open', await outcome(405, 'Pull Request is not mergeable', [OPEN]), 405, 0);
  expectFail('405 changed head', await outcome(405, IN_PROGRESS, [prState('sha-other')]), 405, 0);
  // Existing 409 changed-head handling is kept (benign warning, no rethrow).
  expectOk('409 changed head', await outcome(409, 'head changed', undefined, true), 0, 1);
  // 422 and 5xx are never reconciled, even if the PR looks merged.
  expectFail('422 with merged state', await outcome(422, 'invalid', [MERGED]), 422, 0);
  expectFail('500 with merged state', await outcome(500, 'server', [MERGED]), 500, 0);
}

(async () => {
  await reconciliation();
  for (const opts of [
    {label:'ship-it', missingCheck:true},
    {label:'ship-it', checkStatus:'in_progress'},
    {label:'ship-it', checkConclusion:'failure'},
  ]) {
    const result = await scenario('claude/example',false,true,false,null,
      DEFAULT_TIMELINE,'The-825/breadcrumbs','main',opts);
    if (result.merged) throw new Error('ship-it bypassed a missing or failed check');
  }
  const crossLabel = await scenario('claude/example',false,true,false,null,
    {...DEFAULT_TIMELINE,eventLabel:'greenlight'},'The-825/breadcrumbs','main',{label:'ship-it'});
  if (crossLabel.merged) throw new Error('another label refreshed ship-it');
  const draftShip = await scenario('claude/example',true,true,false,null,
    DEFAULT_TIMELINE,'The-825/breadcrumbs','main',{label:'ship-it'});
  if (draftShip.merged) throw new Error('ship-it bypassed draft reconciliation');
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
  for (const [headRepo, baseRef] of [
    ['outside/breadcrumbs', 'main'],
    ['The-825/breadcrumbs', 'staging'],
  ]) {
    const skipped = await scenario('codex/example', false, true, false,
      null, DEFAULT_TIMELINE, headRepo, baseRef);
    if (skipped.merged || skipped.attemptedSha !== null)
      throw new Error('fork or unexpected base bypassed provenance gate');
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
    for (const label of ['ship-it', 'greenlight']) {
      const result = await scenario('claude/example', false, true, false, null,
        { forcePushes: [], filler: 0, ...spec }, 'The-825/breadcrumbs', 'main', {label});
      if (result.merged !== expected)
        throw new Error(`freshness ${label}: ${name}: expected merged=${expected}`);
    }
  }
})().catch(e => { console.error(e); process.exitCode = 1; });
"""


class AutoMergeContractTests(unittest.TestCase):
    def test_privileged_workflow_uses_base_revision(self):
        for workflow in WORKFLOWS:
            with self.subTest(workflow=workflow):
                source = workflow.read_text(encoding="utf-8")
                self.assertIn("  pull_request_target:", source)
                self.assertNotIn("  pull_request:\n", source)
                self.assertIn('context.eventName === "pull_request_target"', source)

    def test_merge_paths_bind_checked_sha(self):
        for workflow in WORKFLOWS:
            with self.subTest(workflow=workflow):
                subprocess.run(
                    ["node", "-e", HARNESS, str(workflow)],
                    cwd=ROOT, check=True, capture_output=True, text=True,
                )


if __name__ == "__main__":
    unittest.main()
