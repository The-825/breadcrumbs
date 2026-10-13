"""Resolve a public Pages release from main and an observed approved merge.

Python 3 standard library only. Read-only GitHub API calls; no merge or deployment.
"""
from __future__ import annotations

import json
import argparse
import os
import re
from datetime import datetime
from pathlib import Path
from urllib.request import Request, urlopen


def timestamp(value):
    if not isinstance(value, str):
        return None
    try:
        result = datetime.fromisoformat(value.replace('Z', '+00:00'))
        return result if result.tzinfo is not None else None
    except ValueError:
        return None


def select_release(event_name, ref, repository, main_sha, parent=None, merged_pulls=()):
    def verdict(publish, reason):
        return dict(publish=publish, sha=main_sha if publish else '', reason=reason)

    if not re.fullmatch(r'[0-9a-f]{40}', str(main_sha)):
        return verdict(False, 'main revision is invalid')
    if event_name in {'push', 'workflow_dispatch'}:
        return verdict(ref == 'refs/heads/main', 'main release' if ref == 'refs/heads/main' else 'only main can be published')
    if event_name != 'workflow_run' or not isinstance(parent, dict):
        return verdict(False, 'unsupported trigger')
    if (parent.get('name') != 'Auto-merge agent PRs'
            or parent.get('path') != '.github/workflows/automerge.yml'
            or parent.get('head_repository', {}).get('full_name') != repository
            or parent.get('status') != 'completed' or parent.get('conclusion') != 'success'):
        return verdict(False, 'merge-gate run identity or result does not qualify')
    started, completed = timestamp(parent.get('run_started_at')), timestamp(parent.get('updated_at'))
    if started is None or completed is None or started > completed:
        return verdict(False, 'merge-gate run has no valid observation window')
    for pull in merged_pulls:
        merged = timestamp(pull.get('merged_at'))
        base = pull.get('base', {})
        if (pull.get('state') == 'closed' and merged is not None
                and started <= merged <= completed
                and pull.get('merge_commit_sha') == main_sha
                and base.get('ref') == 'main'
                and base.get('repo', {}).get('full_name') == repository):
            return verdict(True, 'current main has a PR merged during the successful gate run')
    return verdict(False, 'no qualifying new main merge; leave the deployment alone')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--verify-sha')
    args = parser.parse_args()
    repository = os.environ['GITHUB_REPOSITORY']
    if not re.fullmatch(r'[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+', repository):
        raise ValueError('invalid repository identity')
    token = os.environ['GH_TOKEN']

    def api(suffix):
        request = Request(f'https://api.github.com/repos/{repository}/{suffix}', headers={
            'Authorization': f'Bearer {token}', 'Accept': 'application/vnd.github+json',
            'X-GitHub-Api-Version': '2022-11-28', 'User-Agent': 'breadcrumbs-pages-release-gate'})
        with urlopen(request, timeout=30) as response:
            return json.load(response)

    event_name = os.environ['GITHUB_EVENT_NAME']
    main_sha = api('branches/main')['commit']['sha']
    if args.verify_sha:
        if args.verify_sha != main_sha:
            raise ValueError('main changed during the build; do not publish the older artifact')
        print('Pages artifact still matches current main')
        return
    parent, pulls = None, []
    if event_name == 'workflow_run':
        event = json.loads(Path(os.environ['GITHUB_EVENT_PATH']).read_text(encoding='utf-8'))
        run_id = event.get('workflow_run', {}).get('id')
        if type(run_id) is not int or run_id <= 0:
            raise ValueError('missing triggering run identity')
        parent = api(f'actions/runs/{run_id}')
        pulls = api(f'commits/{main_sha}/pulls?per_page=100')
    result = select_release(event_name, os.environ['GITHUB_REF'], repository, main_sha, parent, pulls)
    with Path(os.environ['GITHUB_OUTPUT']).open('a', encoding='utf-8') as output:
        output.write(f"publish={str(result['publish']).lower()}\nsha={result['sha']}\n")
    print(json.dumps(result))


if __name__ == '__main__':
    main()
