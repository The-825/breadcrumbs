# Data truth rules

> Part of the companion kit for *From Archivist to Architect* (The Architect's Blueprint, Book 1).

The most dangerous number in any report is the one that quietly disagrees with the dashboard leadership already reads. Hand-rolled counts, misread blanks, and form data trusted over behavior all produce figures that look right and are wrong. These four rules are the standing defense. Paste them into your agent rules file or your team's analytics handbook.

```markdown
## Data truth rules

1. Blank is not missing. Many fields are presence-flags (blank means
   "No") or categoricals (blank is a real category). Check the data
   dictionary or run a value-distribution query before calling any
   field sparse.
2. What a form says is not what behavior verifies. A "yes" recorded at
   intake is confirmed by the behavioral record downstream, and silent
   "no"s never get recorded at all. Reconcile through the behavioral
   source.
3. Source-of-truth-first aggregation. Before reporting any figure, find
   the canonical query or endpoint that already computes it and mirror
   that logic. Raw tables verify, never originate.
4. Source-inventory sweep. Any feature that aggregates across sources
   starts with a documented sweep of every candidate source, with an
   explicit include or exclude decision per source.
```

## Rule 1: blank is not missing

An analyst reviewing a membership program's roster flags the paperless-billing column as "80 percent missing" and proposes a data-quality cleanup. Nothing is missing. The field is a presence-flag: the signup form only writes a value when the member opted in, so blank means "No". A plan-type column can behave the same way, where blank is the default plan, a real category holding most of the population. Encode the semantics (presence-flag, categorical, or genuinely nullable) in the data dictionary at schema time, and never call a field sparse without checking there first or running a value-distribution query.

## Rule 2: signup is not activation

A membership program records acceptances on a signup form. The form is accept-only, so a member who quietly walks away leaves no record; the "no" is silent. Quote signup counts as membership and the figure inflates every period. The behavioral verifier of a real member is appearance in the next period's activity roster, not the form. Any conversion, retention, or headcount figure sourced from intake forms must reconcile through the behavioral record downstream. Where the form and the roster disagree, the roster wins.

## Rule 3: source-of-truth-first aggregation

A stakeholder asks for total revenue by month. The tempting move is a fresh `SUM(amount)` off the orders table. But the revenue dashboard's canonical query already nets out refunds, deduplicates retried payments, and excludes test orders, and your hand-rolled version silently diverges on exactly those edge cases. Worse, the dashboard's number is the one leadership already sees, so your figure starts an argument it will lose. Find the endpoint or canonical query first, read its exact predicates, and mirror it. Query the raw tables only to verify or debug the canonical number, never to originate a reported one.

## Rule 4: the source-inventory sweep

A team builds a customer-engagement score on top of the support-ticket table, because that was the first source someone reached. Purchases, logins, referrals, and survey responses all existed and all belonged in the score; none were considered, because no one enumerated them. The counter is cheap: before building anything that aggregates across sources, list every candidate source and record an explicit include or exclude decision for each, in the design doc or the PR description. The sweep takes ten minutes. Rebuilding a shipped single-source feature takes a lot longer.

Each of these rules exists because someone shipped the wrong number confidently. Adopt them before you do.
