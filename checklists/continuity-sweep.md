# Continuity sweep checklist

> Part of the companion kit for *From Archivist to Architect* (The Architect's Blueprint, Book 1).

A change is not done when the file is saved. It is done when every surface that cites the changed thing agrees with it. Skip the sweep and a corrected figure, a renamed metric, or a changed policy gets updated in one place and stays stale in five, and the stale copy is the one leadership reads. Run this sweep after any change to a fact that other surfaces cite: a number, a name, a price, a status, a label, a definition.

## Part 1: drift check

Every place that cites the changed value must match the canonical source.

- [ ] **Name the canonical source.** Before sweeping, write down where the true value lives (the endpoint, the view, the config entry). If you cannot name it, that is the first problem to fix.
- [ ] **Enumerate the citing surfaces.** Grep for the old value and the old name across everything: dashboards, docs, READMEs, downstream reports, sample outputs, marketing copy if it quotes the number.
- [ ] **Re-verify each hit against the canonical source.** Do not propagate the new value from memory; read it from the source each time. A sweep that copies a typo forward is worse than no sweep.
- [ ] **Check the app-shaped surfaces on three axes.** Page to canonical (every displayed figure traces to the endpoint and config it reads, no hardcoded stale literal, no mock data rendered under a "live" badge). Page to page (no two pages disagree on the same quantity). Page to supporting docs (what the docs prove, the UI reflects).

## Part 2: completeness check

"It wasn't wrong, just absent" is still a miss.

- [ ] **Ask what should now exist.** When something materially changes or is newly added (a concluded cycle, a new data source, a new dimension in the data), find the surfaces that SHOULD now reflect it and do not. Absence never shows up in a grep for the old value; you have to reason from the change outward.
- [ ] **Check the characterizations, not just the citations.** If a report characterizes a population, does it now carry the dimension you just added? If a process concluded, does every doc that mentions it read as concluded, not "in progress"?
- [ ] **Extend your known-drift list.** Keep a short list of drift patterns that have bitten before, and check each one. Add today's find to the list so the next sweep catches it mechanically.

## Discipline

- [ ] **Fix only the impacted files.** Never touch a surface that is already consistent. A sweep that "tidies while it's in there" creates review noise and new drift risk.
- [ ] **Leave period-accurate historical documents alone.** A dated snapshot that was true when written stays as written.
- [ ] **Report "no drift" explicitly when clean.** Silence is ambiguous; it reads as "sweep not run." The two valid outcomes are a list of fixed files or the words "no drift found," and nothing else.
- [ ] **Log out-of-scope finds.** Drift you found but cannot fix in this change goes in the known-issues ledger, never a silent pass.

The sweep runs on the change event, not on a timer. Timers find drift after someone else already has.
