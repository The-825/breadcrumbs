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

If your change touches the kit, run its self-tests before opening the PR:

    python3 -m unittest discover -s ci-kit/guards/tests
    python3 -m unittest discover -s ci-kit/migrations/tests
    python3 -m unittest discover -s ci-kit/workflows/tests

Three green suites locally is the same bar CI holds.

Everything here is MIT licensed (see [LICENSE](LICENSE)); contributions land
under the same terms.
