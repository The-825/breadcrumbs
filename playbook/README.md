# Playbook

This directory holds the connective essays: how the pieces of the kit fit together and why the patterns exist. The copy-paste artifacts themselves live in `ci-kit/`, `skills/`, `templates/`, and `checklists/`.

| File | What it is |
|---|---|
| [agent-ops-operating-model.md](agent-ops-operating-model.md) | The capstone essay: the six commitments that keep agent-assisted development from drifting, plus the adopt-in-this-order sequence for the whole kit. |
| [doc-sync-agent.md](doc-sync-agent.md) | The doc-sync agent pattern: a merge-gated workflow plus a hard-contract prompt that keep README, CHANGELOG, runbook, and roadmap aligned with the code when the bus factor is one. |
| [scheduled-agents.md](scheduled-agents.md) | The scheduled headless agent family: the self-healing janitor, the overnight sweeper, and the weekly triage router, plus the draft-only safety posture they share. |
| [unattended-agent-contract.md](unattended-agent-contract.md) | The five controls every scheduled, no-human-in-the-loop agent needs: a mode switch, a write surface enforced outside the prompt, a bounded read set, degrade-do-not-hard-fail, and a triage-only posture. |
| [coordinator-seat-model.md](coordinator-seat-model.md) | One warm coordinator session plus a roster of cold, on-demand seats that re-adopt identity from a charter file on wake, so a standing team of agents stays coherent across weeks. |
| [scout-discover.md](scout-discover.md) | Autonomous discovery scouting: rotating lanes generate candidates cheaply, a persistent digest dedupes, and only the top few earn an expensive deep evaluation. Read-only; acting on findings stays human. |
