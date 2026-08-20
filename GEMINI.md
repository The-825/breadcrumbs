# GEMINI.md - breadcrumbs agent context

You are working in **breadcrumbs**, a public kit of agent-operations machinery:
templates, a CI kit, command skills, checklists, and the pattern docs behind
them. Readers arrive with a specific problem, usually that their coding-agent
sessions have no memory across a repo that matters, and leave with files they
can copy. The audience is working developers and analysts running coding
agents against a codebase they cannot afford to break: professional and
direct, not academic, not dumbed down.

**[CLAUDE.md](CLAUDE.md) is the single source of behavioral truth for this
repo and remains authoritative.** This file mirrors its binding rules,
conventions, and tone directly, because a review or CLI surface may not
reliably follow an in-repo pointer to another file. If anything here conflicts
with CLAUDE.md, CLAUDE.md wins.

## The single most important fact about this repo

**Everything here is public and world-readable the moment it lands.** Most of
the rules below exist because of that one fact.

## Integrity floor: never decays, flag violations on sight

1. **No private, production, or personal content, ever.** No schemas,
   records, reports, credentials, operational state, internal planning, or
   identifying detail about any organization or individual. War stories are
   welcome and are the most persuasive thing here, told as what the artifact
   IS, never as an account of what was taken out to publish it. A sentence
   announcing that private detail was stripped is itself a disclosure and does
   not ship.
2. **No plagiarized or unattributed content.** Quotes and data carry their
   source at the point of claim.
3. **No unsourced numbers.** A figure in a doc traces to something real in
   this repo or it does not ship.
4. **Confirm before deleting anything** (files, branches, published content).
   Flag irreversible actions before taking them, not after.

## Content quality

5. **Every artifact stands alone.** A reader landing on one file gets the
   whole point of it without reading four others first. Cross-links add
   depth; they never carry the load.
6. **Say what a piece assumes, and whether it ships.** Every artifact that
   assumes a language, platform, or workflow states that in its own header so
   a reader can adapt or skip without discovering the mismatch halfway
   through. A doc describing a mechanism also says whether that mechanism
   ships in this kit: pattern-only is a fine answer, silence is not, because
   a reader defaults to assuming it ships.
7. **No "fix it next PR" TODOs.** Fix it in the change, or log it as a GitHub
   issue on this repo.

## Branch, PR, and merge conventions

- Feature branches are `claude/<feature-slug>`, named after the work, never
  after a session or a generated id.
- PR titles carry intent tags: `feat:` / `fix:` / `docs:` / `chore:` /
  `refactor:` / `test:` / `ci:`.
- PR body template: **Summary / Test plan / What's NOT in scope.**
- One concern per PR: a content addition OR repo infrastructure, not both.
- **The approval label is the merge instruction, tiered by diff.** A PR whose
  changed files are ALL in the safe set (`docs/`, `checklists/`, `README.md`,
  the decisions ledger, `SESSION_STATE.md`; no deletions or renames) merges on
  green with no label. Everything else waits for the label, no matter how
  green. Never assume a green, unmerged PR is broken; it may simply be
  waiting on the label.
- Never merge by hand. The gate in `.github/workflows/` owns merging.
- Verify before pushing: re-read the full diff, run the cheapest check that
  covers the change, confirm the diff matches the PR's stated scope. No
  "push then clean up."

## Decision capture

When a durable call gets made about this repo (structure, naming, what
ships, licensing), it is recorded in `planning/DECISIONS.md` before the work
it unblocks continues. A ruling that lives only in a chat transcript gets
re-litigated by the next session.

## Continuity check

After a change to any artifact, the surfaces that cite it need a matching
sweep: the README, the directory README that indexes it, and any doc that
links to it. Fix only the impacted files; if everything is consistent, say
so and change nothing.

## Writing rules (binding for everything written here)

Applies to docs, templates, code comments, PR bodies, commit messages, and
review comments.

- **No em-dashes.** Use commas, periods, or parentheticals.
- Plain, direct English. Lead with the answer, then the context.
- No filler, no motivation, no hype vocabulary, nothing that reads as
  generated.
- Second person for instructions. The reader is doing the work.
- Name the concrete failure a rule prevents before stating the rule. A rule
  whose cost is invisible gets dropped the first time it is inconvenient.
- Walk through complex topics step by step rather than dumping them at once.

## Known issues

This repo tracks known issues as **GitHub issues**, not as a ledger inside
CLAUDE.md. Check the repo's open issues rather than expecting a KI list here.

## Repo map

```
README.md          Landing page: the problem, the one-afternoon path, the map
CLAUDE.md           Full behavioral contract (this file's source of truth)
CONTRIBUTING.md      How to send a fix
LICENSE              MIT
kit.json              Machine-readable inventory (paths, assumptions, selftests)
llms.txt               Agent-facing map: route by problem
CONTEXT_BUDGET.md       Line budgets for the boot set
templates/               Copy-and-adapt working files
ci-kit/                   The runnable enforcement kit (guards, migrations, workflows)
skills/                    Paste-able rule sets for your own rules file
checklists/                 Operational checklists
docs/                        Pattern essays behind each artifact
playbook/                     How the pieces fit together
```

## Maintenance note (for repo sessions, not for the reviewing agent)

This file deliberately duplicates CLAUDE.md content so a surface that cannot
reliably follow in-repo pointers still has the binding rules, conventions,
and tone in front of it. CLAUDE.md remains authoritative. When CLAUDE.md's
binding rules, branch/PR conventions, or writing rules change, this mirror
needs a manual refresh in the same change, not a later cleanup pass. The
sibling vendor-neutral pointer stub is [AGENTS.md](AGENTS.md).
