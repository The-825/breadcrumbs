# Pre-push checklist

> Part of the companion kit for *From Archivist to Architect* (The Architect's Blueprint, Book 1).

"Push then clean up" burns a review cycle and a CI run that a 30-second check prevents. The follow-up commit that fixes the breakage costs more than the breakage: a reviewer re-reads the diff, CI re-runs the suite, and the PR history now carries a fix-the-fix commit forever. Run this before every push, no exceptions for small diffs.

## The checklist

- [ ] **Re-read the full diff.** Not the files you remember editing, the actual `git diff` output. This is where the stray debug line, the half-finished rename, and the accidentally staged file get caught.
- [ ] **Run the cheapest regression layer that covers the change.** A parse check for code, a targeted grep for prose conventions, the unit or integration test that exercises the changed path. Pick from the table below.
- [ ] **Confirm the diff matches the PR's stated scope.** Every changed file should be explainable by the PR's one concern. If a file in the diff surprises you, unstage it or update the scope.
- [ ] **Nothing unrelated snuck in.** Formatting churn in untouched functions, editor artifacts, lockfile noise from an unrelated install. If it is not part of the concern, it does not ship in this PR.

## Cheapest covering check by change type

| Change type | Cheapest check |
|---|---|
| JavaScript | `node --check <file>` on each changed file |
| Python | `python -c "import ast; ast.parse(open('<file>').read())"` or `python -m py_compile <file>` |
| SQL | Dry-run against the engine, or a SQL linter if no dry-run exists |
| Prose (docs, copy) | Grep for your convention bans (banned characters, banned vocabulary, broken links) |
| Config / YAML / JSON | A parse: `python -c "import yaml, sys; yaml.safe_load(open(sys.argv[1]))" <file>` or `jq . <file>` |
| Route or logic change | The unit or integration test that covers that route or function |
| UI change | The smoke spec for that page, if one exists; otherwise load the page once |

The check should take under a minute. If the cheapest covering check for your change takes ten, that is a signal to build a cheaper layer, not to skip the check.

## When you are tempted to skip it

The temptation peaks exactly when the risk peaks: at the end of a fast batch of "obvious" fixes. That is when a one-character typo ships a reference error that breaks a whole page. The fixes felt too small to verify, and each one individually was. The batch was not. After any burst of fast pushes, the cheap insurance is an audit pass over the last several PRs.

Thirty seconds before the push, or thirty minutes after it. There is no third option.
