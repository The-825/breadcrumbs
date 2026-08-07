# CLAUDE.md

> Resuming work? Read [`SESSION_STATE.md`](SESSION_STATE.md) at the repo root FIRST: the
> living handoff (active branch, in-flight edits, next steps, pending decisions). Refresh
> it fully when the operator says "checkpoint". Durable rulings go in
> [`planning/DECISIONS.md`](planning/DECISIONS.md) the same turn they land. Known issues
> are tracked as GitHub issues on this repo, not in a file.

This file is the behavioral contract for coding agents working in this repo. Read it top
to bottom before touching anything.

It is also a worked example. This repo teaches the rules-file pattern, so it runs on one.
If you are here to copy something, copy [`templates/CLAUDE_TEMPLATE.md`](templates/CLAUDE_TEMPLATE.md)
rather than this file: the template is the general skeleton, and this is one filled-in
instance of it, shaped by what this particular repo ships.

---

## WHAT THIS REPO IS

A public kit of agent-operations machinery: templates, a CI kit, command skills,
checklists, and the pattern docs behind them. Readers arrive with a specific problem,
usually that their agent sessions have no memory across a repo that matters, and leave
with files they can copy.

**Everything here is public and world-readable the moment it lands.** That is the single
most important fact about this repo, and it drives most of the rules below.

**Audience:** working developers and analysts running coding agents against a codebase
they cannot afford to break. Professional, direct, not academic and not dumbed down.

---

## BINDING RULES

Commit-time rules. Every change is judged against them. The integrity floor does not
decay for small fixes or for work done by subagents. If a rule has to break, stop and ask
the maintainer first.

**Integrity floor (never decays)**

1. **No private, production, or personal content, ever.** No schemas, records, reports,
   credentials, operational state, internal planning, or identifying detail about any
   organization or individual. War stories are welcome and are the most persuasive thing
   here, but tell them as what the artifact IS, never as an account of what was taken out
   to publish it. "The guard missed underscored names" ships. A sentence announcing that
   private detail was stripped does not, because announcing it tells a reader there was
   something private there, which is the disclosure the removal was meant to prevent
   (D-5, enforced by `ci-kit/guards/guard_no_provenance_leak.py`, whose blocked phrasings
   are the tell).
2. **No plagiarized or unattributed content.** Quotes and data carry their source at the
   point of claim.
3. **No unsourced numbers.** If a figure appears in a doc, it traces to something real in
   this repo or it does not ship.
4. **Confirm before deleting anything** (files, branches, published content). Flag
   irreversible actions before taking them, not after.

**Content quality**

5. **Every artifact stands alone.** A reader landing on one file gets the whole point of
   it without reading four others first. Cross-links add depth; they never carry the
   load.
6. **Say what a piece assumes.** Every artifact that assumes a language, platform, or
   workflow states that in its own header so a reader can adapt or skip without
   discovering the mismatch halfway through.
7. **No "fix it next PR" TODOs.** Fix it in the change, or log it in the issue ledger.

---

## BRANCH / PR CONVENTIONS

- Feature branches are `claude/<feature-slug>`, named after the work
  (`claude/migration-runner-tests`), never after a session or a generated id. Cut the
  branch first thing.
- PR titles carry intent tags: `feat:` / `fix:` / `docs:` / `chore:` / `refactor:` /
  `test:` / `ci:`.
- PR body template: **Summary / Test plan / What's NOT in scope.** The last section is
  what keeps scope honest.
- One concern per PR: a content addition OR repo infrastructure, not both.
- **The approval label is the merge instruction.** Without it a PR waits, no matter how
  green. Never merge by hand; the gate in `.github/workflows/` does the merging.
- **Verify before you push.** Re-read the full diff, run the cheapest check that covers
  the change, and confirm the diff matches the PR's stated scope. No "push then clean up."

---

## DECISION CAPTURE

**Write a ruling down the same turn it lands.** When a durable call gets made about this
repo (structure, naming, what ships, licensing), record it before moving on to the work
it unblocks. A ruling that lives only in a transcript gets re-litigated by the next
session, every time.

Format, one entry per decision, newest last:

```
## D-<n> · <date> · <topic>
Ruling: <the decision, one or two sentences>
Why: <one line of rationale>
Source: <where it landed>
```

Superseded decisions stay in the ledger with a "Superseded by D-<n>" line added. Never
silently rewrite an entry. The general pattern is
[`docs/decision-capture.md`](docs/decision-capture.md); the template is
[`templates/DECISIONS_TEMPLATE.md`](templates/DECISIONS_TEMPLATE.md).

---

## CONTINUITY CHECK

After changing any artifact, sweep the surfaces that cite it before finishing: the
README, the directory README that indexes it, and any doc that links to it. A renamed
file, a restructured directory, or a reworded claim has to match everywhere it appears.

Fix only the impacted files. Never touch consistent ones. If everything is consistent,
say "no drift" and change nothing. Drift found but out of scope for the current change
goes in the issue ledger, not a silent pass. The full procedure is
[`checklists/continuity-sweep.md`](checklists/continuity-sweep.md).

---

## RETRO

After a substantial change, ask what should have been known and was re-derived, what
friction repeated, and what a rule should now encode. Land each lesson as exactly one
durable artifact: a decision entry, a rule edit here, or an issue-ledger row. Nothing
stays only in chat. Refinement runs on evidence, never on a schedule; a retro with no
findings changes nothing and says so.

---

## WRITING RULES (binding for everything written here)

Applies to docs, templates, code comments, PR bodies, and commit messages.

- **No em-dashes.** Use commas, periods, or parentheticals.
- Plain, direct English. Lead with the answer, then the context.
- No filler, no motivation, no hype vocabulary, nothing that reads as generated.
- Second person for instructions. The reader is doing the work, not watching someone
  else do it.
- Name the concrete failure a rule prevents before stating the rule. A rule whose cost is
  invisible gets dropped the first time it is inconvenient.
- Walk through complex topics step by step rather than dumping them at once.

---

## SESSION EFFICIENCY

- Grep to locate, then read the narrow range. Do not read a whole file when 30 lines
  answer the question.
- Never re-read a file in the same session; the harness tracks file state.
- Cap tool output (`| head -30`, `--limit`).
- No "let me check X" preface before a tool call. Run the tool.
- End-of-turn summary: two sentences or fewer. Corrections: one.

---

## REPO MAP

```
README.md          Landing page: the problem, the one-afternoon path, the map
CLAUDE.md          This file
CONTRIBUTING.md    How to send a fix
LICENSE            MIT
templates/         Copy-and-adapt working files
  commands/        Slash-command definitions
  hooks/           Harness-side hooks
  test-harness/    In-process test harness skeleton
  ledger-tools/    Ledger hygiene tools
  standing-agents/ The standing-agent fleet kit
ci-kit/            The runnable enforcement kit
  guards/          Lint guards plus the fixtures that prove they bite
  migrations/      Migration runner and policy checks, with tests
  workflows/       CI workflow templates around the fail-closed merge gate
skills/            Paste-able rule sets for your own rules file
checklists/        Operational checklists
docs/              Pattern essays: the reasoning behind each artifact
playbook/          How the pieces fit together; multi-agent operation
```
