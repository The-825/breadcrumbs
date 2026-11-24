# Contributing

This repo tracks the book, so the author curates it. That is not a keep-out sign.
It means the shape of the thing is not up for committee, and the fastest way to
help depends on the size of what you found.

Small stuff, straight to a PR: typos, broken links, dead anchors, a command that
does not run as written. These land fast.

Substantive stuff, issue first: new templates, guard changes, restructuring,
whole new docs. Pitch it in an issue before writing it, so the work does not die
in review over a direction call.

The bar for prose is the repo's own style: no em-dashes, no filler, intros that
lead with the failure the piece prevents. Read a page or two of `docs/` first
and match what you see.

If your change touches the kit, run its checks before opening the PR. Python 3.9 or
newer and the standard library are enough; Node is only needed for the intake
example.

    bash ci-kit/run_guards.sh
    python3 ci-kit/kit_manifest_check.py --run-selftests

The first runs every guard over the tree. The second runs every selftest listed in
`kit.json`. Both green locally covers most of what CI checks; the full list is in
`.github/workflows/ci.yml`.

Everything here is MIT licensed (see [LICENSE](LICENSE)); contributions land
under the same terms.
