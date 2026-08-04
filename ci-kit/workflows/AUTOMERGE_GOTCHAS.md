# Automerge gotchas: twelve failure modes a naive automerge hits

`automerge.yml` squash-merges an agent PR only when every required check is green on the PR
head SHA, fail-closed. It stands in for GitHub's paid auto-merge feature on Free-plan private
repos. The workflow looks simple. It is not. Every gotcha below is a real failure mode that was
hit in production use of this pattern. Gotchas 1 through 6 are encoded in the shipped
`automerge.yml`; gotchas 7 through 12 arrived with the second generation of the same gate (the
operator label, the extracted decision script, the label-free lanes, and the
staging-promotion model, documented in
[docs/staging-promotion.md](../../docs/staging-promotion.md)) and bind any variant that
grows those parts. Read
this before adapting the template, and re-read it before "simplifying" it.

The reusable core is a single `requiredChecksGreen(headSha)` gate driven by an explicit
`REQUIRED_CHECKS` list. Each named check must be completed + success on the head SHA; anything
missing, pending, or failed returns false and skips the merge.

## Gotcha 1: `checks: read` permission is required or the gate 403s

Without `checks: read` in the workflow's `permissions:` block, `checks.listForRef` returns 403
and the gate can never confirm green, so nothing ever merges. The failure is silent from the
PR's point of view: checks are green, the PR just sits there.

> **Incident (anonymized).** In the production repo this pattern was extracted from, the
> missing `checks: read` scope was discovered only after green PRs stopped merging, and it took
> a dedicated fix PR to close it.

## Gotcha 2: draft-to-ready must re-fire the gate

Flipping a draft PR to ready-for-review fires no new check run. A PR whose checks went green
during the draft window never re-evaluates, so it sits unmerged until someone hand-merges it.
Fix: a second trigger, `pull_request: [ready_for_review]`, running the identical gate.

## Gotcha 3: verify required checks on the head SHA, never the workflow_run conclusion

The gate calls `checks.listForRef({ ref: pr.head.sha })` and requires every named check to be
completed + success there. Trusting `workflow_run.conclusion` instead means only the triggering
workflow gates the merge; any required check that lives outside it silently stops being a gate.
Verifying the head SHA makes every required check a real gate on every trigger path.

## Gotcha 4: automerge does not fire on `synchronize`

New commits on the PR branch do not re-trigger this workflow directly. Re-evaluation comes only
via the checks workflow's `workflow_run` completion (and the ready_for_review path). This is
fine, and it is worth understanding why: a push (including a merge of main into the branch)
re-fires the checks workflow, and that workflow's completion re-drives the merge gate. If you
add trigger types, keep the gate identical on every path.

## Gotcha 5: an explicit `permissions:` block zeroes all unlisted scopes

Declaring `permissions:` at all switches the token from default scopes to exactly what you
list. Every scope the script needs must be enumerated: `contents: write` (the squash merge),
`pull-requests: write` (the merge API), `checks: read` (the gate). Forgetting one does not fail
the workflow at parse time; it silently breaks the corresponding API call at run time.

## Gotcha 6: both required checks must be jobs in ONE workflow (the separate-workflow never-merge trap)

The check names in `REQUIRED_CHECKS` ("Static checks", "E2E checks") are job names inside one
workflow ("Required checks") on purpose. If the e2e job lived in its own workflow, the
`workflow_run` trigger keyed on the first workflow would fire when it finished, the head-SHA
gate would (correctly, fail-closed) skip because e2e was still pending, and nothing would ever
re-fire once e2e went green. The PR would sit unmerged forever with all checks passing.
Co-locating the jobs makes one `workflow_run` completion cover both. If you must keep separate
workflows, add a `workflow_run` trigger per checks workflow; the head-SHA gate stays correct
either way, but every checks workflow needs to be able to re-drive the merge.

## Gotcha 7: labels are read from the frozen event payload

If you adopt an operator label (as the gate on rung one of the maturity ladder below, or as
the override on rung two), the workflow reads the PR's labels from
`github.event.pull_request.labels`: the payload frozen at the moment the triggering event
fired. Two consequences. First, a label added after the event fired is invisible to the run
already in flight. Second, and nastier: label-adds performed through the API with the default
workflow token emit no workflow-triggering events at all (the same recursion guard behind the
`GITHUB_TOKEN` merge trap below). So a convenience workflow that applies the label for the
operator, a batch labeler or a comment-command labeler, does not re-fire the gate. The label
sits on the PR and is only evaluated on the PR's next event: a new commit, a
ready-for-review flip, or a human toggling the label in the UI, which fires a real `labeled`
event. Ship the limitation as documentation on the labeler itself, and teach the unstick
move: toggle the label off and on by hand.

## Gotcha 8: without pipefail, a crashed gate reads as "waiting" forever

Once the decision logic is its own script, the gate step's natural shape is a pipeline: run
the script, `tee` the output into the log, `grep` the verdict out of it. The default Actions
run shell is `bash -e {0}`: errexit on, pipefail OFF. So when the script crashes, the
pipeline's exit code is the last command's, the verdict parses empty, empty is not "merge",
and the job ends green having merged nothing. On every event. Forever. The same class hides
in `grep -c`, which exits 1 on zero matches: a counting grep at the end of a pipeline either
crashes a healthy step or, with no pipefail, helps swallow an upstream crash into a silent
never-merge. Fix: `set -o pipefail` at the top of the gate step, and design the script to
exit 0 for every computed verdict, "wait" included, so pipefail only turns real failures red.
A waiting PR must read as green; a broken gate must read as red; the default shell gives you
neither for free.

> **Incident (anonymized).** In the production repo this pattern comes from, the decision
> script crashed on every event for a stretch and every gate run ended green with
> merge=false. Green PRs piled up "waiting" with all checks passing until someone read the
> step log. The crash itself had a trivial cause (gotcha 9); the silence was the real bug.

## Gotcha 9: a base branch that predates the decision script no-ops the gate

Run the BASE branch's copy of the decision script, never the PR's: a PR that edits its own
merge gate must not influence its own gate run (the default `pull_request` checkout is the
merge ref, which contains the PR's version of the script). That posture is correct and has a
startup corner: the gate will eventually evaluate a PR whose base branch does not contain
the script at all. The PR that introduces the gate. A PR into a long-lived branch cut before
the gate landed. A freshly reset integration branch. The base checkout has no script, the
call crashes, and combined with gotcha 8's silence the gate no-ops on every event with no
red anywhere. Guard explicitly: test that the script exists in the base checkout before
calling it, and treat missing as a loud wait or a red step, never as merge.

## Gotcha 10: an unlistable changed-file set must fail closed

Protected paths and content-policy lanes only work if the gate can see what changed, and the
changed-files listing is an API call that can fail. When it does, the only safe answer is
"wait for the operator's label": if you cannot see what changed, you cannot clear it.
Defaulting open ("listing failed, assume nothing protected was touched") turns any API
hiccup into a hole through the one list that must hold. Two smaller edges in the same
listing: paginate it (the un-paginated files field caps out on large PRs, and a protected
file at position two hundred is still protected), and count a rename as touching BOTH paths,
so renaming a file out of a protected directory does not slip it past the gate.

## Gotcha 11: judge only the newest run per check name, or one duplicate event poisons the SHA

A push can fire duplicate workflow events, and duplicate events create separate check
suites. The superseded suite's run finishes `cancelled` and stays attached to the head SHA
forever, right next to the newer suite's `success` of the same check name. A gate that
reads "any completed failing run means fail" then blocks that SHA permanently, and nothing
on the PR looks wrong: the checks tab shows green, the gate keeps saying a check failed,
and only an empty-commit push (a new SHA) unblocks it. The platform's "latest" filter does
not protect you, because it collapses runs within one suite, not across suites. The fix is
to dedup check runs to the newest run per check name before judging them; run ids are
assigned in creation order, so newest is the max id. Keep runs that carry no id at all,
which preserves fail-closed behavior for payloads that lack the field. Both generations
need it: the first-generation inline check loop and the second-generation decision script
in this directory carry the dedup.

## Gotcha 12: a lane deployed separately from main needs the SAME protected-path check, not a lighter one

If you run the staging-first promotion model (`../../docs/staging-promotion.md`),
the staging lane is a second deployment of this gate, not a lighter cousin of it.
A natural shortcut is to skip `PROTECTED_PATHS` on the staging lane's copy, on the
reasoning that every change reaches production only through the label-gated
promotion PR anyway, so the extra check on staging is redundant. That reasoning
misses that the gate is SELF-MODIFYING on every lane it runs on: the workflow
checks out the BASE branch's copy of the decision script (gotcha 9), so once a
machinery change (the workflow file, the decision script, a labeler workflow, the
file that grants CI its token scopes) lands on staging with no protected-path
check, it starts judging every SUBSEQUENT staging-lane PR, long before a human
ever sees the promotion PR. And the promotion greenlight is a bulk approval over a
whole batch of feature work, not the specific, deliberate look at a
merge-machinery diff that `PROTECTED_PATHS` exists to force.

Generalized: a self-modifying gate must enforce its protected-path list on every
lane or branch it governs, not just the lane nearest production. If you support a
staging-to-main promotion lane, the staging lane needs the same protected-path
check as main, sourced from the same base-branch read, not a main-only list with
staging exempted.

> **Incident (anonymized).** In the production repo this pattern was extracted
> from, the staging lane's copy of the gate returned "merge" for any agent branch
> before it ever reached the protected-path check, so an agent PR touching the
> automerge workflow, the decision script, or the CI-permissions file self-merged
> onto staging with no human look. The lane's own docstring already carried the
> rule this violated ("an agent PR that edits its own merge gate must never
> self-merge"); the staging lane just never implemented it. Fixed by routing the
> staging lane through the identical protected-path check as main, with the same
> fail-closed posture on an unlistable file set.

## Design trade-offs from two generations of this workflow

The shipped file is the simplified distillation. An earlier, more elaborate production
variant of the same pattern made three choices worth knowing about before you adopt; what
that variant later grew into is the second-generation gate at the end of this doc.

### The operator-label gate

The earlier variant required an operator-applied label (its convention: a "greenlight" label)
on PRs from the primary agent's branch namespace before they could merge to the production
branch. Checks-green alone was not enough; a human explicitly released each merge, and the gate
failed closed (a PR with no labels never merged). Other, lower-stakes agent namespaces merged
on green checks alone. The file shipped here has that gate on by default: `REQUIRE_LABEL`
and `APPROVAL_LABEL` sit in automerge.yml's EDIT ME block, the label is read from a fresh API
fetch inside the gate (never from the triggering event's frozen payload, so a stale payload
cannot vouch for it), a missing labels array counts as unlabeled (fail closed), and
`pull_request: [labeled]` is wired as a trigger so applying the label to an already-green PR
merges it without waiting for another checks run.

The label gate buys a human in the loop before production at the cost of one manual action
per PR. Setting `REQUIRE_LABEL = false` restores the hands-free flow on green checks alone;
do that deliberately, once trust is earned, not by default.

### The GITHUB_TOKEN recursion-guard trap

A squash-merge performed with the default `GITHUB_TOKEN` does not trigger push-event workflows
on the target branch. That is GitHub's deliberate infinite-loop guard, and it means your
deploy-on-push and smoke-test-on-push workflows DO NOT RUN for auto-merged PRs.

> **Incident (anonymized).** In the earlier production variant, every auto-merged PR reached
> the production branch with no deploy and no smoke run, silently, until the workflow was
> extended to explicitly `workflow_dispatch` the deploy and smoke workflows after a successful
> merge. The dispatch API is the recursion guard's one exemption.

If your automerge target branch has push-triggered workflows, either dispatch them explicitly
post-merge or switch the merge to a PAT/GitHub App token (which re-introduces loop risk you
must then guard yourself). The template shipped here does not include a post-merge dispatch
because it assumes no push-triggered deploy; add one if you have one.

### Poll-loop vs event-driven

The earlier variant polled check-run status in a wait loop after its trigger fired, and had to
mirror the lint workflow's path filters exactly; when the filters drifted, a docs-only PR could
merge without waiting for a required scan (a documented hole in that repo). The event-driven
head-SHA gate shipped here removes both needs: no polling, no filter mirroring, because the
gate re-evaluates on every checks-workflow completion and verifies actual check runs. Use the
poll loop only if you genuinely cannot restructure your required checks into one workflow.

## The second generation: extract the decision, then graduate trust

What the production variant grew into once PR volume made one human label per PR the
bottleneck. Three moves, in order. The files are in this directory: `decision_script.py` is
the parameterized second-generation gate, `tests/test_decision_script.py` its suite.

### Move 1: extract the merge decision to a tested script

The first generation's decision lives in workflow YAML and inline JavaScript, which means it
is tested in production, by merging things. The second generation splits the gate in two: the
workflow gathers inputs (branches, labels, draft state, changed files, check runs, mergeable
state) and a pure-function script decides. Two phases match two workflow steps: `lane` (may
this PR merge at all once green: branch lanes, draft guard, label, protected paths, content
policies) and `checks` (is it green right now: required checks, nothing failing, zero-runs
fail-closed, mergeable state clean). Three verdicts: `merge`, `wait` (exit green; a waiting
PR is not a broken PR; the next event re-evaluates), `fail` (a check is red; exit red so the
failure is visible). Every fail-closed guarantee becomes a unit test instead of a comment.

### Move 2: run the base branch's copy, and protect the machinery

One rule shapes the protected list: **a PR that edits its own merge gate must never
self-merge.** Two enforcement halves. The workflow checks out the BASE branch and runs THAT
copy of the decision script, so a PR's edit to the gate cannot influence its own gate run
(mind gotcha 9). And the gate's moving parts (the automerge workflow, the decision script,
any labeler workflows, the file that grants CI its token scopes) stay on `PROTECTED_PATHS`
no matter how far trust graduates, so a change to the gate always waits for the operator.

### Move 3: graduate trust one rung at a time (the maturity ladder)

- **Rung one: label-gated.** Every agent PR waits for the operator's approval label even
  with green checks; the label is the merge instruction. This is the kit's shipped default
  (`REQUIRE_LABEL = True` in the script; the operator-label hardening described above for
  the single-file workflow). Checks prove the change is safe to merge; the label says the
  operator wants it merged. Start here.
- **Rung two: label-free with protected paths.** Agent PRs into the main branch self-merge
  on green; the label gates only `PROTECTED_PATHS` (the machinery, plus high-blast-radius
  trees with no CI policy lane). The label keeps working everywhere as the explicit override
  and the unstick mechanism. The operator's reasoning when one production repo took this
  rung: by the time work reaches a PR, its concepts were already approved in the session
  that produced it; the label was re-approving nothing. Whether that holds for YOUR repo
  depends on how much judgment lives between "PR opened" and "PR safe", which is exactly
  what rung three makes explicit.
- **Rung three: content-policy lanes.** A path family leaves the protected list only when a
  content lint replaces the judgment the label was buying. Worked example:
  `../migrations/policy_checks.py` (forward-only lint, flag seeds default OFF with a
  quoted-approval escape header, duplicate-number guard). A violation does not fail the PR;
  it re-attaches the label requirement, and the label stays the override for legitimately
  destructive work.

Which rung is right is an operator decision, not a destination. A repo with one PR a day
loses nothing to rung one; a repo merging dozens of agent PRs a day feels rung one as a
queue. Climb deliberately, one rung at a time, and write the current rung down where your
agents read it. The fail-closed floor never graduates: drafts, zero check runs, failing
checks, dirty or unknown mergeable state, and unlistable file sets never merge, on any rung.
