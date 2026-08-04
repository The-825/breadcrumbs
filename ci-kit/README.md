# CI kit

> Part of the companion kit for *From Archivist to Architect* (The Architect's Blueprint, Book 1).

The failure this kit prevents: an agent-written PR that quietly breaks an invariant no
human re-checked, a raw view definition outside the versioned layer, a duplicate
migration number, a merge nobody actually approved. Everything here is runnable
enforcement, not advice: copy it into your repo, adapt the parameters at the top of each
file, and the invariants hold on every PR from then on. Adopt it at commit one if you
can ([docs/day-one-mandates.md](../docs/day-one-mandates.md), mandate 1); a gate added
late launches with grandfathered violations to burn down.

## What's in the kit

| Piece | What it is |
|---|---|
| [guards/](guards/) | Six parameterized lint guards (inline style/script, env-var registry, raw fetch, magic limits, raw CREATE VIEW, PII in fixtures), each proven by must-fail and must-pass fixtures under `guards/tests/`. The PII guard also ships a `--stdin` mode so a pre-push git guard and a PreToolUse outbound hook can share its detector instead of each growing their own; see `../templates/hooks/outbound-pii-screen.md`. |
| [migrations/](migrations/README.md) | The migration runner (numbering integrity plus the applied ledger) and the merge-time policy checks, with tests. Its README carries the claim-first ledger rule. |
| [workflows/](workflows/) | The fail-closed automerge gate (`automerge.yml`) with its extracted decision script and tests, the merge-lane companion workflows, and two pattern docs: [AUTOMERGE_GOTCHAS.md](workflows/AUTOMERGE_GOTCHAS.md) and [MERGE_LANE_COMPANIONS.md](workflows/MERGE_LANE_COMPANIONS.md). |
| [run_guards.sh](run_guards.sh) | The aggregate gate your checks workflow calls: every guard in one pass, all violations reported at once, no short-circuit. |
| [pull_request_template.md](pull_request_template.md) | The judgment-only PR body template (Summary / Versions / Test plan / What's NOT in scope); copy it to `.github/`. |

## Run it

```bash
./ci-kit/run_guards.sh   # every guard over the repo, all findings in one pass
python3 -m unittest discover -s ci-kit/guards/tests   # the self-tests that prove each guard bites; same form for migrations/tests and workflows/tests
```

Each piece stands alone; the table rows point at the file that explains it. Nothing in
this README is the source of truth for how a piece works.
