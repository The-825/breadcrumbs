# Adoption verifier

> Pairs with [docs/day-one-mandates.md](../docs/day-one-mandates.md).

A rules file makes claims about its own repo: "env vars live in the config registry", "the deploy workflow is deploy.yml", "these connectors are wired", "there are twenty-four skills". Every one of those can rot, and a rules file that lies is worse than none, because an agent trusts it. This is doubly true when you COPY a kit like this one into your repo: the templates ship with placeholder paths and names you are meant to edit, and a missed edit is a silently mis-wired repo that passes every test until the day it does not. The adoption verifier is the check that a rules doc's claims still match reality. Paste it in as a periodic skill, and run it the moment you finish copying the kit in.

```markdown
## Adoption / setup verifier

Verify the rules doc against the live repo. For each claim, produce a
per-claim verdict (holds / drifted / missing). FILE the drift; never
silently edit the doc to match a broken repo, and never silently edit the
repo to match the doc. A human rules on each mismatch.

Check, at minimum:
1. Config claims. Every env var the rules name exists in the config
   registry the rules point to, and nothing reads an unlisted var elsewhere.
2. Path claims. Every file, workflow, script, and ledger the rules cite by
   path exists on disk at that path.
3. Hook claims. Every hook the rules say fires is present in the settings
   file and points at a script that exists.
4. Connector claims. Every named integration or MCP the rules assume is
   actually reachable in the session, or the claim is marked optional.
5. Count claims. Any number the rules state (skills, agents, endpoints,
   guards) matches a live count, or is replaced by a generated figure so it
   cannot go stale.
6. Copied-kit placeholders. After copying a kit in, every placeholder path,
   check name, label name, and ledger location has been edited to this
   repo's real values. A leftover placeholder is a finding.

Output a verdict table. Drift becomes a filed issue or a known-issues entry,
ranked; it is not fixed silently in the same pass that found it.
```

## Adoption notes

The discipline that makes this safe is "file, do not silently fix." A verifier that quietly edits the doc to match the repo papers over a real regression (the repo lost a hook, and now the doc pretends it never had one). A verifier that quietly edits the repo to match the doc "restores" something a human deliberately removed. Both are the same error: acting on a mismatch without a human ruling on which side is right.

Rung 6 is the one that pays for the whole skill when you adopt a kit. The templates here ship with names you are meant to point at your own repo. A missed edit does not fail loudly; it fails the first time a workflow runs against a path that is not there. The verifier turns that into a finding at copy time, not a broken run three weeks later.

The companion to this skill is a `doctor` script in the CI kit that automates the mechanical rungs (paths, hooks, placeholders) and runs on every PR. The skill is the human-and-agent checklist; the script is the machine floor. Roadmap item, tracked in `planning/ROADMAP.md`.
