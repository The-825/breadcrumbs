# PR discipline checklist

> Part of the companion kit for *From Archivist to Architect* (The Architect's Blueprint, Book 1).

The failure this prevents: a 2,000-line PR that mixes a refactor with a feature, sits unreviewed for a week, and cannot be reverted without taking both down. Its cousin fails the same way from the other direction, a flurry of one-line PRs that chop a single concern into fragments nobody can review as a whole. Run this checklist before you open any PR.

## Before you open the PR

### Shape

- [ ] **One coherent concern.** This PR ships infrastructure OR a user-visible improvement, never both. Force-multiplier work buried inside a feature diff gets no review and no credit; a feature buried inside a refactor cannot be reverted alone.
- [ ] **The ~500-line question.** If the diff passed ~500 changed lines, stop and ask: can this split into PRs that each stand on their own, independently reviewable, mergeable, and revertable? If yes, split. If no (a self-contained module, generated code, a pure refactor), ship it whole and add one line to the scope block: "larger PR because: ..."
- [ ] **Not artificially chopped.** The inverse check. Related changes that only make sense together land together. A single concern split into five one-line PRs is the same anti-pattern as the mega-PR. The goal is reviewability and one coherent concern, never a line count for its own sake.

### Naming

- [ ] **Intent-tagged title.** One of `feat:` / `fix:` / `docs:` / `chore:` / `refactor:` / `test:` / `ci:`, followed by what changed. The title names the work, not the session. `feat: order export to CSV`, never `session updates 2026-07-18`.
- [ ] **Feature-slug branch.** The branch is slugged after the same work the title names (for example `agent/order-export`). Never push an auto-generated or session-named branch to the remote. If your tooling pinned you to one, cut the feature branch now, before the first push.

### Body

- [ ] **Summary.** What changed and why, two to four sentences.
- [ ] **Test plan.** The checks you actually ran, named specifically. "Ran the parse check and the order-export unit tests," not "tested locally."
- [ ] **What's NOT in scope.** The section that does the real work. Writing it forces you to notice everything that snuck in. If you cannot write this section honestly, the PR has a scope problem; fix the diff, not the description.

Add a Versions line if your repo CI-stamps versions; the fuller body template with that section is [ci-kit/pull_request_template.md](../ci-kit/pull_request_template.md).

## Why the last section matters

Summary and test plan describe what is there. The not-in-scope section is the only part that makes you account for what should not be. Every scope-creep incident survives the first two sections and dies at the third, because you cannot list "unrelated config change" as out of scope while it sits in the diff.

A PR that passes all eight boxes gets reviewed fast, merges clean, and reverts clean. That is the entire point.
