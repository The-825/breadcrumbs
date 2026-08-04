# Command starter set

> Part of the companion kit for *From Archivist to Architect* (The Architect's Blueprint, Book 1).

Twenty-nine copy-paste slash-command definitions for Claude Code, extracted from a production agent-ops setup and generalized. Without a shared command set, every session re-derives its own procedure for branching, shipping, and closing out, and the write-authority boundary drifts with it. Each is a markdown file with YAML frontmatter; the body is the instruction the model follows when the command is invoked. They pair with the templates one directory up (the session-state and conclusions-store templates especially), but each works alone.

Note: this location is provisional pending a repo-layout decision on how command artifacts are packaged; if they move, it is one `git mv` and the files themselves do not change.

## Install

1. Copy the files you want into your repo's `.claude/commands/` directory. The filename becomes the command: `ship.md` installs `/ship`.
2. Fill the angle-bracket placeholders (`<main-branch>`, `<branch-prefix>`, `<conclusions-store>`, `<your-health-endpoint>`, and so on). They are all visible inline, and the more configurable files list theirs in a fill-these line near the top of the body.
3. Delete what does not apply to your repo. A command that references a file you do not keep should lose that step, not keep a dead pointer.

Frontmatter fields: `description` (shown in the command picker), `argument-hint` (shown as you type; arguments land in the body wherever `$ARGUMENTS` appears), `allowed-tools` (the tools the command is allowed to run), and optionally `model` (pin a command to a specific model). All are optional; a plain markdown body still works as a command, but `description` keeps the picker legible and `allowed-tools` scopes what the command can do.

## The commands

| Command | What it does · when to run it |
|---|---|
| [sprint.md](sprint.md) | Cuts a fresh feature branch from the default base on the `<branch-prefix>/<feature-slug>` convention. Run at the start of any coherent unit of work. |
| [ship.md](ship.md) | Commits, runs the pre-push checks and the adversarial pass, pushes, and opens a ready-for-review PR with a structured body. Run when the work is ready for review. |
| [adversarial-verify.md](adversarial-verify.md) | Spawns a subagent whose only job is to refute the current diff, then triages findings by severity and confidence. `/ship` runs it automatically; run it standalone for a second opinion on any diff. |
| [tiered-review.md](tiered-review.md) | Reviews a change set with a model-tier ladder: cheap draft pass, stronger adversarial verify pass, whole-change reconcile pass only when the change is wide. Run on large or risky change sets. |
| [model-check.md](model-check.md) | Classifies a task description (LOOKUP / SHIP / COMPLEX) and recommends a model tier from a table you fill in. Run before starting work when the right tier is not obvious. |
| [retro.md](retro.md) | Post-task retrospective: mines the arc that just finished for lessons and lands each as exactly one artifact (conclusions append, command edit, or wishlist row). Run at the end of a coherent arc; pairs with docs/self-improvement-loop.md. |
| [deflake.md](deflake.md) | Works one flaky test: reproduce N times at zero retries, classify race / baseline / env, fix by class, log the row in the flake ledger. Run on any test that passed on retry. |
| [status.md](status.md) | One-screen snapshot: open PRs, local tree, what awaits the operator, what is blocked, next recommended action. Run at session start or after time away. |
| [checkpoint.md](checkpoint.md) | Rewrites `SESSION_STATE.md`, the living handoff file, from current reality, preserving the irreplaceable-values section verbatim. Run on the operator's "checkpoint" trigger, and before any model or session switch. |
| [warp.md](warp.md) | Answers "what do we know about X?" from the conclusions store, the repo index, and recent git history, without re-deriving from source. Run before touching an area you have not worked in recently. |
| [pending.md](pending.md) | Sweeps the repo for every deferred idea and follow-up, and reports each with its current status (delivered, ripe, blocked, invalidated, recurring). Run periodically so deferred work resurfaces instead of dying. |
| [scout.md](scout.md) | Evaluates an external URL against your repo with a have / borrow / adopt / skip verdict per concept, and persists a dated report. Run when someone sends you a tool or repo worth a look. |
| [scout-discover.md](scout-discover.md) | The autonomous variant of `/scout`: generates candidates from the live ecosystem with no URL given, dedupes against prior reports, deep-evaluates the top few, and ships dated reports plus a ranked digest. Run periodically so borrowable ideas find you. |
| [optimize.md](optimize.md) | Five-phase performance review (baseline, frontend, transport, backend runtime, regression guards) with evidence-only findings. Run a few times a year or after a slow-feeling stretch. |
| [session-cost.md](session-cost.md) | Prints a per-model token and estimated-cost table for a saved session transcript, via a small stdlib-only helper script included in the file. Run when you want to know what a session cost. |
| [verify-deploy.md](verify-deploy.md) | Confirms a merge actually rolled out by checking the deploy workflow's runs and the health endpoint's version contract. Run after a merge you care about, mindful of batched deploy windows. |
| [merge-train.md](merge-train.md) | Serial merge driver for a wave of open PRs: order, scope-check, consolidate compatible small ones, and unstick each car while the gate lands them. Run when several PRs are ready at once. |
| [promote.md](promote.md) | Drives one staging-to-main promotion: preflight, the manifest PR, the known snags, the post-merge staging reset. Run at promotion time; pairs with docs/staging-promotion.md. |
| [land.md](land.md) | Shepherds one or more open PRs to merged: checks, conflicts resolved on the feature branch, and the correct automerge path. Never merges by hand and never applies the approval label. Run when a green PR sits unmerged or a wave needs walking home. |
| [close-out.md](close-out.md) | End-of-session close-out: every PR accounted for, feature-toggle state noted, every ruling captured, ledgers ticked, then a checkpoint refresh of the handoff file. Run before ending any session that produced work. |
| [grant.md](grant.md) | Records a standing authority grant in the authority ledger, or flips an existing grant to revoked or expired (lines never deleted). Run the same turn the operator issues a grant, before the agent work that needs it. |
| [summon.md](summon.md) | Summons a specialist desk: resolves it from the registry, assembles its boot pack, and spawns the agent with a commander's-intent task spec (GOAL / CONSTRAINTS / DONE-LOOKS-LIKE). Run when a task belongs to a standing desk rather than the coordinating session. |
| [incident.md](incident.md) | Incident triage with rollback playbooks, cheapest reversal first: flag flip, config revert, bad-deploy revert, data restore, user comms. Run when production is wrong and the clock is running. |
| [prompt-master.md](prompt-master.md) | Silently restructures a messy, voice-transcribed, or unstructured task prompt into a clean task spec, then executes the restructured version. Run on brain-dump prompts instead of asking for a spec. |
| [transcript-triage.md](transcript-triage.md) | Triages a pasted meeting transcript: extracts the other party's questions and commitments, answers them grounded in live code and data, and converts their asks into the work plan. Run after any meeting that produced asks. |
| [review-family.md](review-family.md) | Grouped operator review of a family of like surfaces: a resumable ledger, numbered questions each with a recommended pick, verbatim same-turn ruling capture, and a roll-up gate before close. Run when a whole class of items needs a human ruling per item. |
| [find.md](find.md) | Spawns a cheap read-only subagent that locates a file, symbol, or value and returns only the location, keeping the search payload out of the calling context. Run instead of grepping in-session for anything you only need to find. |
| [recall.md](recall.md) | Greps the local session transcripts and compaction saves to recover earlier context (what was said, decided, or measured) instead of re-deriving it. Run before re-deriving anything from earlier in this session or a prior one. |
| [setup-check.md](setup-check.md) | Verifies each checkable claim in the setup or onboarding doc against reality, with a per-claim verdict table; drift is filed in the KI ledger, never silently fixed. Run periodically and before pointing a new arrival at the guide. |

## Safety posture

These commands are deliberately one-sided about write authority. `/sprint` creates a local branch and stops. `/ship` opens the PR and stops: it never merges, never enables auto-merge, and never applies an approval or merge-gate label, because authorizing a merge is the operator's act. `/land` shepherds gated PRs the same way: it reports green-and-waiting, and applying the label stays the operator's move. `/status`, `/warp`, `/pending`, `/verify-deploy`, and `/model-check` read and report only. Keep that boundary when you adapt them; a command that can both open and approve its own PR removes the one human checkpoint in an agent-driven flow.
