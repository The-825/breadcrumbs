# Make a number explainable

**Status:** public, pattern-only exercise. No reporting endpoint or chart ships here.

**Assumes:** you have the synthetic received CSV in [Automate one handoff](03-automate-one-handoff.md) and a text editor. The example count is derived only from that fixture.

A number without its inclusion rule can be repeated as if it measures something else. Before charting, make one count traceable to its source and owner.

## Your action

Write one source-to-action card for `distinct supply items`. State the source file and revision or digest from the transfer receipt, inclusion rule, count, refresh time, owner, and the question the count can answer. Count each unique nonblank item value once. The fixture has three such values. Write `not recorded` if your receipt lacks a revision, time, or owner instead of inventing one.

Add a prior-period field. If you have no comparable prior synthetic file, write `not available`. If you do, apply the same inclusion rule and record any mismatch for investigation. Do not infer a trend from unlike inputs.

## Human check

Ask the file owner whether the inclusion rule matches the intended question. Reopen the received file and verify the rows. If a count differs, inspect the source, receipt, and rule before changing the card. Save the checked card, not just the number.

The [report catalog pattern](../report-catalog-pattern.md) covers governed self-service queries. This exercise stops at one explainable count.

**Next:** use the card as an example of evidence to preserve in [Review a change before release](05-review-a-change-before-release.md).
