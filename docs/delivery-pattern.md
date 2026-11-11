# Ship it: one delivery pattern

Assumes an existing owned pull request, Git, and the repository's installed CI,
merge and deployment gates. No provider call or new worker is required.

"Ship it" authorizes the named scope through its in-scope corrections, branch
update, checks, merge, deployment and verification. Recover accepted authority
instead of asking for the same approval again. A material scope expansion,
protected-data decision, spending or separate external effect still needs its
own authority. Paused projects remain exceptions. Draft is a state to reconcile,
not proof either that work is ready or that it should be ignored.

1. Inventory every open PR with owner, exact head, intended base and dependencies.
2. Fetch the actual remote target. Preserve dirty/shared work and use one writer.
3. Update the owned branch against that target. Inspect conflicts for behavior,
   not just syntax. Use force-with-lease only for an owner-approved safe rebase;
   never bulk-force-push or delete branches/worktrees to make the queue look clean.
4. Run the applicable checks on the resulting final head and target integration.
   Review changed risks. Fix a demonstrated failure before resubmission.
5. With valid human authority, apply the current head's shipping label and use the
   installed merge gate. Refresh the target before each sibling integration.
6. Bind deployment to the actual merge revision and verify the intended user
   surface. Source-only artifacts retain their stated install/adoption boundary.
7. Record exact head/base, checks, merge, deployment and live acceptance separately,
   or a named genuine blocker. Preserve first-submission failures even after a
   successful repair. An eventual merge is not first-submission quality.

## Human phrase and compatible mechanism

The authorized operator can comment exactly `ship it` on the current PR. The
installed comment workflow checks the verified account allowlist and whole-body
match, applies `ship-it`, then requests normal gate reevaluation. Historical
`greenlight` and `gl` comments and the `greenlight` label remain compatible.
Each accepted label must still postdate the current head's server-observed run
and any force push. A different label's event cannot refresh a stale approval.
Missing or failed exact-head CI, an unexpected target, fork or draft still blocks
the gate. Historical receipts and technical filenames are not rewritten.

During the first installation, the existing gate may require its historical
label to approve the policy change itself. Record that compatibility bootstrap;
it is not a request for a different human phrase or a bypass of freshness.

Serialize Pages publishing without canceling an active release. Keep the
current-main check after the queue wait, before upload and deployment. A stale
artifact must stop rather than overwrite a newer release. After a deployment
failure, inspect its actual external state before one bounded recovery; do not
blindly resubmit or interrupt another active job.
