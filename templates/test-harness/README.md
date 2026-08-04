# In-process test harness

> Part of the companion kit for *From Archivist to Architect* (The Architect's Blueprint, Book 1).

Boot the real app in your test process, fake only the edges, and prove route behavior
on every PR in seconds.

## The pattern

Catch regressions at the lowest layer that can catch them. A parse check proves a file
compiles. A deployed-environment check proves the whole stack works, but it is slow,
needs credentials, and runs late. Between those two sits a layer most teams skip: prove
that the real routes behave (the auth gate fires, the right query runs, the response
takes its shape) with no network, no credentials, and no deployed environment.

An in-process harness closes that layer. It boots the REAL app, the actual route table
and gate logic, and fakes exactly three external seams:

1. **The data client.** A fake that records every query and returns canned rows you seed
   per test. Unmatched queries return an empty list, never a loose mock object, so code
   that mishandles an empty result fails loudly instead of passing by accident.
2. **The auth resolver.** A stub that returns one fixed synthetic caller when the request
   carries the auth header, and nothing when it does not. The app's own gate logic still
   runs, so a request with no header exercises the real 401 branch, not a shortcut.
3. **The flag store.** Forced to a known state: every flag OFF unless a test turns it on.
   That default doubles as the fail-closed proof, the branch that must run when the flag
   system has no answer.

Do not mock your own functions. If a test replaces the code it claims to test, it proves
nothing. Fake the external collaborators, run everything else for real.

Because the suite touches no I/O, it finishes in well under a second and runs in CI on
every PR, forever.

## What is in this directory

| File | What it is |
|---|---|
| `harness.py` | The generic harness: `FakeDataClient` (pattern-to-rows router, records queries), the stub auth resolver, `FakeFlagStore` (OFF by default), and a `Harness` exposing `get(path)` / `post(path, body)` |
| `app_example.py` | A tiny synthetic inventory app with the three seams visible: one public health route, one auth-gated data route, one flag-gated route |
| `test_routes_example.py` | The proof tests: boot the app through the harness and assert real route behavior |

Run it (stdlib only, nothing to install):

```
cd templates/test-harness
python3 -m unittest discover
```

## Adapting it to a real app

The example app is scaffolding you replace; the harness classes and the test shapes are
the part you keep. The work is finding the three seams in your codebase and cutting them
cleanly:

- **Data client seam.** Find the one shared client object (or query helper) that all
  route code calls, and point its query method at `FakeDataClient.query` before the
  first request. If routes construct their own clients inline, that is the first
  refactor: one shared client, bound once, is what makes the seam patchable. Seed
  fixtures per test with `seed(pattern, rows)`; assert the route really queried with
  `ran(pattern)`.
- **Auth resolver seam.** Identify the single function that turns a request into a
  caller (reading your platform's authenticated-user header, verifying a token, looking
  the caller up in a directory). Replace that function, not the gate that calls it. The
  gate must stay real so the rejected path is genuinely exercised.
- **Flag store seam.** Replace the flag lookup with a per-test store whose default
  answer is OFF. Turning a flag on is an explicit test action, and the untouched default
  is your standing proof that flag-gated routes fail closed.

If your app is a framework app (Flask, FastAPI, Express), keep the same shape: import
the real app factory in the test process, install the three fakes before the first
request, and drive it with the framework's built-in test client instead of the plain one
here. When the app constructs cloud SDK clients at import time, stub those modules in
`sys.modules` before importing the app so the import itself needs no credentials. This
directory stays dependency-free on purpose, so the skeleton runs anywhere Python runs
and your CI needs no install step to keep the layer green.

Ground rules that keep the harness honest:

- Fixtures are synthetic by construction. Placeholder emails on `example.com`,
  identifiers shaped nothing like your production ones, no rows copied from a real
  store. Pair this with a CI guard that scans fixture files for PII-shaped tokens.
- One harness per test. Fresh fakes each time means no cross-test bleed through shared
  caches or recorded queries.
- The default for anything unseeded is the empty, closed, or rejected state. Tests earn
  the open state explicitly.

## What this layer does not cover

The harness proves route behavior against faked data. It cannot prove things about the
data itself or about the rendered product. Cover those layers with their own tools:

- **Data integrity.** Whether real rows obey the rules (keys present, values in range,
  no orphans) is a warehouse-layer question. Write assertion queries that must return
  zero rows, in whatever your view tooling supports, and run them on schedule.
- **End-to-end behavior.** Whether the shipped page actually works in a browser (markup,
  script wiring, the full request path) needs a browser-driving suite such as Playwright
  against a running instance.
- **Pure business logic.** Functions with no I/O deserve plain unit tests. Cheaper than
  the harness, and they pin the logic at the lowest possible layer.

One layer per failure class, each running on every PR. The harness is the middle rung,
not the whole ladder.
