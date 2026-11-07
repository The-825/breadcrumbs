# Set up App-authenticated CI template sync

Assumes GitHub Actions and a repository administrator. The reusable workflow ships
an opt-in publishing path. App registration, secrets and hosted acceptance are not
performed by the workflow or proved by local tests.

The built-in GITHUB_TOKEN cannot push the workflow updates required by this job.
The publisher uses a repository-scoped installation token instead. Existing callers
now render in preview mode unless they explicitly enable publishing. Preview reports
a difference but does not open a PR or claim that synchronization is complete.

## Configure one repository first

1. Register a dedicated GitHub App under your organization. Disable webhooks if you
   do not need them. Allow installation only on the intended account.
2. Request repository permissions: Contents read/write, Pull requests read/write,
   and Workflows read/write. Do not request administration or bypass permissions.
3. Install on one selected test repository initially. Do not choose all repositories.
4. Save its client ID as the repository Actions variable `CI_SYNC_APP_CLIENT_ID`.
   Generate a private key and save it directly as the Actions secret
   `CI_SYNC_APP_PRIVATE_KEY`. Never paste it into chat, commits, logs or PRs.
5. Update the caller below, retaining its existing schedule, approved logins, label
   and merge-gate settings. Replace `REVIEWED_COMMIT_SHA` with the accepted full
   Breadcrumbs commit. Pin `source_ref` to that same commit so executable rendering
   code does not float independently of the reviewed workflow.

```yaml
permissions:
  contents: read
jobs:
  sync:
    uses: The-825/breadcrumbs/.github/workflows/sync-ci-kit.yml@REVIEWED_COMMIT_SHA
    with:
      approved_logins: '["YOUR_APPROVER"]'
      source_ref: REVIEWED_COMMIT_SHA
      publish_pr: true
      sync_app_client_id: ${{ vars.CI_SYNC_APP_CLIENT_ID }}
    secrets:
      sync_app_private_key: ${{ secrets.CI_SYNC_APP_PRIVATE_KEY }}
```

Do not use `secrets: inherit`. Map only the one required secret. The job requests
only its caller repository and three write capabilities when minting the token.
Git checkout does not retain credentials. The Git and PR operations use the same
App token, which the token action revokes during cleanup. The App cannot approve
its own change under the existing human approval identity rules.

## Verify before expanding

Run manually on the selected repository. Confirm the rendered diff changes only
`greenlight-all.yml` and `greenlight-command.yml`, the author is the intended App,
required CI runs on the opened PR, and no merge or deployment occurs without the
existing release approval. Run again and confirm the same branch/PR is updated
without duplicates. Also verify missing credentials fail before any push, and
`publish_pr: false` performs no external write. Do not merge a generated PR as
part of this authentication check.

The dedicated `chore/sync-ci-kit` branch belongs to this job. Concurrent runs are
serialized and pushes use an explicit lease; do not put manual work on that branch.
Check every adopting repository's gate independently before a wider rollout.

## Disable or rotate

Set `publish_pr: false` to return to preview-only behavior. Revoke the App key or
installation if access must stop immediately. Rotate the secret through GitHub's
secret form, then verify a fresh run; never print it to diagnose authentication.
App setup and workflow release remain separate approvals.

References: [GitHub App permissions](https://docs.github.com/en/apps/creating-github-apps/registering-a-github-app/choosing-permissions-for-a-github-app)
and [installation token action](https://github.com/actions/create-github-app-token).
