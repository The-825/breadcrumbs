<!-- TEMPLATE. Copy to .github/pull_request_template.md and adapt the example
     lines in the pre-flight block to your own binding rules. Design notes:
     ci-kit/workflows/MERGE_LANE_COMPANIONS.md, "The judgment-only PR template". -->

## Summary

<!-- What changed and why, in a few plain sentences. Lead with the answer. -->

## Versions

<!-- Version strings are CI-stamped, never hand-bumped. Note "n/a" for infra or
     docs PRs that stamp nothing. -->

## Test plan

<!-- The cheapest regression layer that covers this change, and how to run it:
     parse checks, lint guards, in-process harness, unit tests, browser e2e.

     Judgment-only pre-flight (robots cover the rest). Answer in prose where a
     line applies; no "- [ ]" checkboxes. Test-plan items are evidence of what
     already ran, not reviewer TODOs:
     - user-visible feature: its feature flag exists and is seeded default OFF
     - new reporting view: ships through the version-controlled view layer,
       never ad-hoc DDL pasted into a console
     - new feature: adds its own spec to the e2e suite
     - thresholds and limits live in the config registry, never inline literals
     - feature that aggregates across data sources: the source sweep is
       recorded (sources considered, included, excluded, and why)
     - change touches a fact other docs or surfaces cite: the continuity sweep
       ran
     - one coherent concern: split only if the pieces stand alone
     - no TODO comments without a linked issue
-->

## What's NOT in scope

<!-- The scope-discipline line. Name what this PR deliberately does not touch,
     and if it is a large single-concern PR, add "larger PR because: ...". -->
