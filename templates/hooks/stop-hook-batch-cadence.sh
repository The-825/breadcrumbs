#!/usr/bin/env bash
# Stop hook: batch-cadence-aware git check.
#
# Contract:
#   Silent (exit 0) when the tree is clean and everything is pushed, and
#   silent while dirty or unpushed work still shows fresh activity inside
#   the batch window. Warns on stderr and exits 2 only when dirty or
#   unpushed work has gone stale past the window. Exit 2 is what feeds
#   the warning back to the agent; exit 0 keeps the turn end quiet.
#
#   The window measures the age of the NEWEST activity: the later of the
#   last local commit's committer time and the newest mtime among the
#   modified/untracked paths from git status. Default 14400 seconds
#   (four hours); override with STOP_HOOK_BATCH_WINDOW_SECS.
#
#   Never window-suppressed: the stop_hook_active recursion guard, the
#   not-a-git-repo bail, the no-remote bail, and the placeholder-identity
#   check on unpushed commits. The identity check ranges only over commits
#   unique to the branch relative to its own remote-tracking ref
#   (origin/<branch>..HEAD); it never runs against the origin/HEAD
#   fallback, so already-published mainline history cannot be flagged.
#
# Dependencies: bash + git. jq parses the hook input when present; a
# targeted grep covers its absence. Pattern doc: batch-cadence.md.

input=$(cat)

# Recursion guard. The harness sets stop_hook_active when this stop was
# itself caused by a stop-hook warning; warning again would loop forever.
if command -v jq >/dev/null 2>&1; then
  active=$(printf '%s' "$input" | jq -r '.stop_hook_active // false' 2>/dev/null)
else
  # No jq: the payload is machine-generated JSON, so a targeted grep is enough.
  active=false
  printf '%s' "$input" | grep -Eq '"stop_hook_active"[[:space:]]*:[[:space:]]*true' && active=true
fi
[ "$active" = "true" ] && exit 0

# Not a git repository: nothing to check.
git rev-parse --git-dir >/dev/null 2>&1 || exit 0

# No remote: every warning below asks for a push, meaningless without one.
[ -n "$(git remote)" ] || exit 0

window="${STOP_HOOK_BATCH_WINDOW_SECS:-14400}"
[[ "$window" =~ ^[0-9]+$ ]] || window=14400

# Gather state.
modified=0
if ! git diff --quiet || ! git diff --cached --quiet; then
  modified=1
fi
untracked=$(git ls-files --others --exclude-standard)

branch=$(git branch --show-current 2>/dev/null)
upstream=""
upstream_is_fallback=0
unpushed=0
if [ -n "$branch" ]; then
  if git rev-parse --verify --quiet "origin/$branch" >/dev/null 2>&1; then
    upstream="origin/$branch"
  elif git rev-parse --verify --quiet "origin/HEAD" >/dev/null 2>&1; then
    upstream="origin/HEAD"
    upstream_is_fallback=1
  fi
  if [ -n "$upstream" ]; then
    unpushed=$(git rev-list --count "$upstream..HEAD" 2>/dev/null) || unpushed=0
    [ -n "$unpushed" ] || unpushed=0
  fi
fi

# Placeholder-identity check, never window-suppressed. An unpushed commit
# authored with an unset or placeholder identity is cheap to fix now and
# painful after the push. Extend the pattern list for your environment.
#
# Ranged strictly over the branch's own remote-tracking ref. With the
# origin/HEAD fallback the range can include already-published history
# (a stale or mispointed default ref makes upstream..HEAD sweep commits
# main already has), and the amend/rebase advice below must never point
# at published commits, so the check skips when only the fallback exists.
if [ -n "$upstream" ] && [ "$upstream_is_fallback" -eq 0 ] && [ "$unpushed" -gt 0 ]; then
  bad_identity=$(git log --format='%h  %an <%ae>  committed by %cn <%ce>' "$upstream..HEAD" 2>/dev/null \
    | grep -Ei '\(none\)|example\.com|your name|<>')
  if [ -n "$bad_identity" ]; then
    {
      echo "Unpushed commit(s) on '$branch' carry a placeholder or unset git identity:"
      echo "$bad_identity"
      echo "Set git config user.name and user.email, rewrite the affected commits with 'git commit --amend --no-edit --reset-author' (tip commit) or 'git rebase --exec \"git commit --amend --no-edit --reset-author\" $upstream' (earlier commits), then push."
    } >&2
    exit 2
  fi
fi

# Clean and fully pushed: silent.
if [ "$modified" -eq 0 ] && [ -z "$untracked" ] && [ "$unpushed" -eq 0 ]; then
  exit 0
fi

# Batch-window test. Newest activity = max(last commit committer time,
# newest mtime among modified/untracked paths). Fresh activity means an
# accumulation window is in progress: stay silent.
now=$(date +%s)
last=$(git log -1 --format=%ct 2>/dev/null)
[[ "$last" =~ ^[0-9]+$ ]] || last=0
while IFS= read -r line; do
  [ -z "$line" ] && continue
  path=${line:3}
  path=${path##* -> }            # rename entries: keep the new path
  [ -e "$path" ] || continue     # deleted or git-quoted paths: commit time covers them
  m=$(stat -c %Y -- "$path" 2>/dev/null || stat -f %m -- "$path" 2>/dev/null) || continue
  [[ "$m" =~ ^[0-9]+$ ]] || continue
  [ "$m" -gt "$last" ] && last=$m
done < <(git status --porcelain 2>/dev/null)

if [ $((now - last)) -lt "$window" ]; then
  exit 0
fi

# Stale past the window: warn, exit 2.
if [ "$modified" -eq 1 ]; then
  echo "Uncommitted changes have sat untouched past the batch window (${window}s). Commit them, then push the branch." >&2
  exit 2
fi
if [ -n "$untracked" ]; then
  echo "Untracked files have sat untouched past the batch window (${window}s). Commit them or ignore them, then push the branch." >&2
  exit 2
fi
if [ "$unpushed" -gt 0 ]; then
  echo "Branch '$branch' has $unpushed unpushed commit(s) and no new activity inside the batch window (${window}s). Push the branch." >&2
  exit 2
fi

exit 0
