# The rules spine: a guide to writing a binding CLAUDE.md

> Part of the companion kit for *From Archivist to Architect* (The Architect's Blueprint, Book 1).

*This essay is the long version of the short guide embedded in
[templates/CLAUDE_TEMPLATE.md](../templates/CLAUDE_TEMPLATE.md); copy that template when
you are ready to write yours.*

## Why an agent-operated repo needs one

A repo where AI agents do real work has a failure mode human teams mostly avoid: nothing
carries over. Every session starts cold. A convention agreed on Tuesday is invisible on
Thursday. A subagent spawned mid-task inherits none of the caution its parent was told to
use. Standards do not decay because anyone decided to lower them; they decay because
nothing pinned them down, and velocity fills the vacuum.

Human teams absorb their discipline through code review, hallway correction, and shared
memory. An agent gets one substitute for all three: a rules file the harness loads at
session start (Claude Code reads `CLAUDE.md` automatically; other harnesses read
`AGENTS.md` or their own equivalent). The spine of that file is a set of binding
commit-time rules: the numbered list every PR is judged against before it merges.

"Binding" is the load-bearing word. A style guide describes preferences. A spine states
obligations, with the expectation that a PR breaking one gets fixed before it lands, no
matter who or what produced the diff and no matter how small the diff is. The difference
shows up under pressure: preferences lose to deadlines; rules that a CI guard enforces
and a human merge gate backs do not.

Three properties make a rule binding rather than decorative:

- **Judged at commit time.** The rule is checked when the change is proposed, not
  discovered in a cleanup sprint. A session self-corrects before proposing a change that
  breaks one; if a rule genuinely has to break, the session stops and asks the operator
  first.
- **Numbered and citable.** "Rule 6" fits in a review comment, a commit message, and an
  agent's working context. A rule that cannot be cited by number will eventually be
  skipped, because restating a paragraph is friction and citing an integer is not.
- **Grouped so the floor is visible.** Security and integrity rules sit together at the
  top, under a heading that says they never decay. Grouping is what lets a session see
  at a glance which rules are absolute and which are conventions.

The rest of this guide walks the skeleton those rules live in, section by section: what
each section binds, the failure it prevents, and a starter version you can write in one
afternoon. The template carries the full skeleton, including the parts this essay skips
(owner identity, operator tone preferences, the repo map); the eight below are the
load-bearing ones.

## The operating-tier statement

**What it binds.** One line near the top of the file: what tier this system runs at
(production, internal tool, prototype) and what that tier means for the discipline
floor. For a production repo it reads like this: every change defaults to production
discipline no matter how small the diff looks, and if a subagent or a cheaper model
would default to lower discipline on a small fix, that default is wrong for this repo.

**The failure it prevents.** The small-fix downgrade. Nobody proposes lowering the
security floor; it lowers itself, two lines at a time, because every gate feels
disproportionate to a tiny diff. Subagents make this worse: a cheap model dispatched for
a trivial edit will produce prototype-grade work inside a production repo unless the
tier is stated where every session, at every tier, reads it.

**The afternoon version.** Three sentences. Name the tier, state that the floor applies
regardless of diff size, and state that it applies to subagents. That is the whole
section; its value is in existing, not in length.

## The integrity floor

**What it binds.** The never-decays group at the top of the numbered rules. For a
service handling real user data: parameterized queries only, auth resolved at the
boundary through one grep-auditable path, no silent failures, no secrets or PII in
fixtures or logs, forward-only migrations. For a content or docs repo the floor is
integrity in the other sense: nothing fabricated, nothing unattributed, no identifying
detail about real people, confirm before deleting anything.

**The failure it prevents.** Erosion by exception. Each floor rule survives the big PRs,
where scrutiny is high, and dies in the small ones, where it is not. On the production
system this kit was extracted from, the floor rules exist because each one was once
violated in a diff that looked too small to matter.

**The afternoon version.** Write the three to five rules whose violation would be a
genuine incident, not a nuisance. Put them first, number them, and label the group
"never decays." Resist the urge to add rule six on day one; the floor earns trust by
being short enough that every session actually holds all of it.

## Branch and PR conventions

**What it binds.** The shape of every unit of work. Feature-slugged branches
(`<prefix>/<feature-slug>`, cut first thing, never a session-named or auto-generated
branch). Intent-tagged titles (`feat:` / `fix:` / `docs:` / `chore:`) that name the
work, not the session. One coherent concern per PR, with roughly 500 changed lines as a
soft prompt to ask whether it splits. A fixed description template ending in **What's
NOT in scope**. And verify before push: re-read the diff, run the cheapest check that
covers it, confirm it matches the stated scope.

**The failure it prevents.** Work nobody can find or trust. An agent left to harness
defaults will push to whatever auto-named branch the harness created, and a remote full
of session-hash branches is archaeology nobody does. We adopted the
never-push-a-session-branch rule after finding a full arc of feature work parked on one;
the rule text now carries the date it was codified, which is exactly how rules should be
born. The scope section works from the other direction: it makes the author say out loud
what this PR deliberately does not do, which is where scope creep goes to get caught.

**The afternoon version.** Adopt the title tags, the branch pattern, and the
three-section PR body (Summary / Test plan / What's NOT in scope). The
[pr-discipline](../checklists/pr-discipline.md) and
[pre-push](../checklists/pre-push.md) checklists in this kit are the runnable form.

## The label-gated merge

**What it binds.** Who presses the button. Merging can be automated, but the instruction
to merge stays human: a named label only the operator applies. The automation is
fail-closed: a draft never merges, a PR with zero completed checks never merges, a
failing or unknown check state never merges. And the machinery is self-protecting: a PR
that edits the merge gate itself never self-merges through it.

**The failure it prevents.** An agent merging its own work, and the quieter cousin,
"green" meaning "no checks ran." Both are one bad afternoon away from a production
incident. The label keeps a human on the merge button at near-zero cost: applying it
takes two seconds and works from a phone, so the human stays in the loop without
becoming the bottleneck.

**The afternoon version.** Start with the convention alone: the agent never merges; the
operator's label is the merge instruction. When you want the automated version, this kit
ships it label-gated by default
([ci-kit/workflows/automerge.yml](../ci-kit/workflows/automerge.yml), `REQUIRE_LABEL`);
relaxing that flag is the documented graduation step, and the self-protecting machinery
for merge-gate edits lives in the tested decision script in the same directory.
[AUTOMERGE_GOTCHAS.md](../ci-kit/workflows/AUTOMERGE_GOTCHAS.md) documents the ten
non-obvious ways a naive automerge fails, each one paid for in production.

## The numbered issue ledger

**What it binds.** How problems are tracked. Every discovered issue gets a numbered
entry (`KI #<n>`) with the date found, the evidence, and its status. Fixed entries move
to a Resolved section with the fix reference (PR or commit). No entry is ever silently
dropped, and numbers are never reused.

**The failure it prevents.** Rediscovery. Sessions have no shared memory, so without a
ledger the same broken button gets found, diagnosed, and half-fixed twice in one week by
two sessions that each thought they were first. The never-silently-dropped rule guards
against the other failure: a helpful cleanup pass that prunes "stale" entries and
deletes the only record that a problem exists.

**The afternoon version.** Two headings (Active, Resolved) and the format line, kept in
the rules file itself. Move the ledger to its own file when it outgrows the spine.

## Same-turn decision capture

**What it binds.** What happens when the operator makes a durable ruling: a definition,
a threshold, a naming call, a policy. The session appends it to an append-only decisions
ledger in the same turn, before starting the work the ruling unblocks. Each entry is the
ruling, one line of why, and where it landed. Superseded entries get a superseded-by
line; nothing is rewritten.

**The failure it prevents.** Re-litigation. A ruling that lives only in a transcript
does not exist next session, so the operator gets asked the same question twice, or
worse, the next session quietly decides the other way. Same-turn is the load-bearing
part: sessions end or compact without warning, so capture at the event beats capture at
the end every time the end never arrives.

**The afternoon version.** Create the ledger from
[templates/DECISIONS_TEMPLATE.md](../templates/DECISIONS_TEMPLATE.md) and add one rule
to the spine: rulings are appended the same turn they land.

## Continuity checks

**What it binds.** What "done" means when a fact changes. A change is not done until
every surface that cites the changed fact matches, and completeness counts: a surface
that should now mention the fact and does not is still a miss. "It wasn't wrong, just
absent" does not pass.

**The failure it prevents.** Drift between surfaces. Change a price on one page and the
FAQ keeps selling the old one; rename a feature and the docs, the tests, and the
marketing copy each keep a different old name. Agents amplify this failure because they
edit exactly what they were asked to edit; the sweep rule is what widens the check
beyond the literal ask.

**The afternoon version.** List your citing surfaces once, in the rules file. Then one
rule: before finishing, grep every changed literal (the number, the name, the status
word) across that list, and on a rename grep the old name too, because the stale name is
what lingers. The [continuity-sweep checklist](../checklists/continuity-sweep.md) is the
full method.

## Session-efficiency rules

**What it binds.** The per-turn budget. The rules file attaches to every turn, and so
does everything a session reads and prints, so the spine ends with habits that cap the
tax: grep to locate and read narrow line ranges instead of whole files, never re-read a
file in the same session, cap tool output, end-of-turn summaries of two sentences or
less.

**The failure it prevents.** A session that spends its context window on ceremony:
reading a four-thousand-line file to answer a thirty-line question, narrating every tool
call, then compacting away the one finding that mattered. Efficiency rules are not about
cost alone; a session that reads narrowly keeps more of its window for the work, and the
work is what you are paying for.

**The afternoon version.** Paste the five defaults from the template. They are generic
on purpose; tune them only when your repo proves a different bottleneck.

## How rules earn their place

Every rule in the spine traces to a real failure. That is the test for adding one, and
the test for keeping one.

The strongest spines read like an incident log turned inside out: the rule against
session-named branches carries the date one burned us; the fail-closed rule for feature
flags exists because a flag once failed open; the no-magic-numbers rule exists because
the same threshold, inlined in three places, got updated in two of them. When a rule is
codified after an incident, write the origin into the rule text. A rule with a visible
reason gets followed; a rule with no visible reason gets skimmed past, and skimming is
how spines die.

The deletion test is the same test run backward. On review, ask of each rule: what
failure does this prevent, and can anyone name the time it happened or nearly did? A
rule nobody can trace gets deleted. This is not softness. Untraceable rules are where
spines bloat, and a bloated spine gets skimmed, which costs you the rules that matter.
The rebuild variant of the decisions ledger
([templates/DECISIONS_TEMPLATE.md](../templates/DECISIONS_TEMPLATE.md)) makes the test
mechanical: every day-one rule sits in a table next to the specific past failure it
prevents, and a row with an empty failure column is a rule to cut.

Adopting someone else's spine, including the one in this kit, follows the same logic.
Keep the integrity floor on trust; those failures are universal. Treat the rest as
candidates, and confirm each one against your own failure history as it accrues.

## How the spine is enforced

A rule with no enforcement is a request. The spine stays binding because three
mechanisms back it, and each rule should be routed to the cheapest mechanism that can
hold it.

**CI guards make silent violation impossible.** Any rule that reduces to a detectable
pattern (an inline style block, a raw fetch call, a hardcoded threshold, PII in a
fixture) becomes a guard that fails the build. The guard is the rule; the sentence in
the spine is its documentation. Two disciplines keep guards honest: each guard is proven
to fail against a deliberately-bad fixture, because a guard that never fails is worse
than no guard, and guards do not short-circuit, so an author sees every violation at
once. The [ci-kit](../ci-kit/) in this repo is a working set of seven.

**The merge gate keeps a human on the button.** Whatever the guards miss, a person sees
before it lands, and the fail-closed default means the outcome of anything ambiguous is
"wait," not "merge."

**The ledgers keep failures from being rediscovered.** The issue ledger holds open
problems by number. The decisions ledger holds rulings. And a fixed-do-not-revert list
holds past bugs promoted to invariants, so no future session can helpfully reintroduce
one. Each is append-only in spirit: entries resolve, supersede, or persist; they never
vanish.

Some rules resist all three mechanisms: one concern per PR, name the work not the
session, say the problem before executing. Those are judgment rules, and they are held
by the operator reading PRs with the spine open. Keep them few and sharply worded, and
move everything mechanical into a guard, because every rule a machine holds is attention
the human gets back for the rules only a human can hold.

## Where to start

Copy [templates/CLAUDE_TEMPLATE.md](../templates/CLAUDE_TEMPLATE.md) into your repo
root. Fill the operating tier and the integrity floor first, and stop there for day one;
the other sections earn their way in as the failures they prevent start happening to
you. Keep the whole file lean forever (under about 700 lines, per the template's
adoption notes; it is a tax on every turn). And when you want the wider operating model
the spine plugs into, read
[the agent-ops operating model](../playbook/agent-ops-operating-model.md).

The spine is not documentation, and it is not aspiration. It is the contract every PR is
judged against, and the only part of your judgment still in the room when the next
session starts cold.
