# Flake ledger

One row per flake incident. The contract that makes this ledger worth
keeping: **a pass-on-retry is a sighting, and every sighting gets a row**,
including the ones nobody investigates that day. Retries exist so one
flake does not block a wave of merges; the ledger exists so the retry
never becomes the fix. A row with status `open` is an honest backlog
entry; a flake that only ever lived in a retried-green CI run is invisible
debt.

Pairs with `templates/commands/deflake.md` (the investigation procedure)
and the CI posture below.

| Date | Test | Symptom | Class | Fix | Status |
|---|---|---|---|---|---|
| YYYY-MM-DD | path/spec.ts:LINE or test title | one line: what failed, where seen | race / baseline / env / unknown | PR # or blank | open / fixed / cannot-reproduce |

Class vocabulary (from the deflake command): `race` (asserted before an
async load settled), `baseline` (snapshot diff against a stale or
locally-rendered baseline), `env` (CI-only timing or infrastructure),
`unknown` (sighted, not yet worked).

## The CI posture that feeds this ledger

Configure the test lane so a passed-on-retry run counts GREEN for the
merge (one flake must not block a wave) but is surfaced as a flake at the
same time: the lane detects that retries were consumed and files or
annotates the sighting instead of letting the green swallow it. Green with
a note beats red with a rerun button, and beats silent green by more. In
the production setup this template comes from, the smoke lane does exactly
that: passed-on-retry is green AND files the flake row.

Two rules that keep the ledger truthful:

- Zero retries locally, retries only in CI. Local runs are where flakes
  get REPRODUCED; retries there would hide the thing you came to see.
- Never regenerate visual or accessibility baselines locally. Baselines
  are rendered where CI renders, via a dispatchable workflow that opens
  its own regen PR; a locally-rendered baseline is the `baseline` class's
  most common cause.
