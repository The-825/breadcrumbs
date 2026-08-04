#!/usr/bin/env bash
# Run every file-scan CI lint guard over the repo (default paths). Exit
# non-zero if any guard fails. This is the aggregate gate your checks workflow
# calls. The guard registry lives in the GUARDS array below, not scattered
# across workflow YAML.
#
# Guards run from the repo root, one level above this script; adjust REPO_ROOT
# if you place ci-kit elsewhere. They do not short-circuit: an author sees all
# violations at once.
set -u

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$HERE/.." && pwd)"
cd "$REPO_ROOT"

GUARDS=(
  guard_no_inline_style_script.py
  guard_env_var_in_config.py
  guard_no_raw_fetch.py
  guard_no_magic_limit.py
  guard_no_raw_create_view.py
  guard_no_pii_in_fixtures.py
)

# Deliberate exception: guard_authority_citations.py is not a file-scan guard,
# so it is not in the array above. Its default mode reads the PR body from the
# GitHub event payload (GITHUB_EVENT_PATH) and it fails closed when the
# authority ledger file is missing, so registering it here would fail this
# aggregate run in any repo that has not adopted the ledger, this one included.
# Wire it as its own PR-workflow step per docs/authority-ledger.md; its
# self-tests already run with the other guard tests in ci-kit/guards/tests/.

status=0
for g in "${GUARDS[@]}"; do
  echo "== $g =="
  if ! python3 "$HERE/guards/$g"; then
    status=1
  fi
done

if [ "$status" -ne 0 ]; then
  echo "run_guards: one or more guards FAILED"
else
  echo "run_guards: all guards clean"
fi
exit "$status"
