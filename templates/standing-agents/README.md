# Standing agents

This directory is the fleet-of-one kit: how one operator runs a fleet of standing specialist agents over one codebase. The failure it prevents is expensive and invisible: every new agent session re-derives the codebase from scratch, burns its context window on unscoped reading, and works without a contract, so quality and cost are both unmanaged. The fix is a small set of durable definitions: a registry of specialist desks with scopes and postures, a fixed read diet per desk, a task contract for every summon, and the plumbing (a task bus, wake routing, a skills registry) that keeps the fleet coherent. Use it when the same kinds of questions keep landing on the same parts of your repo and each one is paying full price.

| File | What it covers |
|---|---|
| [registry.template.json](registry.template.json) | The specialist roster: per-desk scope, posture, fare classes, boot-pack pointer, budget |
| [boot-packs.template.yaml](boot-packs.template.yaml) | Per-desk ordered, budget-capped read playlists: the boot diet, not a suggestion |
| [summon-protocol.md](summon-protocol.md) | The summon flow: commander's-intent task specs, calibrated reports, the harbor-pilot variant |
| [standing-desk-lifecycle.md](standing-desk-lifecycle.md) | Summon vs stand, standing a desk, keeping it honest, retiring it |
| [a2a-task-bus.md](a2a-task-bus.md) | The issue-backed agent-to-agent task bus: verbs, states, leases, reaping |
| [wake-routing.md](wake-routing.md) | Changed paths wake the right desk: the mapping table and router function |
| [skills-registry.md](skills-registry.md) | The skill inventory pattern and the staleness gate that fails CI on rot |
| [routine-prompt.template.md](routine-prompt.template.md) | Fill-in-the-blanks prompt for a scheduled, unattended agent: mode switch, bounded read set, closed write surface, triage posture, plus the post-run guard that enforces it |

## The operating model

A desk is a durable definition, not a resident process. Four artifacts make one specialist: a roster entry in the registry (scope, posture, fare classes), a boot pack (the ordered reads that turn a generalist worker into the specialist), the accumulated conclusions your ledger already keeps for that area, and the summon contract (a commander's-intent task spec in, calibrated language out). Because the definition lives in files, a desk costs nothing between calls, survives any session loss, and gets better every time a conclusion lands in the ledger.

Summoning is the default form: spawn a fresh worker, hand it the pack, hand it the spec. Standing a desk (keeping one warm session serving repeated calls) is the exception you earn with traffic; the lifecycle doc carries the decision rule.

## How the pieces connect

The registry names the desks and their boundaries. Boot packs cap what a summoned desk reads, so booting costs a known budget instead of the whole corpus. The summon protocol makes every call a contract with an acceptance shape. The task bus lets desks hand work to each other without a human relay. Wake routing maps merged file changes to the desks that own them, so the right specialist hears about drift in its territory. The skills registry keeps the command library honest with a CI gate that fails on rot.

Two existing pages pair with this kit: [the doc-sync agent](../../playbook/doc-sync-agent.md) is a worked single instance of a standing agent (one desk, one contract, one cadence), and [the unattended agent contract](../../playbook/unattended-agent-contract.md) is the safety floor for any desk that runs on a schedule with nobody watching. This directory is the generalization to a fleet.

## Adoption order

Start with three artifacts: the registry with two or three desks, one boot pack for your highest-traffic area, and the summon protocol. That alone converts unscoped sessions into scoped, budgeted, contracted ones. A matching slash command ships in [../commands/summon.md](../commands/summon.md) so the resolve-and-assemble step costs one line. Add the lifecycle doc when a desk earns standing traffic. Add the bus, wake routing, and the skills gate as the fleet grows past what one operator can relay by hand.

You are not hiring nine agents. You are writing nine job descriptions any agent can step into cold.
