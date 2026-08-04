# Regression layering

> Part of the companion kit for *From Archivist to Architect* (The Architect's Blueprint, Book 1).

A production incident caused by a typo that a one-second syntax check would have caught is the most expensive possible way to find that typo. The failure this artifact prevents is layer inversion: expensive gates (human review, end-to-end suites, live incidents) catching what a cheap gate should have caught, while the cheap gate does not exist. The principle: catch each class of regression at the lowest layer that can catch it, because low layers run cheaply on every change forever. Paste the ladder into your agent rules file or CI standards doc.

```markdown
## Regression layering rules

1. Catch each class of regression at the LOWEST layer that can catch
   it. The ladder, cheapest first:
   a. Parse-time: syntax checks (`node --check`, a Python compile pass,
      YAML and JSON parsing) and lint guards that grep for banned
      patterns (an inline style block, a raw fetch call, a hardcoded
      threshold).
   b. Unit tests: pure logic. A discount calculator, a date parser, a
      status mapper.
   c. Integration: boot the real app in-process with faked externals
      (database client, auth, third-party APIs) and hit the routes.
      Verifies wiring and behavior, not just syntax.
   d. End-to-end browser tests: what the user actually sees. A handful
      of smoke specs per page, such as "the orders page renders rows
      and the total matches the API".
   e. Data-quality assertions: views that must return zero rows, wired
      into a real run gate. "Zero orders with a negative total", "zero
      signups with a null ID".
2. Every layer runs on every change, forever. A gate you run once is
   manual testing; a gate in CI compounds.
3. When a bug escapes to production, add the check at the LOWEST layer
   that would have caught it, not just a test at the top. If a syntax
   error shipped, the fix is a parse gate, not another e2e spec.
4. A red gate blocks the rollout. A check that can be skipped under
   deadline pressure is decoration.
```

## Adoption notes

Order of construction matters less than people fear. If you have nothing, start at the bottom: parse checks and lint guards take an afternoon to wire and immediately screen every future change. The integration layer is the sleeper. Booting the app with faked externals and sweeping every read route catches an entire class of wiring bugs (a renamed function, a missing import, a broken route registration) that unit tests structurally cannot see and e2e suites catch slowly and expensively.

Rule 3 is the one that keeps the system honest over time. Each escaped bug becomes a permanent gate at the cheapest layer that would have stopped it, which means the ladder is built out of your actual failure history rather than someone's testing philosophy.

Coverage compounds: at fifty specs, every change is regression-tested against all fifty, and the marginal spec is nearly free. The expensive layers should be bored.
