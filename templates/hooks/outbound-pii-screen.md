# One PII detector, three call sites

> Part of the companion kit for *From Archivist to Architect* (The Architect's Blueprint, Book 1).

The failure mode this pattern prevents: a repo grows a CI lint that catches PII in
tracked files, then later someone notices agents can also leak PII through a Gmail
draft, a cloud-drive upload, or a published artifact, none of which touch git. The
easy fix is a second regex, hand-copied into a new hook. Then a pre-push guard wants
the same check and gets a third copy. Three copies drift the moment one gets tuned
(a widened ID-digit length, a new excluded path) and the other two do not.

The fix is one detector with a `--stdin` mode, wired to all three call sites:

```text
CI lint over the tree      -> guard script, no args, walks the repo
pre-push git guard         -> guard script, no args, run inside a PreToolUse(Bash)
                               hook when the command is a git push
PreToolUse outbound hook   -> guard script, --stdin, fed the tool call's payload
```

Same regexes, same exit-code contract, in one file. Tune the
detector once and every call site inherits the fix in the same commit.

## The shared detector

[`../../ci-kit/guards/guard_no_pii_in_fixtures.py`](../../ci-kit/guards/guard_no_pii_in_fixtures.py)
is the core: an institutional-email regex and an ID-shaped-number regex, both
parameterized at the top of the file. It already had two modes (CI: walk
`DEFAULT_PATHS`; self-test: an explicit path, exclusions skipped so a bad fixture
still bites). This pattern adds the third: `--stdin`, which runs the identical
`check_line()` over stdin instead of the filesystem. No new detection logic; the
outbound and pre-push lanes reuse the exact function the CI lint calls.

```bash
python3 ci-kit/guards/guard_no_pii_in_fixtures.py            # CI mode: walk the tree
python3 ci-kit/guards/guard_no_pii_in_fixtures.py path/to/f  # self-test mode: one file
echo "$payload" | python3 ci-kit/guards/guard_no_pii_in_fixtures.py --stdin  # outbound mode
```

Exit 1 on a violation, 0 clean, in every mode. The guard prints `path:line: message`
so a hook can relay the findings verbatim back to the agent for redaction.

Adapt the detector to what your repo actually needs to catch. The shipped guard
looks for an institutional-email domain and a fixed-digit ID shape because that is
what a fixture leak looks like; an outbound-payload screen for a different kind of
sensitive data (API keys, internal hostnames, customer records) is the same
three-call-site pattern over a different regex set. Build the one detector for what
your repo actually leaks, not a copy of this one's exact patterns.

## Call site 1: CI lint over the tree

Already shipped: [`../../ci-kit/run_guards.sh`](../../ci-kit/run_guards.sh) calls
the guard in CI mode as part of the aggregate gate. Nothing to add here; this is
the baseline the other two lanes extend.

## Call site 2: pre-push git guard

A `PreToolUse(Bash)` hook that inspects the command about to run, and when it is a
`git push`, runs the guard in CI mode (no args, whole tracked tree) before letting
the push through. This closes the gap where PII lands in a commit whose lint
predated the guard, or where a guard update has not yet been re-run locally: the
push itself is the last cheap place to catch it, before the payload becomes a PR
diff other reviewers and other tools now have to un-see.

```bash
# Inside a PreToolUse(Bash) hook, after extracting the git-push invocation
# from tool_input.command (never scan the whole command blob; commit
# messages and unrelated prose in the same call will false-positive):
if printf '%s' "$push_segs" | grep -qE '\bgit[[:space:]]+push\b'; then
  root="$(git rev-parse --show-toplevel 2>/dev/null)"
  guard="$root/ci-kit/guards/guard_no_pii_in_fixtures.py"
  if [ -f "$guard" ] && command -v python3 >/dev/null 2>&1; then
    if ! out="$(cd "$root" && python3 "$guard" 2>&1)"; then
      echo "Blocked: PII-shaped token in the working tree. Redact before pushing:" >&2
      printf '%s\n' "$out" >&2
      exit 2
    fi
  fi
fi
```

Fail open on tooling absence (no python3, no guard file): a broken screen should
not halt every push, and CI still catches what the local guard misses. Extract
only the push invocation from the command string, never the whole blob; prose
elsewhere in a compound command will otherwise false-positive.

## Call site 3: PreToolUse outbound hook

[`outbound-pii-screen.sh`](outbound-pii-screen.sh) is the runnable hook. It reads
the `PreToolUse` payload from stdin, pulls every string value out of `tool_input`
(plus the file contents behind any `file_path` / `files[]` the tool is about to
publish, since some outbound tool shapes pass a path rather than a body), and
pipes the combined text through the guard's `--stdin` mode. A finding exits 2,
which blocks the tool call and returns the findings to the agent for redaction; a
clean payload, or any tooling gap, exits 0.

Register it on the tool names your outbound integrations actually use (Gmail,
Slack, Drive, an artifact-publish tool):

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "mcp__gmail__.*|mcp__drive__.*|Artifact",
        "hooks": [
          { "type": "command", "command": "bash \"$CLAUDE_PROJECT_DIR/.claude/hooks/outbound-pii-screen.sh\"" }
        ]
      }
    ]
  }
}
```

Match your harness's actual matcher syntax and tool names; the pattern is "every
tool that sends content outside the repo," not any specific list.

## Why this is one pattern, not three hooks

All three call sites answer the same question, "does this text contain a
PII-shaped token," at three different moments: before it is committed to the tree
(CI), before it leaves the local machine as a push (pre-push), and before it
leaves the machine any other way (outbound). Moving the check to a moment does not
change what it checks for. Keep the detector as the one file that knows the
patterns, and let each call site be nothing but "get me the text, run the
detector, act on the exit code."
