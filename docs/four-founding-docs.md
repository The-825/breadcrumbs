# The four founding docs

A rebuild, or any new agent-operated repo, starts with four blank documents. Before the first line of code lands, the repo already knows its rules, its scope, its order, and its reasons. That is the whole meta-pattern: discipline is not something the project grows into, it is the state the project is born in, and four small files are enough to hold it.

The four, with their templates:

1. **The rules spine** · [templates/CLAUDE_TEMPLATE.md](../templates/CLAUDE_TEMPLATE.md)
2. **The build order** · [templates/BLUEPRINT_TEMPLATE.md](../templates/BLUEPRINT_TEMPLATE.md)
3. **The parity contract** · [templates/PARITY_TEMPLATE.md](../templates/PARITY_TEMPLATE.md)
4. **The decisions ledger** · [templates/DECISIONS_TEMPLATE.md](../templates/DECISIONS_TEMPLATE.md)

## What each doc binds

**The rules spine binds behavior.** It is the single source of behavioral truth: the operating tier, the security floor that never decays, the PR conventions, the operator's preferences, the known-issues ledger. Every session, human or agent, reads it before touching anything, and every other doc defers to it on rules. Without it, conventions live in chat history and get re-derived differently each session.

**The build order binds sequence.** Phase by phase, it says what gets built when, what each phase must prove before the next one starts, and which rules gain their enforcement mechanism at each step. Its core claim: the infrastructure floor ships before the first feature, and a later phase does not start until the prior phase's exit criteria are green. Without it, feature pressure sets the order, which is how the last system got built.

**The parity contract binds scope.** Every capability of the system being replaced appears as a row, and nothing counts as done until its row is checked with evidence. It is the difference between "feature parity" as a checkable contract and as a hope. A green-field repo with no predecessor records that fact in one line and moves on; the file earns its place the moment you are replacing anything, because the capability nobody remembered is the regression you will ship.

**The decisions ledger binds memory.** Every durable ruling (a price, a name, a threshold, a policy call) lands here the same turn it is made, append-only, superseded entries kept visible. In its rebuild variant it also carries the founding retrospective: each day-one rule paired with the specific old-system failure it prevents. Without it, decisions get re-litigated, and sometimes reversed by accident.

## How they interlock

They were designed as a set, and the joints matter more than the parts:

- **The build order schedules the spine.** Each phase's "Rules established" section is the moment a spine rule stops being an intention and gains a guard, a gate, or a test. A spine rule with no phase is an aspiration; a phase that establishes no rules is just a task list.
- **The parity contract feeds the build order.** Every parity row back-links to the phase that delivers it. A row with no phase is unscheduled work hiding in plain sight, and a phase whose exit criteria check no rows is unaccountable.
- **The ledger justifies the other three.** The rebuild tables pair each day-one rule with the failure it prevents; if you cannot name the failure, cut the rule. The build order's thesis (invert the old order) is itself a ledger entry with evidence behind it.
- **The spine points at the rest.** Its pointer block names where state, rulings, and settled facts live, so every session loads the whole set, not just the rules.

The interlock is also the maintenance model. Rename a phase and the parity rows repoint. Supersede a ruling and the spine rule it justified gets re-examined. A change in one doc that leaves the others untouched is usually a change that is not finished.

## The order to write them

1. **Open the ledger first.** It costs a minute: the header contract and entry D-1, the decision to do this at all. Every choice you make while writing the other three docs is a ruling, and rulings land the turn they happen, so the ledger has to exist before the choices start.
2. **Write the rules spine second.** If this is a rebuild, the ledger's rebuild tables are your retrospective, and their left column is the draft rule list; number the rules and group them so the floor is visible. If it is green-field, start from the template's floor and cut what does not apply.
3. **Fill the parity contract third.** Walk the old system bucket by bucket before designing anything. The inventory is the honest size of the job; a build order written before it is a guess.
4. **Write the build order last.** It has to come last, because it sequences the other two: the spine's rules land phase by phase, and the parity rows get their phase assignments here.

Why, what binds, what exists, then when. Each doc is an input to the next.

## The smallest honest version

None of this requires a planning offsite. The day-one versions are small:

- **Ledger:** the header contract plus D-1 with its one-line why.
- **Spine:** one page. The operating-tier line, three or four security-floor rules, the PR shape, the pointer block. Everything else accretes as it earns its place.
- **Parity:** every bucket heading with real rows, even where a bucket honestly records "none." An empty bucket is a claim you checked; a missing bucket is a blind spot.
- **Build order:** the phase list with one-line exit criteria each. Deliverables can grow later; the gates cannot be added retroactively, because by then something has already crossed them.

Three or four pages total, one sitting. Repos that add these files after the code treat them as documentation, and documentation drifts. Repos that start with them treat them as law, and the code grows up inside it.

For the flat checklist version of what day one should establish, see [day-one-mandates.md](day-one-mandates.md).
