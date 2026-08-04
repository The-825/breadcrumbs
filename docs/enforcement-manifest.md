# The enforcement manifest: every floor rule names its check

The [rules spine](rules-spine.md) closes on the point that a rule with no enforcement
is a request. The enforcement manifest is that point made machine-readable: one JSON
object per floor rule, binding the rule to its honest enforcement point, checked into
the repo next to the rules it covers. The fill-in version is
[templates/ENFORCEMENT_MANIFEST_TEMPLATE.json](../templates/ENFORCEMENT_MANIFEST_TEMPLATE.json).

## The contract

Each entry carries the rule's text, the zone of the codebase it governs, an
`enforcement` class, a `mechanical_check` pointer, and a `non_delegable` flag. The
enforcement classes are ranked by strength, and every rule gets the strongest class
that actually exists for it:

- **lint**: a universal static guard that sees whole files and fails the build, like
  the guards in [ci-kit/guards/](../ci-kit/guards/). The strongest class, because it
  runs on every PR and cannot be argued with.
- **test**: a dedicated test file that proves the rule holds, like the migration
  policy checks in [ci-kit/migrations/](../ci-kit/migrations/).
- **harness**: behavioral coverage through the real code path on representative
  routes, like the [in-process harness](../templates/test-harness/README.md). Weaker
  than lint because it covers representatives, not the universe, and the entry says so.
- **review**: no viable low-false-positive static check exists. The rule is held by
  human review plus convention, and the entry names a compensating control.

## The honesty convention

`enforcement` is honest, not aspirational. This is the load-bearing discipline. The
easy failure is a manifest that lists every rule as "enforced" by pointing at a check
that does not really cover it; that manifest is worse than none, because it converts a
known gap into a false assurance.

A rule lands in `review` when a static check would drown real hits in false positives.
The classic case is parameterized queries: interpolating trusted constants into query
strings is idiomatic in most codebases, and a grep cannot tell a trusted constant from
user input without taint analysis. Marking that rule `lint` with a naive grep would
either block half the codebase or allowlist itself into uselessness. So the entry says
`review`, explains why in `reason`, and names what compensates: for example, the test
harness records every query configuration so parameter usage is observable in tests,
and the weakly gated zone gets a higher human-audit rate than zones with mechanical
coverage. A named gap with a named control beats a fake green check.

## The non_delegable flag

`non_delegable: true` means an LLM verify never substitutes for the mechanical check.
A model reading a diff and approving it is an opinion; the mechanical gate sees whole
files and has no incentive to be agreeable. The flag matters most in agent-operated
repos, where it is tempting to let a review pass by a second model stand in for a lint
run. For floor rules, it never does: the model pass can run in addition to the gate,
never instead of it. Security and integrity rules should carry the flag by default.

## The coverage gate

The manifest earns its keep when a small lint reads it in CI and fails the build if:

- a rule listed in the rules file's floor section is missing from the manifest,
- a rule's `mechanical_check` points at a file that no longer exists,
- a rule flips to `review` without a non-empty `reason`,
- a rule loses its `non_delegable` flag.

That makes the floor tamper-evident. A refactor that deletes a guard, or a cleanup PR
that quietly downgrades a rule's enforcement, turns the build red instead of passing
silently. The gate itself is a few dozen lines of stdlib Python in the shape of the
[ci-kit guards](../ci-kit/README.md), and like every guard it should be proven to bite:
break the manifest locally, watch it fail, revert.

## Adopting

Copy the template, list your floor rules (start with the three to five from your rules
file's never-decays group), and classify each honestly. Expect at least one `review`
entry; a floor with zero admitted gaps usually means the classification was
aspirational. Then write the coverage gate, wire it into CI next to your other guards,
and treat any future enforcement downgrade as a PR that has to argue for itself.
