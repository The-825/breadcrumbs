# Reuse first

The fastest code to maintain is the code you did not write. An agent asked to "add X" will, left alone, write X from scratch even when a helper three files over already does it, because generating is what it does. Multiply that across a year of sessions and the repo grows fifty near-duplicate ways to do one thing, each its own bug surface. The reuse-first ladder makes "does this already exist" the first move, not an afterthought. Paste it into your agent rules file.

```markdown
## Reuse-first ladder (run before writing new code)

Before writing anything new, walk these rungs in order and stop at the first
that answers:

1. Does it already exist? Search the repo for the function, route, query, or
   markup. If it exists, call it. Do not fork it.
2. Is there a composable helper? A shared utility, base class, or mixin you
   can pass new arguments to beats a new implementation.
3. Does the stdlib or an existing dependency do it? Do not hand-roll what a
   library you already ship already solves.
4. Can it be one line at a call site? A small inline beats a new abstraction
   nobody else will find.
5. Only then write the minimum new code, and put it where the NEXT person
   will find it by search.

Never trade the security floor for reuse: parameterize queries, gate auth at
the boundary, flag user-visible changes behind a switch, and never swallow an
error silently, even when reuse would be shorter.
```

## Adoption notes

Rung 1 is the one agents skip, and it is the one that compounds. A thirty-second grep for the thing you are about to build is the cheapest bug prevention in the repo: every re-implementation you avoid is a bug surface you never have to test, a behavior you never have to keep in sync, and a line a reviewer never has to read.

The last paragraph is the guardrail on the guardrail. Reuse-first is an efficiency rule, and efficiency rules must never win against the integrity floor. A shorter path that skips input parameterization or drops an error on the floor is not the minimum, it is a defect wearing a smaller diff.

Codify the pattern once and new work becomes "compose the existing pieces." That is the whole force-multiplier bet: the second time you need a shape, it should already be there.
