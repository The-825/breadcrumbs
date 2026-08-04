# Staging-first promotion: a graduated lane for agent PRs

When autonomous agents open a handful of PRs a day, merge policy is a footnote. When they open
dozens, it becomes the operating question: who stands between agent output and production, and
how often? Two defaults present themselves, and both are bad. Gate every PR on the operator and
the operator becomes the bottleneck; agents stall behind approvals, and approving thirty PRs a
day decays into rubber-stamping anyway. Let every green PR flow straight to production and the
operator loses the one thing a human should keep: a deliberate switch in front of production.

The staging-first promotion model splits the difference. Agent PRs merge freely, on green, into
a staging branch. Production receives that work in batches, through a single promotion PR that
only the operator can approve. The operator stops reviewing merges and starts reviewing
releases.

## The model in one picture

```
feature branch --PR--> staging --self-merge on green, no label*--> staging deploy
                                 (*unless the diff touches a       (operator previews here,
                                  protected path, which waits       updated per merge)
                                  for the label on this lane too)

staging --promotion PR--> main --merges only with <approval-label>--> production deploy
```

Branch names in this doc are the documented defaults, `staging` and `main`; substitute your
own. `<approval-label>` is whatever label your merge gate treats as the operator's explicit
approval.

## Why a staging lane

Two properties, one for each side of the operator's attention.

**Agent work is visible immediately.** Every PR that lands on staging deploys the staging
environment right away. There is zero delay between an agent finishing a feature and the
operator seeing it running. Feedback happens at conversation speed ("that button is wrong, fix
it") instead of release speed.

**Production moves deliberately.** Production receives work only when the operator promotes,
so the blast surface of continuous agent merging is the staging environment, never production.
One human decision still sits in front of every production change, but it is one decision per
batch, not one per PR.

## The flow

**1. Feature PRs base on staging and self-merge on green.** This is the graduated lane: agent
branches target `staging`, and the automerge gate (see `ci-kit/workflows/automerge.yml`)
merges them with no label once every required check passes. The bar for entering staging is
machine-checkable: green checks, non-draft, an agent-prefixed branch, and no protected path
touched without the approval label.

That last clause matters and is easy to skip by accident. The staging lane is a second
deployment of the same gate, and the gate is self-modifying: it runs the BASE branch's copy of
the decision script, so a machinery change (the automerge workflow, the decision script, a
labeler workflow) that reaches `staging` with no protected-path check starts judging every
later staging-lane PR, long before a human ever sees the promotion PR. The end-of-day promotion
greenlight is a bulk approval over a whole batch of feature work; it is not the specific,
deliberate look at a merge-machinery diff that `PROTECTED_PATHS` exists to force. Give the
staging lane's copy of the gate the identical `PROTECTED_PATHS` list as main's copy, not a
lighter one. Full failure mode: `ci-kit/workflows/AUTOMERGE_GOTCHAS.md`, gotcha 12.

**2. Promotion is one PR, label-gated, forever.** At end of day, or on demand, open a PR from
`staging` into `main`. This PR merges only with the operator's `<approval-label>`. It never
graduates to label-free, no matter how mature the rest of the machinery gets: it IS the human
in the loop. The shipped automerge template already excludes it by construction, because the
promotion PR's head branch is the staging branch itself, which matches no agent prefix; the
label gate is the same mechanism as the operator-label hardening described in
`ci-kit/workflows/automerge.yml`.

**3. Reactive promotion is one action.** When the operator says "I want that in production
now," the whole ceremony is: someone (a session, a script, a human) opens the promotion PR,
and the operator applies the label. The operator's word is the trigger; the mechanics belong
to whoever heard it. Batching is the default cadence, not a delay the operator has to accept.

**4. After each promotion, staging resets to main.** Covered next, because the reset is where
the sharp edges live.

## The reset, and why it must fail closed

Promotions squash-merge (one commit on main per batch keeps main's history readable). But a
squash-merge means main's new commit does not exist on staging, and staging's individual
feature commits do not exist on main. The content is identical; the histories have diverged.
Left alone, the divergence compounds with every batch until the branches are unrecognizable to
each other.

> **Incident (anonymized).** In the production repo this pattern was extracted from, the
> staging branch went un-reset through weeks of squash-merge traffic. By SHA it ended up
> simultaneously far behind and far ahead of main, even though everything on it had long since
> landed on main by other routes. The guard below could not prove that mechanically (the trees
> no longer matched), so recovery needed the explicit override. Reset after every promotion and
> the guard passes on its own, every time.

So: after each promotion, force-reset staging to main. And there is the problem, because a
force-push discards commits, and a workflow that force-pushes on request is aimed at any
staging-only work that has not been promoted yet.

The reset skeleton (`ci-kit/workflows/staging-reset.yml`) refuses to push unless it can prove
the push loses nothing. It proceeds only when one of three conditions holds:

1. **Staging is an ancestor of main.** Everything on staging is reachable from main. Nothing
   can be lost.
2. **Staging's tree is byte-identical to main's tree.** The histories diverged (the normal
   post-squash-promotion state) but the content is the same. Nothing can be lost.
3. **The operator explicitly set the override input.** The run log prints exactly which
   commits and what content delta will be discarded, and the operator accepted it.

Anything else refuses, and the refusal is the point. Notice what the guard actually verifies:
not "did a PR with the right title merge," but "does staging carry anything main does not." If
the promotion never merged, staging carries the whole batch and the guard refuses. If new
agent work landed on staging after the promotion, the guard refuses. If refs cannot be fetched
or state cannot be verified, the job errors out before the push step runs. Every ambiguous
state resolves to "do not push."

Two more properties worth copying even if you write your own version:

- **The push is lease-pinned.** The force-push uses `--force-with-lease` pinned to the exact
  staging SHA the guard verified, so if a merge lands between the guard passing and the push
  executing, the push fails instead of silently discarding it.
- **Dispatch-only, serialized.** The workflow runs on manual dispatch, never on a schedule and
  never on PR events, one push per run, inside a concurrency group. A reset is an
  operator-initiated act; nothing should trigger it as a side effect.

One platform gotcha rides along: a push made with the default workflow token fires no
push-event workflows (the platform's recursion guard). If a workflow deploys your staging
branch on push, it will not see the reset, and the staging environment will serve stale
content until the next merge. Either have the reset workflow dispatch the deploy explicitly
(the skeleton supports this) or push with a personal access token, whose pushes fire events
natively.

## If staging shares a backing store with production

The deploy side of staging is out of scope here, but one warning travels with the model: if
the staging environment reads the same database, feature-toggle store, or object store as
production, then staging is only read-safe. A write performed "on staging" (a sync job, an
admin action, a toggle default flipped "just for staging") mutates production. Either isolate
the backing store, or treat staging as read-only and preview features per-user instead of
flipping shared defaults.

## The hotfix carve-out

Direct-to-main PRs stay valid for hotfixes, under whatever rules your main lane already has. A
production incident should not queue behind a batch of unrelated staging work, and forcing it
to would teach everyone to bypass the model the first time it hurts. Keep the carve-out narrow
(hotfixes, not "this one is small") and the promotion lane stays the default by being the path
of least resistance, not the only path.

## The smallest starter version

Nothing above requires deploy automation. The minimum viable model is:

1. Create a staging branch from main.
2. Retarget agent feature PRs at it (a one-line change in your agent instructions).
3. Adopt one ritual: a promotion PR from staging into main, merged only on the operator's
   `<approval-label>`, at end of day or on demand.
4. After each promotion, reset staging to main. By hand at first, after confirming staging
   carries nothing unpromoted; adopt `ci-kit/workflows/staging-reset.yml` when you want the
   reset to be a button with the safety check built in, instead of a checklist you have to
   remember.

Even with no staging deploy at all, the batching property is real: main only moves when the
operator says so, and agent merge traffic stops churning production CI. Add a per-merge
staging deploy when you want the visibility property too.

One honesty note from production use: in the repo this was extracted from, the switch was
roughly cost-neutral in CI minutes (per-merge staging deploys cost about what main-lane merge
churn had cost). The reason to adopt the model is control, not compute.
