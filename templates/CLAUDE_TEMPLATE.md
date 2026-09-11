# CLAUDE.md starter template

Anything that lives only in chat history gets re-derived, differently, every session. An agent without a rules file will break your conventions, not out of malice, but because nothing pinned them down. This file is the spine of agent-assisted work: the single source of behavioral truth in the repo, read top to bottom before anything is touched, and the file every other doc defers to on rules. Copy the template below into your repo root as `CLAUDE.md` (or `AGENTS.md`), fill the placeholders, and delete what does not apply.

## The rules-spine guide

This is the short version; the full essay, with the failure each section prevents and an afternoon-sized starter for each, is [docs/rules-spine.md](../docs/rules-spine.md).

What each section is for, so you fill it with intent instead of copying blind:

- **Who you work with.** The owner, their role, and the hard boundaries the agent must never cross (contexts it must not mix, data it must not expose). Boundaries stated here survive every session.
- **What this system is.** One paragraph, plus an explicit operating tier. The tier line matters most: it stops the agent (and any cheaper subagent it spawns) from downgrading to prototype discipline on a "small fix."
- **Binding rules.** Numbered, grouped, judged at commit time. Group them so the floor is visible: security, data, code conventions, testing. A rule the agent cannot cite by number is a rule it will eventually skip.
- **PR conventions.** Shape rules for how work lands: titles, branches, description template. The "What's NOT in scope" line is the single highest-value item; it forces scope discipline on every PR.
- **Operator preferences.** Tone and format rules binding for everything the agent writes, not just code. Without them every doc and commit message sounds like a press release.
- **Session efficiency.** The rules file attaches to every turn, so verbosity is a per-turn tax. These habits cap it.
- **Pointers.** Where the rolling state, the rulings, and the settled facts live. The rules file holds the RULES; those files hold everything that changes.
- **Known issues.** A numbered ledger so problems get tracked instead of rediscovered. Entries move to Resolved with a fix reference; they are never silently dropped.

## The template

````markdown
# CLAUDE.md · <project name>

> Resuming work? Resolve the owning checkout, then read `SESSION_STATE.md` FIRST
> as the candidate handoff. Read this file completely, then verify repository
> identity, branch, worktree, source revisions, and current PR state before acting.
> Refresh the handoff when <operator name> says "checkpoint".

This file is the single source of behavioral truth for this repo. Read it top to
bottom before touching anything.

---

## WHO YOU WORK WITH

**<Operator name>**, <role>. Email: <email>.

<Hard boundaries. Examples: "Keep <context A> and <context B> completely separate
unless bridged explicitly." "End users never see SQL, raw data, or backend config."
"Never log or commit customer PII, secrets, or API keys.">

---

## WHAT THIS SYSTEM IS

<One paragraph: what the system does, who uses it, where it runs.>

**Operating tier: <production / internal tool / prototype>.** <If production:>
This system is live and handles real <customer / member / order> data. Every change
defaults to production discipline no matter how small the diff looks. The security
floor never decays, including on small fixes and work done by subagents. If a
subagent would default to lower discipline on a small fix, that default is wrong
for this repo. MVP and prototype tiers explicitly do not apply here.

---

## BINDING RULES

Commit-time rules. Every PR is judged against them. Self-correct before proposing
a change that breaks one; if a rule has to break, stop and ask <operator name> first.

**Security floor (never decays)**
1. **All queries are parameterized.** Never interpolate user input into SQL.
2. **Auth at the boundary, every time.** Every endpoint that touches <sensitive
   data> resolves the caller first, through one grep-auditable decorator.
3. **No silent failures.** Every try/except logs. Every promise has a catch.
   Every fetch has a fallback UI state.
4. **No secrets or PII in test fixtures.** Enforced by a pre-push lint.

**Data rules**
5. **Migrations are forward-only.** Add columns, never roll back schema. Old
   columns stay with a deprecation note.
6. **Soft-delete for records the process depends on.** The principle is
   recoverability, not a blanket DELETE ban. If you cannot verify a delete is
   loss-free, archive instead or ask.

**Code conventions**
7. **No magic numbers.** Every threshold (<page size, price floor, retry cap>)
   lives in the central config registry. Never inline a literal.
8. **No new env var without an entry in the config registry** (<path, e.g.
   `config.py`>, one frozen dataclass).

**Testing**
9. **Every user-visible feature ships behind a feature flag, default OFF in
   production.** Reversible by config, not by revert. Flags fail closed.
10. **Every user-visible feature ships with at least one end-to-end test.**
    Coverage compounds; every later PR is regression-tested against the set.

---

## PR CONVENTIONS

- Intent-tagged titles: `feat:` / `fix:` / `docs:` / `chore:` / `refactor:` /
  `test:` / `ci:`. The title names the work, not the session.
- Branches are slugged after the feature: `<prefix>/<feature-slug>`. Never push
  a session-named or auto-generated branch. Cut the feature branch first thing.
- PR description template: Summary / Test plan / **What's NOT in scope**. The
  last section forces scope discipline.
- One coherent concern per PR: infrastructure OR a user-visible improvement,
  never both. ~500 changed lines is a soft prompt to split, not a hard wall.
- Verify before you push: re-read the full diff, run the cheapest check that
  covers the change, confirm the diff matches the stated scope.

For an authorized task, follow the task-owned commit through push, PR, checks and
review for the current PR head, any already-authorized approval, and verified merge
to the base branch. Record deployment separately. Do not stage unrelated files,
bypass gates, treat enabled automerge as a completed merge, or delete a branch
without confirmation.

---

## OPERATOR PREFERENCES

Binding for everything written here: chat replies, docs, PR bodies, commit
messages, code comments.

- <Tone rules. Example: "Plain English, direct. Lead with the answer. No filler,
  no over-complimenting.">
- <Formatting rules. Example: "No em-dashes in anything newly written.">
- <Decision style. Example: "Give a recommendation, not a list of options. See a
  problem with the ask? Say it BEFORE executing.">
- <Deletion policy. Example: "Confirm before deleting anything. Flag irreversible
  actions before taking them.">

---

## SESSION EFFICIENCY

- Read narrow line ranges: grep to locate, then read just those lines.
- Reuse a prior read only while its source revision and dependent assumptions are
  unchanged. Re-read the affected range after an edit, branch change, pull, merge,
  generated-file refresh, or conflicting evidence.
- Cap tool output (`| head -30`, `--limit`).
- End-of-turn summary: two sentences or less. Corrections: one sentence.
- No "let me check X" preface before tool calls. Run the tool.

---

## WORK PLAN AND CHECKPOINTS

- Save a plan before implementation. Scale it to the task and state the objective
  and deliverables, scope and exclusions, affected repositories and dependencies,
  constraints, completion evidence, milestones, and exact intended files. Add
  risks, authority, model constraints, and release steps when they matter. Revise
  it when scope or evidence changes.
- Record the selected approach and credible alternatives, including reuse or no
  change when relevant. State their tradeoffs and why the selected approach fits
  the evidence and constraints.
- Challenge assumptions, likely failures, contradictory evidence, edge cases,
  privacy and authority boundaries, recovery, and tests that could disprove
  success. Record unresolved issues and how each will be resolved.
- Checkpoint material decisions, corrections, milestones, blockers, source
  changes, handoffs, objections, scope revisions, and evidence-backed completion.
  A finished milestone does not finish its parent task automatically.
- Record verified, unverified, pending, and blocked state with provenance. Name
  source revisions, assumptions, superseded claims, unfinished work, and the next
  executable step. Old memory is context, not new authority.
- A failure record separates the attempted action, observation, known cause,
  suspected cause, side effects, blocker, and next action. A workaround links the
  failure, rationale, tests, and residual limits. Attempted recovery is not
  verified recovery.
- Delegated workers inherit the goal, exact scope, exclusions, authority, required
  model or routing constraint, checkpoint duties, and completion evidence. A
  dispatch or worker response is not integration. The parent verifies the diff
  and evidence. Never silently substitute a required model.
- Define the planning and review model separately from the implementation model:
  `<planner model and effort>` for planning and review, `<worker model and
  effort>` for implementation. Use exact identifiers only when current host or
  provider metadata verifies them. Record the selected model from that metadata,
  not from model-authored prose.
- Reuse bounded source-linked evidence only while its revision and assumptions
  remain current. A changed PR head invalidates older checks. Never invent token
  counts. Markdown guidance does not prove runtime enforcement.
- Scale planning depth to the task, but do not omit the considerations above.
  Filled fields do not prove substantive review. Do not add a reviewer only to
  satisfy the template. If one is useful, apply the planning-model policy and
  record what the reviewer actually tested.

---

## WHERE EVERYTHING ELSE LIVES

| File | Holds | Updated when |
|---|---|---|
| `SESSION_STATE.md` | The rolling handoff: branch, in-flight work, next steps | Operator says "checkpoint" |
| `planning/DECISIONS.md` | Durable operator rulings, appended same turn they land | A ruling lands |
| `engineering/CONCLUSIONS.jsonl` | Settled facts sessions have verified | A fact worth not re-deriving is proven |

This file stays authoritative on rules; those files hold state, rulings, and
settled knowledge. Content moves between them on the events above, never by whim.

---

## KNOWN ISSUES

Numbered ledger. Log an entry as `KI #<n>` with the date found, the evidence, and
its status. Move fixed entries to Resolved with the fix reference (PR or commit).
Never silently drop an entry.

### Active

(none yet)

### Resolved

(none yet)

---

## REPO MAP

```
<one line per top-level file or directory, purpose only>
```

Split into "exists now" and "target layout" if the repo is young; create
directories when their first real content lands, not before.
````

## Adoption notes

Keep the active portion of the file under about 700 lines. It attaches to every turn, so length is a recurring tax; move resolved history to a runbook or changelog and leave a one-line pointer. Add an anti-goals line once you know your repo's recurring temptations ("no new build step until the current pattern hurts across at least three separate features" is a good starter). And when a past bug earns an invariant, record it in a "fixed, do not revert" list so no future session can reintroduce it.

The rules file is not documentation. It is the part of your judgment that survives the session.
