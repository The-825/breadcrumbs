# AGENTS.md

This repo's agent instructions live in **[CLAUDE.md](CLAUDE.md)**. That file is
the single source of behavioral truth for every coding agent working here,
regardless of vendor or tool (Claude, Codex, Gemini, or anything after them).
Read it completely before touching anything.

Where this repo's memory lives:

- `SESSION_STATE.md`: the living handoff. Read it before resuming work.
- `planning/DECISIONS.md`: the D-numbered rulings ledger.
- Known issues: GitHub issues on this repo, not a file.
- Everything here is public the moment it lands: no private, production, or personal content, ever (rule 1).

Do not duplicate policy into this file. It is a router only; durable rules
stay in CLAUDE.md, and a ruling that lands in chat is captured in the ledger
the same turn. Every agent follows the same branch, PR, and merge conventions
CLAUDE.md defines; no vendor default overrides them.

For cross-repository routing, read `kit.json` → `portfolio_contract`. It is the
machine-readable ownership and public-data boundary for this repository.
