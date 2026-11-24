# Security policy

A flaw in a merge gate, a guard or a workflow template here can spread to every
repo that copied it. If you find one, report it privately so it can be fixed
before it is described in public.

## How to report

Use GitHub's private reporting: open the
[Security tab](https://github.com/The-825/breadcrumbs/security) and choose
**Report a vulnerability**. Only the maintainer sees the report.

Please do not open a public issue or pull request for a security problem.

Include what you can:

- The file and, if you know it, the commit you looked at.
- What an attacker or a careless PR could do, step by step.
- Whether you have seen it happen or reasoned it out.

## What counts

In scope, because people copy these into their own repos:

- `ci-kit/workflows/`: the automerge gate, the greenlight companions, the
  sync workflow, and the decision scripts behind them. For example, a way to
  merge without the approval label, to run a PR's own code with write
  permissions, or to reach a secret.
- `ci-kit/guards/`: a guard that passes content it claims to block, such as
  the PII guard missing a pattern it documents.
- `.github/workflows/` in this repo, for the same reasons.
- `templates/hooks/` and any shipped script that reads or writes files.

Out of scope: prose disagreements, the research archive, and anything in the
Pages site that does not run code. Open a normal issue for those.

## What to expect

This is a one-maintainer project, so there is no response-time promise. A
confirmed report gets a fix on `main`, a note in `planning/DECISIONS.md` when
it changes a shipped contract, and credit in the fix if you want it.

Fixes land on `main` only. There are no release branches, so update your copy
from `main` or re-run the sync workflow
([`ci-kit/workflows/sync-app-setup.md`](ci-kit/workflows/sync-app-setup.md))
to pick a fix up.
