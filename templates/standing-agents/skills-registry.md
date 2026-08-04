# Skills registry and staleness gate

> Part of the companion kit for *From Archivist to Architect* (The Architect's Blueprint, Book 1).

A command-skill library rots silently: a skill references a file that moved three refactors ago, nobody notices, and the failure surfaces as an agent mid-task following a dead pointer with full confidence. The registry makes the inventory explicit, and the staleness gate makes rot loud: a CI check that exits nonzero the moment the registry and the tree disagree. Use it once your skill library passes about ten files, the point where hand-auditing quietly stops happening. The fleet pieces the gate feeds (the task bus, the desks) are indexed in the [README](README.md).

The registry, one entry per skill, kept as data (the readable table is rendered from it, never hand-edited):

```yaml
skills:
  - name: ship
    path: .claude/commands/ship.md
    purpose: "Commit, verify, push, open the PR"
    references: [".github/workflows/ci.yml", "SESSION_STATE.md"]
    status: ok            # ok | stale | deprecated
    last_verified: <date>
    owner: <who answers for this skill>
```

## The registry pattern

Two files, one truth. The data file (yaml above) is the source of truth: it carries the fields tools need, including every repo path the skill references. The rendered markdown index is for humans and is regenerated on every checker run, with a do-not-hand-edit banner, so the two can never disagree for long. `references` is the load-bearing field: it is what the gate verifies, and the checker re-extracts it from the skill body on each run rather than trusting the stored list, so a skill edit cannot silently orphan it.

Manual fields survive regeneration: `owner`, and a hand-set `deprecated` status. A skill you are sunsetting on purpose is not "stale".

## The staleness gate

The check, in sketch:

```python
# For each skill: re-extract referenced repo paths from the skill body,
# verify each exists in the tree, recompute status. In gate mode, exit
# nonzero only on NEWLY stale skills (stale now, ok in the stored data),
# so known rot files follow-up work instead of blocking every PR forever.
for skill in registry:
    refs = extract_repo_paths(read_text(skill.path))
    skill.missing = [r for r in refs if not exists(r)]
    skill.status = "stale" if skill.missing else "ok"
newly_stale = [s for s in registry if s.status == "stale" and s.was_ok]
write_registry(registry)
render_markdown_index(registry)
sys.exit(1 if gate_mode and newly_stale else 0)
```

The newly-stale distinction is what makes the gate livable. Fresh rot fails the PR that caused it, at the moment the author has full context. Old rot, already recorded in the data file, does not re-block unrelated work; instead the checker files one bus task per stale skill, routed to the desk that owns docs, and the fleet works the backlog.

## Wiring

Run the checker in CI on every PR that touches the skills directory or any path a skill references (running on every PR is also fine; the check is a directory walk, not a network call). Add a scheduled weekly run as a backstop for deletions that arrive outside PRs. Filing tasks needs the bus; until you have one, printing the would-be tasks in the CI log is enough to start.

## Adoption notes

Seed the registry with a one-time init that walks the skills directory and extracts references mechanically; do not type the inventory by hand, it will be wrong by row six. The extractor needs only a conservative heuristic (tokens that look like repo paths under your known top-level directories); false negatives are fine, false positives get pruned once. The gate's whole value is that the registry is maintained by a program and verified by CI, so trust in the library stops depending on anyone's memory.

A skill nobody has verified is a liability wearing a helpful name.
