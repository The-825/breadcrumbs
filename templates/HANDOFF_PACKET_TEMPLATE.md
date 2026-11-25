# Handoff packet template

Assumes: Markdown, filled by hand or posted as a comment; no tooling required. This ships as a template only, with no automation behind it.

When work passes between agents, or between an agent and a person, each side tends to invent its own handoff format. The receiver then has to ask what the topic is, which decisions are settled, where the evidence is, and how old it is. Those questions cost a round trip each, and a handoff nobody can verify gets treated as if it had never happened.

This packet fixes the shape. One file or one pinned comment, five fields, and a status that only moves forward. Use it as the body of a pull request status comment, a hand-off message to another agent, or the first block of a session-state file.

## The packet

```markdown
## Handoff: <short topic, three to six words>

**Topic:** <one sentence: what this work is for>
**Status:** <queued | delivered | acknowledged | responded | verified>
**Updated:** <date and time, with time zone>
**From:** <agent or person> **To:** <agent or person>

### Decisions already made
- <decision, who made it, date. Settled; do not reopen without new evidence.>

### Sources
- <link or path> (read at <date>; <still current | changed since>)

### Freshness
<What would make this packet stale: a merged PR, a changed file, a new ruling.
Name the thing to re-check before acting on it.>

### Next action
<One concrete step, who owns it, and what done looks like.>
```

## The status ladder

The status field walks one ladder and never skips a rung:

| Status | Means | Who sets it |
|---|---|---|
| queued | Written down, not yet sent | The sender |
| delivered | The receiver's channel accepted it | The sender, from a delivery receipt |
| acknowledged | The receiver confirmed it read the packet | The receiver |
| responded | The receiver acted or replied | The receiver |
| verified | Someone other than the receiver checked the result against evidence | A verifier |

Delivered is not acknowledged, and responded is not verified. Writing "done" on a packet that only reached the delivered rung is the failure this ladder exists to stop. If the receiver is unavailable, leave the status where it is and write the blocker under Next action instead of advancing it.

## Rules for filling it in

1. **One packet per work item.** Edit it in place as the status moves; do not stack new packets.
2. **Sources carry a read date.** A link with no date cannot be checked for staleness.
3. **Decisions list who made them.** A decision with no owner is a guess.
4. **No private data.** Keep student records, client details, credentials, and internal operational specifics out of the packet. Point to where they live.
5. **Stop after five rounds.** If the packet has bounced five times between the same two parties without reaching verified, escalate to a person.
