# The composite-persona method

Telling true stories from protected data without exposing anyone.

## The problem

The most persuasive artifact a data office produces is a story about one
person. It is also the one artifact you often cannot ship: student records,
client cases, and patient notes are protected, and "changing the name" is not
protection. De-identification of a real record fails quietly, because the
combination of true details is itself identifying.

Aggregates are safe and bloodless. Personas are the bridge: fictional people
assembled only from verified aggregate patterns, so the story is true in
every statistical sense and fictional in every personal one.

## The rules that make it safe

1. **Pattern first, person never.** Start from a verified aggregate (a real
   cohort-level statistic or documented pattern), then invent a person who
   embodies it. Never start from a real record and disguise it; that is
   de-identification, and it fails.
2. **Every attribute carries a receipt.** Each fact in the persona traces to
   a named aggregate claim a reviewer can audit. If an attribute has no
   receipt, cut it or mark it invented color.
3. **No persona maps to a real individual.** If anyone who knows the
   population can say "that is obviously so-and-so," the persona fails
   review and gets rebuilt from different attribute combinations.
4. **Label the fiction everywhere it appears.** On the page, in the deck, in
   the training material: composite, fictional, built from verified
   aggregates, no real person depicted.
5. **Personas are delivery, never evidence.** The aggregate is the evidence.
   The persona exists to make the aggregate land with a human audience.
   Nothing gets decided about any real person because of a persona.

## Where it earns its keep

- Leadership decks that need the human stakes of a finding without a case file.
- Staff training on intervention playbooks (walk the persona, not a student).
- Design work: interface and outreach flows tested against persona journeys.
- Public-facing writing from protected domains, this repo's book included.

## The checklist

- [ ] Every attribute has a named aggregate source
- [ ] Built pattern-first; no real record was the seed
- [ ] Reviewed by someone who knows the population: recognizably nobody
- [ ] Fiction labeled at every appearance
- [ ] Used to communicate a finding, not to decide about a person
