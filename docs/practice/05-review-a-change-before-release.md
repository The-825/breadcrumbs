# Review a change before release

**Status:** public, pattern-only exercise. No Agent Card validator or release action ships here.

**Assumes:** you can compare two fictional Agent Card excerpts. These are teaching fixtures, not live cards or a claim about a service. A contract review cannot prove endpoint behavior.

Removing a declared skill can break a consumer even if the new card parses. Record the change and its owner decision before release.

## Fictional cards

```json
{"version":"baseline","skills":[{"id":"invoice.read"},{"id":"invoice.submit"}]}
{"version":"candidate","skills":[{"id":"invoice.read"}]}
```

## Your action

Write one contract-change receipt: baseline identifier, candidate identifier, changed field, known consumers, owner, decision, and evidence still needed. Record that `invoice.submit` is absent from the candidate. Write `unknown` for consumers you have not checked. The owner chooses whether to restore the skill or prepare a consumer migration; your comparison does not make that choice.

## Human check

Have the owning reviewer confirm consumer impact and the decision. Separately verify actual endpoint behavior in an authorized environment before claiming the release works. Keep those two pieces of evidence distinct. The [A2A score export](../../templates/a2a-score-export/README.md) is a separate optional pointer pattern, not a substitute for contract or runtime review.

**Next:** carry the decision and open evidence into [Hand it to another person](06-hand-it-to-another-person.md).
