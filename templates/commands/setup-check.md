---
description: Verify each checkable claim in the repo's setup or onboarding doc against reality - per-claim verdict table, drift filed as a KI ledger entry, never silently fixed from inside the check.
argument-hint: "(no arguments)"
allowed-tools: Bash, Grep, Read, Glob
---

Verify the setup guide against the live repo. Onboarding docs rot faster than any
other doc class, because nothing exercises them between new arrivals; this command is
the exerciser.

Fill these before first use: `<setup-guide>` (the setup or onboarding doc to verify),
`<config-registry>` (the central config file where env vars are registered, if your
rules require one), `<ki-ledger>` (where known issues are logged, per your rules
file's KI convention).

## Step 0: does the guide exist?

If `<setup-guide>` is absent, report exactly "guide not found: nothing to verify" and
stop. This command never creates or seeds the guide.

## Step 1: extract the checkable claims

Read the guide once and collect every claim that can be verified mechanically from
the repo alone. Typical classes:

1. **Env vars**: every env-var name the guide cites.
2. **Files and hooks**: every path the guide references (scripts, hook files,
   config files, directories).
3. **Counts**: any "NN commands / NN checks / NN templates" style figure.
4. **Commands**: every runnable command the guide tells a new arrival to run.

A claim that needs a live service, credentials, or a network probe is out of scope;
list it as `not checkable here` rather than guessing.

## Step 2: verify each claim mechanically

- **Env vars**: the name appears in `<config-registry>` (or wherever your rules say
  env vars register). Absent = drift.
- **Files and hooks**: the path exists on disk (Glob or `ls`). Absent = drift.
- **Counts**: recount the counted thing (`ls | wc -l`, `grep -c`) and compare.
  Mismatch = drift.
- **Commands**: the binary or script exists and, where cheap, `--help` or a dry-run
  exits zero. Failure = drift.

## Step 3: report and route

One verdict table:

| # | Claim (verbatim from the guide) | Class | Verdict | Evidence |

Verdicts: `ok` / `drift` / `not checkable here`. After the table, one line per drift
item naming the fix.

Routing discipline: drift gets FILED, never silently fixed from inside this check.
Log each drift item in `<ki-ledger>` per your rules file's KI format (date found,
evidence, status), then let the fix land as its own small focused PR that cites the
verdict table. Silently editing the guide during verification destroys the audit
trail that says the check ever found anything.
