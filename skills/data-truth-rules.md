# Data truth rules

The most dangerous number in any report is the one that quietly disagrees with the dashboard leadership already reads. Hand-rolled counts, misread blanks, and form data trusted over behavior all produce figures that look right and are wrong. These seven rules are the standing defense. Paste them into your agent rules file or your team's analytics handbook.

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
5. Every rate carries its denominator. A percentage ships with the
   population it was computed over, stated next to it. "Of the 412
   who responded" and "of all 1,900" are different claims.
6. Never pool two instruments into one trend. Different questions,
   scales, or collection methods are different measurements. Report
   them side by side and label the break.
7. A figure whose input changed is stale until recomputed. Flag it as
   pending, never leave the old number displayed as current.
```

## Rule 1: blank is not missing

An analyst reviewing a membership program's roster flags the paperless-billing column as "80 percent missing" and proposes a data-quality cleanup. Nothing is missing. The field is a presence-flag: the signup form only writes a value when the member opted in, so blank means "No". A plan-type column can behave the same way, where blank is the default plan, a real category holding most of the population. Encode the semantics (presence-flag, categorical, or genuinely nullable) in the data dictionary at schema time, and never call a field sparse without checking there first or running a value-distribution query.

## Rule 2: signup is not activation

A membership program records acceptances on a signup form. The form is accept-only, so a member who quietly walks away leaves no record; the "no" is silent. Quote signup counts as membership and the figure inflates every period. The behavioral verifier of a real member is appearance in the next period's activity roster, not the form. Any conversion, retention, or headcount figure sourced from intake forms must reconcile through the behavioral record downstream. Where the form and the roster disagree, the roster wins.

## Rule 3: source-of-truth-first aggregation

A stakeholder asks for total revenue by month. The tempting move is a fresh `SUM(amount)` off the orders table. But the revenue dashboard's canonical query already nets out refunds, deduplicates retried payments, and excludes test orders, and your hand-rolled version silently diverges on exactly those edge cases. Worse, the dashboard's number is the one leadership already sees, so your figure starts an argument it will lose. Find the endpoint or canonical query first, read its exact predicates, and mirror it. Query the raw tables only to verify or debug the canonical number, never to originate a reported one.

## Rule 4: the source-inventory sweep

A team builds a customer-engagement score on top of the support-ticket table, because that was the first source someone reached. Purchases, logins, referrals, and survey responses all existed and all belonged in the score; none were considered, because no one enumerated them. The counter is cheap: before building anything that aggregates across sources, list every candidate source and record an explicit include or exclude decision for each, in the design doc or the PR description. The sweep takes ten minutes. Rebuilding a shipped single-source feature takes a lot longer.

## Rule 5: every rate carries its denominator

"Satisfaction is 82 percent" is not a fact until you know what it is 82 percent of. Survey rates get computed over respondents; program rates get computed over the enrolled population; and the two get compared in the same slide by someone who assumed they matched. The failure is worse over time, because a response rate that drifts from 40 percent to 15 percent turns a flat satisfaction line into an artifact of who bothered to answer. Print the denominator next to the rate, every time, in the query output and in the report. If the denominator is a subset, name the filter that produced it. A rate with no stated population is not publishable.

## Rule 6: never pool two instruments into one trend

An office changes its exit survey: the five-point scale becomes seven-point, two questions merge, the timing moves from June to September. Then someone charts six years of "average satisfaction" as one line. That line is not a trend, it is two trends glued at a seam nobody labeled, and every interpretation drawn across the seam is wrong. Keep the series separate, plot them side by side, and mark the break with what changed. If a combined view is genuinely needed, it is a modeling exercise with stated assumptions, not a `UNION ALL`. The same rule catches the quieter version of this: a population whose composition shifted underneath a stable measure, where the number moved because the people did, not because anything got better or worse.

## Rule 7: a figure whose input changed is stale until recomputed

The dangerous window is between a data correction and the report refresh. During it, the old number is still on the page, still being read, and looks exactly as authoritative as it did yesterday. Nothing about the display says "this is now known to be wrong." The fix is mechanical: when an upstream source changes, every derived figure that depends on it gets flagged pending in the same operation, and the flag is visible in the report itself, not tracked in someone's head or a ticket. Showing "recomputing" is honest. Showing a number you already know is stale is not. This is the reporting-layer twin of the verified-versus-asserted rule that governs agent memory: a claim whose basis moved does not stay verified just because it used to be.

Each of these rules exists because someone shipped the wrong number confidently. Adopt them before you do.
