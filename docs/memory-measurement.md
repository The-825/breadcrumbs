# Memory measurement: sit the exam instead of writing more study material

**Assumes:** you already run some form of durable memory for your agents, a settled-facts
store, a rules file, a doc corpus, or all three, and something injects part of it at
session start. It assumes nothing about your language or platform. Every instrument here
is a report you run against your own repo.

Every other doc in this repo tells you what to build. This one tells you how to find out
whether what you built actually works, which is a different question and a much less
comfortable one.

## The failure this prevents

You write a settled fact into the store. It is correct, it is well worded, it is keyed to
the right file. Six weeks later a session re-derives it from scratch, gets a slightly
different answer, and ships that instead.

Nothing failed loudly. The entry was there the whole time. It just never surfaced, because
the key you chose does not match anything the boot matcher looks at, or because the boot
lane has a cap and older entries win it every time, or because a superseded entry is
outranking it. The store looks complete. A reader browsing it would say the system is
working. The only evidence otherwise is work being redone, and that evidence arrives
months late and disguised as ordinary effort.

This is the structural weakness of every memory system built the way this repo describes:
**writing is instrumented and retrieval is not.** You can see how many entries you have.
You cannot see whether a single one of them ever changed what a session did. Every
addition after that point is faith-based, and the natural response to doubt (write more
signage) makes the boot lane more crowded, which makes the problem worse.

The fix is borrowed from how competitive spellers train. They do not re-read the word
list. They practice retrieval, they drill their own misses, and they measure. A memory
layer that has never been tested cold is a study guide nobody has been quizzed on.

## Four questions, four instruments

Each question is a different failure mode, so each needs its own instrument. Running one
of these and skipping the rest gives you a healthy-looking score over a broken lane, which
is worse than no score at all.

| Question | Instrument | Failure it catches |
|---|---|---|
| Could this entry ever surface? | Reachability exam | Write-only entries |
| Did the injection lane actually carry it? | Lane probe | A healthy corpus behind a stuck lane |
| Did anyone act on it? | Use stamps | Dead weight that still costs boot tokens |
| What did someone look for and not find? | Search-miss ledger | Gaps you have no other way to see |

### 1. Reachability: could this entry ever fire

Take the matching rules your session-start hook actually uses, replay them against your
real repo tree, and ask of every entry: is there any input that would surface this?

This is the cheapest instrument by a wide margin, because it costs no sessions. It is pure
static analysis against code you already have. Give each entry a verdict:

- **Precise.** The key is a path that exists. A session touching that file surfaces it.
- **Broad.** The key matches, but so widely that the entry competes with everything else
  under the same key and rarely wins a capped lane.
- **Unreachable.** The key is a path that no longer exists, or was never a path at all.
  A bare noun as a key is the common case, and it feels perfectly reasonable when you
  write it.
- **Special.** Deliberately keyed to a domain word your matcher handles by name.

Unreachable is the verdict that matters, and the reason is worth stating plainly: **a
write-only entry is worse than no entry.** No entry leaves a visible hole. A write-only
entry fills the hole on paper, so nobody goes looking, and the ledger reports coverage it
does not have.

Ratchet the result. Store the current counts as a baseline file and fail the check when
reachability gets worse, the same way [context-budget.md](context-budget.md) ratchets what
every session loads. Without the ratchet you get one good cleanup and slow regrowth.

Two regressions are worth catching, and the second is the one people miss. More
unreachable entries is obvious. Fewer precise entries at the same total is the subtle one,
because re-keying a specific entry to something broad reads as tidying up and is a
downgrade.

*From the system this pattern came out of:* the exam was written after three unrelated
questions converged on the same missing thing, and the first run found entries keyed to
bare nouns that could never have fired. One of them had been written earlier the same day,
by a session that believed it had captured a ruling.

### 2. Lane probe: a healthy corpus behind a stuck lane

Reachability scores the corpus. It says nothing about the lane.

You can have a corpus where nearly every entry is precisely keyed and still be injecting
the same handful of entries into every session, because the ranking has a tie-break that
never varies, or the cap is smaller than you remember, or one path key matches so much
traffic that it crowds the rest out.

So probe the lane directly. Simulate several different session-start conditions, capture
what each one would actually inject, and diff them against each other. Identical output
across genuinely different inputs is the finding. The corpus can score perfectly healthy
while this is happening, which is exactly why it needs its own instrument and its own run.

### 3. Use stamps: did anyone act on it

[floating-memory.md](floating-memory.md) covers use-stamped decay as a trust signal. The
same stamp is a measurement instrument, and this is the readout side.

When a session uses an injected entry, meaning it changed what the session did, stamp it in
place with the date and bump a counter. Seeing an entry is not use. Use is: it prevented a
re-derivation, it shaped a query, it stopped a wrong assumption. Only stamp when it did
work.

Then read the corpus as a whole rather than one entry at a time:

- How many live entries have ever been stamped at all
- How many were used in the last window
- Which entries are injected often and used never, the dead weight paying boot tokens on
  every single session

That last line is the one that changes behavior. An unstamped entry is not proof of
uselessness, since stamping is a discipline and disciplines are leaky, but a large
unstamped fraction tells you the lane is decorative and you should stop adding to it until
you know why.

### 4. Search-miss ledger: what someone looked for and did not find

The other three instruments examine what you wrote. This one captures what was missing.

When a lookup comes back with nothing useful, log one line: the date, where you searched,
the query verbatim, what you expected to find, and where the answer should live once
somebody writes it. Append-only, never edited. A gap that gets filled simply stops
recurring.

Without this, a miss evaporates with the session. The next session hits the same wall,
pays the same cost, and also leaves no trace. The ledger is what turns a private moment of
friction into a queue you can work, and the `suggested_home` field means the fix is
already scoped when you get to it.

Schema and adoption notes:
[templates/ledger-tools/SEARCH_MISSES.md](../templates/ledger-tools/SEARCH_MISSES.md).

## The fifth thing, which is not an instrument

Supersession pointers deserve a mention here even though they are curation rather than
measurement, because they corrupt every number above.

An entry that announces in its own prose that it corrects or replaces an earlier one, but
carries no machine-readable pointer saying so, is still live. It still ranks. It still
competes for a capped injection lane against the very entry that replaced it. Your
reachability score counts it as healthy, because it is reachable, and it is reachable to
say something you no longer believe.

Scan for the prose without the pointer. Restrict candidate targets to the same key with a
strictly earlier date, since that is the only structural guarantee the ledger gives you,
and **propose rather than apply.** A wrong supersession pointer silently deletes a live
fact from every future injection, and the failure mode is invisible, so the default has to
be a human ruling on a cheap proposal.

## Running it

The first three instruments ship as one script,
[templates/ledger-tools/retrieval_exam.py](../templates/ledger-tools/retrieval_exam.py).
Stdlib only, no dependencies, exits 0 unless you ask it to gate.

```
python3 templates/ledger-tools/retrieval_exam.py <your-ledger.jsonl> --root .
python3 templates/ledger-tools/retrieval_exam.py --selftest
```

**The matcher is the honest catch, so read this before trusting a number.** The script
cannot read your session-start hook. It ships a model of the common matcher shape (entries
keyed by repo path, a cap on how many get injected, most specific and most recent win) and
you correct it with a small `--matcher` config: your special keys, your real cap, which
date field you rank on, where you draw the line between precise and broad. Get that config
wrong and the report describes the model instead of your system, which is worse than
having no report, because it looks like evidence.

The cap is the number to check first. It is what turns "reachable" into "actually seen,"
and it is almost always smaller than people remember.

Probes are the other input worth an honest look. With no probes file the script derives one
per top-level directory so it runs on any repo immediately, but derived probes are a smoke
test, not an answer. Write probes that mirror the session shapes you actually run. If no
probe touches a file any entry keys on, the script says `UNEXERCISED` and refuses to draw a
conclusion about the lane rather than reporting a stuck one, because a confident verdict
about a lane that was never exercised is the same mistake the exam exists to catch.

### Survey mode: before you have a ledger at all

Everything above needs a conclusions store in this kit's schema, which means it runs only
for people who already adopted the pattern, who are the people who need it least. Survey
mode asks the same question of what a normal repo already has:

```
python3 templates/ledger-tools/retrieval_exam.py --survey --root /path/to/repo
```

With no ledger there is no injection cap to model. What loads automatically is the rules
file, and every other document is reachable only if something the agent already read
points at it. So reachability becomes link distance from that boot surface, and the
finding is the orphan: a document nothing links, which a session never opens on its own
no matter how good it is. Islands are the worse version, a cluster linked only from other
unreachable documents, which is what an index page nobody points at produces.

It also prints what every session pays before any work happens, which is the
[context-budget.md](context-budget.md) number measured rather than estimated.

Run against this repo on 2026-08-06: 117 markdown documents, 2 booted (CLAUDE.md and
README.md, 376 lines and 20,052 bytes charged to every session), 115 linked, 0 islands,
0 deep, 0 orphans. The first run had one orphan, CONTRIBUTING.md, which nothing in the
repo linked; the README now does, which is what took the count to zero.

**One caveat learned by getting it wrong here.** The first version of the resolver treated
a link to `templates/` as a link to nothing, because a directory is not a document. That
reported 87 islands and 6 orphans in this repo, which looked like a dramatic finding and
was a bug in the tool: a forge renders a directory link as its README, so a reader
following that link lands somewhere real. The resolver now does the same. If your tooling
does not, your number is different from this one and you should say so.

In CI, store a baseline and gate on it:

```
python3 templates/ledger-tools/retrieval_exam.py <ledger> --root . \
    --baseline .retrieval-baseline.json --fail-on-regression
```

## Sizing it

Start with reachability. It costs no sessions, and on a corpus that has never been tested
it will find something on the first run. Add the search-miss ledger next, because it is a
text file and a habit, and it starts paying the moment anyone uses it.

The lane probe and the use-stamp readout both need the first two to be worth anything, so
they come after. Do not build all four before running any of them. The point of this doc
is to stop building study material.

## Related

- [floating-memory.md](floating-memory.md), decay by rank, age, and use
- [context-budget.md](context-budget.md), the ratchet pattern these checks reuse
- [catalog-routing.md](catalog-routing.md), the routing layer reachability is testing
- [self-improvement-loop.md](self-improvement-loop.md), where a finding becomes an artifact
- [breadcrumbs-whitepaper.md](breadcrumbs-whitepaper.md) section 7, which names this
  instrumentation as new and its numbers as owed
