# Templates

Copy-paste starting points for the working files an agent-assisted repo needs. To adopt one: copy the file, fill the angle-bracket placeholders, delete what does not apply, and commit it to your repo root or docs directory. Each template's intro explains the failure it prevents, so read that before deciding whether you need it.

| File | What it is |
|---|---|
| [CLAUDE_TEMPLATE.md](CLAUDE_TEMPLATE.md) | Starter rules file for any agent-assisted repo: operating tier, binding rules, PR conventions, known-issues ledger |
| [SESSION_STATE_TEMPLATE.md](SESSION_STATE_TEMPLATE.md) | The living handoff file, refreshed on "checkpoint", so a new session picks up mid-flight |
| [FLAKE_LEDGER_TEMPLATE.md](FLAKE_LEDGER_TEMPLATE.md) | One row per flake sighting, pass-on-retry included; pairs with the deflake command and the retries-green-but-filed CI posture. |
| [DECISIONS_TEMPLATE.md](DECISIONS_TEMPLATE.md) | Append-only decisions ledger: durable rulings captured the turn they land, plus the rebuild variant pairing each day-one decision with the failure it prevents |
| [CONCLUSIONS_TEMPLATE.md](CONCLUSIONS_TEMPLATE.md) | JSONL store of settled facts, keyed by path, read at session start so knowledge survives sessions |
| [PARITY_TEMPLATE.md](PARITY_TEMPLATE.md) | Zero-regression parity inventory for a rebuild or migration, bucketed and checked with evidence |
| [ADR_TEMPLATE.md](ADR_TEMPLATE.md) | One-page architecture decision records, framed for data platforms, with a filled example |
| [BLUEPRINT_TEMPLATE.md](BLUEPRINT_TEMPLATE.md) | Phased build order for a disciplined rebuild: floor before features, exit criteria per phase, every old retrofit converted to a day-one rule |
| [AGENT_PREAMBLE_TEMPLATE.md](AGENT_PREAMBLE_TEMPLATE.md) | Numbered binding blocks that every skill, command, and spawned-agent prompt references instead of restating, so rule wording never forks |
| [INCIDENT_TEMPLATE.md](INCIDENT_TEMPLATE.md) | Incident postmortem format whose load-bearing section is misdiagnosis lessons: where the diagnosis went wrong and what check would have caught it sooner |
| [MECHANICAL_FACTS_TEMPLATE.md](MECHANICAL_FACTS_TEMPLATE.md) | One regenerated home for rot-prone counts, so prose points at the numbers instead of restating figures that drift |
| [AUTHORITY_LEDGER_TEMPLATE.md](AUTHORITY_LEDGER_TEMPLATE.md) | Append-only JSONL record of standing permission grants, the permissions sibling of the conclusions store; pairs with [authority_ledger.jsonl](authority_ledger.jsonl), the ready-to-copy starter |
| [ENFORCEMENT_MANIFEST_TEMPLATE.json](ENFORCEMENT_MANIFEST_TEMPLATE.json) | One JSON object per floor rule, bound to its honest enforcement point, with the non-delegable flag; the contract is explained in [docs/enforcement-manifest.md](../docs/enforcement-manifest.md) |
| [commands/](commands/README.md) | Copy-paste slash-command definitions for Claude Code, each a markdown file with frontmatter; its README carries the install steps and the full table |
| [test-harness/](test-harness/README.md) | In-process test harness skeleton: boot the real app, fake only the edges, prove route behavior on every PR in seconds |
| [ledger-tools/](ledger-tools/README.md) | Tools that keep a long-lived conclusions ledger trustworthy: provenance tiers, a staleness auditor, the capture nudge, union-merge hygiene |
| [standing-agents/](standing-agents/README.md) | The fleet-of-one kit: specialist registry, boot packs, summon protocol, desk lifecycle, task bus, wake routing, skills registry |
| [hooks/](hooks/README.md) | Harness-side hooks: the window-aware batch-cadence stop hook plus the pre/post-compaction pair |

The templates reference each other (the rules file points at the state file, the ledger, and the conclusions store). They work fine alone, but they were designed as a set.

CONCLUSIONS_TEMPLATE.md pairs with [conclusions.jsonl](conclusions.jsonl), a ready-to-copy starter store, and the same-turn capture practice behind the ledger and the store is written up in [docs/decision-capture.md](../docs/decision-capture.md).
