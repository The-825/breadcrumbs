---
description: Work one flaky test - reproduce it N times at zero retries, classify race vs baseline vs env, fix by class, and log the incident in the flake ledger. An unlogged deflake is unfinished.
argument-hint: "<failing spec ref or test title, e.g. e2e/portal.spec.ts:2584 or 'Annual Reports'>"
allowed-tools: Bash, Read, Grep, Edit
---

Deflake **$ARGUMENTS**. A flake is any test that passed on retry in CI or
fails intermittently anywhere. Every incident this command touches gets a
row in the flake ledger (Step 4, see the FLAKE_LEDGER template); an
unlogged deflake is unfinished, and a sighting you are NOT investigating
today still gets an `open` row.

Fill these before first use: `<test-runner-command>` (your runner with
repeat and zero-retry flags) and the ledger path.

## Step 1: reproduce at zero retries

Retries are how flakes hide. The proof bar, both for the reproduction and
later for the fix: N consecutive passes (10 is the production default)
with retries hard-off, plus one full pass of the surrounding suite file.

```
<test-runner-command> --grep "<test title>" --repeat-each=10 --retries=0
```

If it passes 10/10 locally and the flake is CI-only, say so and lean class
`env`.

## Step 2: classify

- **race**: the assertion sampled state before an async load settled
  (lazy imports, fetch-then-render, deferred panel loads).
- **baseline**: a visual or accessibility snapshot diff against a stale or
  wrongly-generated baseline artifact.
- **env**: CI-only timing, resources, ports, or proxy behavior; the test
  logic itself is sound.

## Step 3: fix by class

- **race**: poll for the settled state, never sleep for it. Use your
  suite's polling idiom (`expect.poll`, `waitFor`, an event hook) so the
  assertion waits on the CONDITION, not on a guessed duration; an
  arbitrary sleep is a slower flake. Re-prove at the Step 1 bar after the
  fix.
- **baseline**: regenerate the baseline WHERE CI RENDERS, never locally. A
  locally-rendered baseline is a future flake, because your machine's
  fonts, GPU, and platform differ from the runner's. The clean shape is a
  dispatchable workflow that runs the update pass on CI hardware and opens
  the regen as its own PR.
- **env**: fix the config or infrastructure cause. If it cannot be
  reproduced at all, say so plainly and log the row with the CI run link
  as evidence; never guess a fix into the test.

## Step 4: log the incident

Append a row to the flake ledger (date, test ref, symptom, class, fix PR,
status) in the same PR as the fix; when the fix rides a CI-opened PR
(baseline regens), log the row in its own small docs PR.

End with: repro result (n/N), class, fix applied, ledger row added, and at
most two sentences of summary.
