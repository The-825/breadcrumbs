# Blueprint template: the phased build order

A rebuild is worth doing only if you invert the original build order. The old system built features first and poured the floor later: tests, flags, config, typed loading, and module boundaries all arrived as retrofits, each one paid for at retrofit prices while the features it should have carried fought it. The blueprint flips that. Every retrofit the last system needed becomes a day-one rule here, and the phases below are the schedule on which each rule stops being an intention and becomes enforced reality.

Two structural commitments make the inversion real:

1. **The infrastructure floor ships before the first feature.** Founding docs, CI, the auth skeleton, feature flags, the module shell, and typed ingestion are all live and gated before any user sees anything new. Phases 0 through 3 are that floor.
2. **The hard gate: a later phase does not start until the prior phase's exit criteria are all green.** Not mostly green. The urge to start features while the floor is half-poured is the exact force that built the old system, and the gate is where the inversion survives contact with that urge.

Evidence that this order holds up, anonymized from one real production rebuild that ran this template: the first eleven PRs were all infrastructure (docs, guards, harness, migration runner, app skeleton), and the first user-visible feature landed as PR twelve, composed from the floor in an afternoon. The merge history is the receipt. You can point at the exact PR where the floor ended and the features began, and every feature PR after it stays small because it composes instead of inventing.

## How to use this template

1. Copy the block below into your repo root as `BLUEPRINT.md`.
2. Fill the angle-bracket placeholders. Everything in angle brackets is a domain slot; this template ships with no domain content on purpose.
3. Write Phase 4 yourself. It is your data spine, and no template can know it.
4. List your own features in Phases 5 and 6. The list is yours; the per-feature composition recipe is not negotiable.
5. Wire the blueprint to its siblings: each phase's exit criteria should be checkable against your parity inventory ([PARITY_TEMPLATE.md](PARITY_TEMPLATE.md)), each "Rules established" list should name rules that live in your rules spine ([CLAUDE_TEMPLATE.md](CLAUDE_TEMPLATE.md)), and the reasoning behind the day-one rules belongs in your decisions ledger ([DECISIONS_TEMPLATE.md](DECISIONS_TEMPLATE.md)).

## The template

```markdown
# BLUEPRINT.md · build order for <rebuild-name>

This rebuild inverts <old-system>'s build order: the floor first, the data spine
second, features last, composed on the patterns. Every retrofit <old-system>
needed is a day-one rule here.

**The gate:** a phase does not start until the prior phase's exit criteria are
ALL green. Feature pressure does not move the gate; it is the reason the gate
exists.

---

## Phase 0 · Founding docs and the CI floor

The repo can enforce its own rules before it holds anything worth ruling on.

**Deliverables**
- The four founding docs, committed with structure even where content is thin:
  the rules spine (`CLAUDE.md`), this build order, the parity inventory
  (`PARITY.md`), the decisions ledger (`DECISIONS.md`).
- A CI workflow gating every PR: parse checks plus lint guards.
- Each lint guard parameterized for this stack, with one deliberately-bad
  fixture and one clean fixture.
- The migration runner (refuses duplicate numbers and out-of-order apply) and
  an ADR directory holding the ADR template.
- Branch and PR conventions live: feature-slug branches, intent-tagged titles,
  the description template with a "What's NOT in scope" section.

**Exit criteria**
- Every lint guard is proven to FAIL its deliberately-bad fixture and pass its
  clean one. A guard that has never failed anything is not a guard.
- A test PR goes red on a planted violation and green once it is fixed.
- The parity inventory has a row for every capability of <old-system>, all
  buckets walked, "none" recorded where true.
- The decisions ledger carries its founding entries: the decision to rebuild,
  and the day-one rules paired with the old-system failures they prevent.

**Rules established**
- Every PR is judged against the rules spine, starting with PR #1.
- No convention without a guard or a gate where one is possible.
- A ruling is captured in the ledger the same turn it lands.

---

## Phase 1 · Application skeleton

The shape of the app before any behavior: modules, auth, config, flags, and the
harness that proves them.

**Deliverables**
- App factory plus per-area route modules plus shared helpers. There is no
  single-file era, not even briefly.
- Auth at the boundary: one grep-auditable caller-resolution helper, and a
  placeholder route living behind it.
- The central config registry: one frozen structure; every env var and every
  threshold enters the codebase through it.
- The feature-flag store, fail-closed, with its loader and short-TTL cache.
  Flags live here and nowhere else.
- The API contract stub, so the spec exists from the first route.
- The in-process test harness: boots the real app factory with only the I/O
  edges faked (external clients, the data store, auth headers, the flag store).

**Exit criteria**
- The harness boots the real app in CI.
- An unauthenticated request to the placeholder route gets a real 401/403
  through the real auth path.
- A test proves flags fail closed: a flag-store error reads as OFF.
- The env-read guard is green: zero reads outside the config registry.

**Rules established**
- Auth at the boundary, every time.
- No magic numbers; every threshold lives in the config registry.
- Every user-visible feature ships behind a flag, default OFF in production.
- Tests exercise the real app; never mock your own functions.

---

## Phase 2 · Typed ingestion

Data enters typed, watermarked, and quarantined before anything consumes it.

**Deliverables**
- One ingestion path per source (<source-A>, <source-B>, ...) with an explicit
  type map. No schema autodetect anywhere.
- Incremental sync on a watermark field verified reliable, with sync state
  recorded for audit.
- An ingest-time quarantine: a load whose null rates or row counts degrade past
  <threshold> is refused, not written.

**Exit criteria**
- One real source lands end-to-end typed, on schedule.
- A deliberately degraded fixture load is refused by the quarantine.
- Re-running a load is idempotent; row counts hold stable.

**Rules established**
- Typed ingestion only; autodetect is banned.
- Watermark fields are proven reliable before they are trusted.
- A canonical store is never rebuilt from a side snapshot or spreadsheet.

---

## Phase 3 · View layer and data-quality gates

Every consumer-facing number comes from a version-controlled view, and the
views are tested.

**Deliverables**
- Version-controlled view definitions, one file per view, deployed from the
  repo. Views are never hand-edited in a console.
- Data-quality assertions (queries that must return zero rows) wired into a
  gate that actually runs, not one that only compiles.
- The canonical filters of the domain (<active-record-filter>, ...) encoded
  once, in views, never re-derived per query.

**Exit criteria**
- Views deploy from the repo through the gate.
- A deliberately-bad assertion fixture blocks the gate.
- No consumer reads a raw table where a canonical view exists.

**Rules established**
- Views are code: reviewed, versioned, deployed.
- Assertions run on every change, forever.
- One canonical definition per business filter.

---

## Phase 4 · The domain data spine <your-data-spine>

The canonical stores and lifecycle model of your domain. This phase is
deliberately blank in the template: it is all domain, and yours will not look
like anyone else's. Design it on paper before the DDL.

**Deliverables**
- <canonical-store>: the master record tables, with the status vocabulary and
  lifecycle transitions written down before any DDL runs.
- <lifecycle-model>: soft-delete recoverability (dated marker columns, default
  filters), so no record the process depends on can become unrecoverable.
- <identity-resolution>: how records from <source-A> and <source-B> resolve to
  one canonical key before anything compares them.
- Migration files for all of it, applied through the runner.

**Exit criteria**
- A round-trip test passes: a record enters via ingestion, moves through each
  lifecycle state, and stays queryable after archival.
- The parity rows covering <old-system>'s data model are checked or scheduled
  to a later phase.

**Rules established**
- Migrations are forward-only.
- Soft-delete for records the process depends on.
- One writer per field; resolver-owned columns are excluded from bulk upserts.

---

## Phase 5 · Feature composition, first wave

Features begin, and every one is a composition of the floor, not a snowflake.

**The per-feature recipe (binding for this phase and every phase after):**
each feature ships as

1. a route behind the auth boundary,
2. behind a feature flag, default OFF in production,
3. reading a version-controlled view, never a raw table,
4. rendered by a component composed from the shared library,
5. with at least one end-to-end test spec,
6. with an API-contract entry,
7. with its parity inventory rows checked, evidence recorded.

**Deliverables**
- <feature-1>, per the recipe.
- <feature-2>, per the recipe.
- <feature-3>, per the recipe.

**Exit criteria**
- Every shipped feature passes all seven recipe items.
- The parity rollup shows this wave's rows done.
- No feature merged with its flag defaulted ON.

**Rules established**
- The recipe is the definition of "feature." A change that skips an item is
  not a feature; it is debt arriving early.

---

## Phase 6 · Parity close-out and cutover

The rebuild earns the word "done": every parity row resolved, then the old
system retires.

**Deliverables**
- The remaining feature waves, same recipe.
- Side-by-side verification: the figures both systems report
  (<key-figure-1>, <key-figure-2>, ...) compared and reconciled.
- The cutover plan with a rollback path, and the decommission list for
  <old-system>'s jobs, services, and integrations.

**Exit criteria**
- Parity rollup: every row done with evidence, or recorded DROPPED with an
  approval. Nothing in between.
- Old and new agree on every shared figure, or the difference is explained in
  writing and accepted.
- Operator sign-off on cutover, recorded in the decisions ledger.

**Rules established**
- Nothing is decommissioned until its replacement's parity row carries
  evidence.
- Deferred and dropped are recorded statuses, never silent omissions.
```

## Adoption notes

Resist two failure modes. The first is starting Phase 5 early because the floor "mostly works": that is the old system's origin story, replayed. The second is padding phases to feel thorough: exit criteria you cannot check are theater, so keep each one observable (a passing test, a red fixture, a checked row, a recorded sign-off).

The phases are a schedule for rules, not just for code. Read each "Rules established" list as the moment that rule gains an enforcement mechanism; before its phase, it is a plan, and after, breaking it should require deliberate effort. If a rule in your spine never gets a phase, either find its phase or question the rule.
