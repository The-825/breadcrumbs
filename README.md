# breadcrumbs

Your coding agent starts every session with no idea what the last one did.

You feel it as a tax before any real work happens. The session re-reads files to guess
what is in flight. It re-derives a decision you already made and sometimes lands on a
different answer. You open a file, think "who changed this," and realize it was your own
agent, in a session you closed yesterday, for a reason nobody wrote down. Compact a long
session and the same thing happens from the inside: an idea from an hour ago quietly
does not survive the summary, and gets redone next week.

None of that is a model problem. It is a memory problem, and it lives in your repo, not
in the tool.

**breadcrumbs** is the trail one session leaves so the next one finds its way back:
copy-and-adapt templates, a CI kit whose guards are tested to actually bite, command
skills, and the pattern docs behind each piece. MIT licensed. No signup, no service, no
dependency on any particular agent product.

The premise underneath all of it: a rule that lives only in a doc gets violated
silently. A rule with a guard, a gate, or a template becomes structurally hard to break.
This repo ships the guards, the gates, and the templates.

## Start here, one afternoon

Three files and one gate give agent work a memory and a brake. Do these in order and
stop when you have had enough for the day; each one stands on its own.

1. **A handoff file.** Copy [`templates/SESSION_STATE_TEMPLATE.md`](templates/SESSION_STATE_TEMPLATE.md)
   to your repo root. It holds only what is in flight: branch, open PR, half-done edits,
   next steps. Refresh it on a trigger word you say out loud, not on "keep it updated,"
   which means never.
2. **A decisions ledger.** Copy [`templates/DECISIONS_TEMPLATE.md`](templates/DECISIONS_TEMPLATE.md).
   Numbered entries, newest last. Write the entry the same turn you make the call, before
   the work it unblocks. A ruling that lives only in a transcript gets re-litigated.
3. **A rules file.** Copy [`templates/CLAUDE_TEMPLATE.md`](templates/CLAUDE_TEMPLATE.md)
   and delete what does not apply to you. This is the file every session boots from, so
   it is the highest-leverage thing in the repo.
4. **A merge gate.** [`ci-kit/workflows/`](ci-kit/workflows/) ships a fail-closed
   automerge that only merges when every required check is green on the exact head commit,
   and only after you apply an approval label by hand. Read
   [`AUTOMERGE_GOTCHAS.md`](ci-kit/workflows/AUTOMERGE_GOTCHAS.md) before adopting it; the
   naive version of this workflow has about ten non-obvious ways to fail.

## What is in here

| Directory | What it gives you |
|---|---|
| [`templates/`](templates/) | Copy-and-adapt working files: rules file, session handoff, decision and authority ledgers, incident and ADR templates, plus slash commands, a test-harness skeleton, ledger tools, and harness hooks |
| [`ci-kit/`](ci-kit/) | The runnable part: lint guards that ship with fixtures proving they bite, a migration runner with policy checks, and CI workflow templates around a fail-closed merge gate |
| [`skills/`](skills/) | Paste-able rule sets for your own rules file, from data-truth rules to forward-only migrations |
| [`checklists/`](checklists/) | Two-minute operational checklists: PR discipline, pre-push verification, the continuity sweep |
| [`docs/`](docs/) | The reasoning behind each artifact. Read one when you want to know why a piece is shaped the way it is |
| [`playbook/`](playbook/) | How the pieces fit together, and the patterns for running more than one agent at a time |

## How to use this repo

Take the pieces, not the whole thing. Nothing here needs the rest of it to work, and
adopting all of it at once is the fastest way to adopt none of it. Copy a file, fill in
the placeholders, delete the parts that do not match how you work.

Some of it will not fit you. The guards assume a Python and JavaScript tree; the merge
gate assumes GitHub Actions; the ledger formats assume you are the one making the calls.
Where a piece assumes something, it says so in its own header. Adapt or skip.

If a piece is unclear or broken, open an issue.
[CONTRIBUTING.md](CONTRIBUTING.md) is the short read for sending a fix.

## Where this came from

These patterns were extracted from running coding agents daily against a production
system that handles regulated data for real users, with every domain identifier removed.
Templates here are authored fresh from documented skeletons rather than scrubbed from
real instances, because scrubbing risks residue and fresh authoring does not. Where a
real incident is what made a rule land, it appears as an anonymized note in a clearly
labeled callout.

No production content ships here: no schemas, no reports, no records, no operational
state.

## The book

This repo is the practical companion to *From Archivist to Architect*, Book 1 of The
Architect's Blueprint series, by Jovan Smith. The book tells the story; this repo is the
working machinery, and it stands on its own without it.

> Coming to Amazon.

## License

MIT. See [LICENSE](LICENSE). Take it, adapt it, ship it.
