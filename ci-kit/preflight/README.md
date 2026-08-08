# Preflight

Catch the branch collision before you push, not after.

## The problem

GitHub has no stacked pull requests. When several branches are open against the
same base at once, nothing tells you they are going to fight until one of them
merges and the rest go stale. By then the cost is already paid: conflicts
resolved by hand, CI re-runs on every affected branch, and a review queue where
half the diffs no longer apply.

The frustrating part is that all the information needed to prevent it exists
*before* the push. Which files this branch touches is knowable. Which files the
other open branches touch is knowable. Whether this branch is already behind its
base is knowable. Nothing checks any of it at the one moment when fixing it is
nearly free.

This runs at that moment.

## The checks

| Check | Fails when | Why it earns a place |
|---|---|---|
| `behind_base` | The branch is behind its base | It will merge stale and force a re-run later. Cheapest possible fix, right now. |
| `overlap` | Another open branch touches a file this one touches | This is the stacked-PR problem stated plainly. Whichever merges first makes the rest stale. |
| `commit_hygiene` | A commit subject is a placeholder like `wip` or `fix` | A batched branch is only reviewable if each commit says what it did. |
| `base_merges` | Base has been merged in more than twice | The branch keeps going stale, which usually means it should have shipped smaller or sooner. |
| `stale_state` | A `SESSION_STATE*.md` handoff file has gone over a week without a commit | A crashed or abandoned session leaves its handoff narrating a present that ended. The next session boots on it as current, which is worse than no handoff, because no file prompts a fresh look and a stale one gets believed. The check names the rot; a human refreshes or retires the file. Ages come from git history, not mtime, so a fresh clone does not reset them. |

## Usage

```
python3 preflight.py --base main
python3 preflight.py --base main --others others.json
python3 preflight.py --selftest
```

`others.json` describes the other open branches:

```json
[{"name": "feature-b", "files": ["src/a.py", "docs/x.md"]}]
```

Generate it however you list open branches. The script takes plain JSON on
purpose so it stays dependency free and does not care what produced it.

## The design decision worth stealing

**A check that cannot run reports SKIPPED, never PASSED.**

Without `--others`, the overlap check does not quietly succeed. It says it could
not run, and the summary line says so too. This matters more than it looks: a
tool that reports green when it checked nothing is worse than no tool, because
it converts an unknown into a false assurance. The self-tests pin this
explicitly, and so does the behavior when the base branch cannot be compared.

The same principle shows up throughout this kit. A guard that never fails has
not been proven to work, and a green result that was never computed is a lie
with good manners.

## Where to run it

Locally, immediately before pushing. That is the moment the information is
actionable and the fix is a rebase rather than a conflict resolution.

It also works as a CI job, though by then the branch already exists and some of
the cost is spent. Local is better. CI is a backstop for when someone forgets.

## What it deliberately does not do

- It does not rebase or merge for you. It reports; you decide. A tool that
  rewrites history on its own is not one you leave running.
- It does not judge whether the change is good, only whether it is about to
  collide.
- It does not look at PR review state, labels, or approvals. Those belong to the
  merge gate, which is a separate concern in `../workflows/`.
