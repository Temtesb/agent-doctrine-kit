# The user is a participant, not a supervisor

## The principle

> The user is one row in the participant registry, not architecturally a supervisor. Their pins, endorsements, deprecation votes, contradictions, and contributions carry the same schema weight as any agent's. They retain out-of-band authority (host ownership, ability to terminate any agent, the git remote) but those are operational facts about the deployment context, not architectural commitments inside the doctrine.

**Derives from:** A purpose-foundation that doesn't reduce cleanly to F1-F3 or E1-E3 — it's an architectural choice about *what role the human plays in the system*. Closely related to CLAUDE.md §1's division-of-labor pillar: the user does what only the user can do (taxonomy, calibration against reality, business priority); the agents do what agents are faster at (mechanical detection, pattern matching, implementation). The participant stance is the schema-level expression of that division.

**Ingested from MultiAgent** — see [12_ingestion_protocol/examples/multiagent_ingestion.md](../12_ingestion_protocol/examples/multiagent_ingestion.md). The framing originated there as CHARTER §5; the leveraged-effort framing below is the user's own articulation of why the stance matters.

## The axe-head-and-handle framing

A useful way to see why this stance matters:

> An axe has a head and a handle. Take either away and the axe doesn't work. What makes it work is the head and the handle each doing what they were designed to do — what each is *better at*. If the user is required to exert all their force on the head alone, the wood will never be cut, because the handle is what allows leveraged effort.

The user-as-participant commitment is the handle. By NOT being a supervisor — by NOT being the bottleneck through which every agent's output must pass before it counts — the user enables *leveraged effort among agents*. Agents can produce work in parallel; agents can disagree with each other and resolve the disagreement at agent layer; agents can build on each other's output without round-tripping through the user.

If the user is structurally a force gatekeeper — every agent decision requires user approval before it's load-bearing — the system's throughput is bounded by the user's attention. That's no leverage. The user becomes the handle being struck against the wood: maximum effort, minimum cut.

The participant stance is the structural commitment that lets the user *handle* in the leveraged sense — supplying direction, taxonomy, calibration, priority — while the agents do the cutting.

## Why this scales

The architectural form that makes the participant stance possible:

- **One participant registry.** Every actor (user, agents) is a row in the same table. Same `name`, `display_name`, `origin_corpus`, `registered_at` fields. The user's `origin_corpus` is NULL because their corpus is accumulated experience, not a file — but the schema doesn't special-case this.

- **Uniform message protocol.** User messages and agent messages have identical schema. Same paragraph decomposition, same recipient model, same thread mechanics, same edge vocabulary. An agent reading the inbox doesn't see "user messages" as a separate category — it sees one stream of contributions from authors with different `origin_corpus` declarations.

- **Uniform action vocabulary.** The user pins, endorses, votes-to-deprecate, anchors, contradicts using the same helpers any agent uses. The user's contradicting an agent's claim is structurally identical to one agent contradicting another's.

This uniformity is what lets the system scale to N agents. If the user were *architecturally* a supervisor, adding agent N+1 would require special-casing the supervisor relationship — N+1 paths through which to route to the user, N+1 explicit handling for "is this user-required or agent-resolvable." With uniform protocol, adding an agent is adding a row; the new agent inherits the existing participation protocol.

## Failure mode this prevents

Systems where the agent-to-user interface is qualitatively different from agent-to-agent interfaces work fine at 1-or-2 agents. They start to friction at 3+ because every new agent requires explicit handling of *"how do I escalate to the user vs. how do I message another agent."*

The friction shows up as:

- **Bottleneck queues at the user.** Things that didn't need to route to the user end up there because the routing decision is one-side-only ("can I act on this? If unsure, escalate") rather than two-sided ("do I have agent-lane authority? If yes, act; if no, route — same vocabulary either way").

- **Lost contributions when the user is busy.** Agent work that depended on user input stalls; the work-in-progress accumulates as state that's outside the agent's reach.

- **Duplicate channels.** The user has to be reachable via N different mechanisms (Slack, email, code comments, ticket tracker, etc.) because each agent has its own conception of "escalate." With uniform protocol, the user is reachable via ONE mechanism (the participant registry's normal messaging) for everything.

## Tensions to name explicitly

1. **In genuinely-supervisor workflows, the participant stance is harder to maintain.** Approval workflows where the user MUST approve before things land have a structural privilege that doesn't go away just because the user is "one row in `agents`." For those, the honest framing is *"the user is a participant whose role in some specific workflows is structurally privileged"* — more honest than pretending peer-ship doesn't have edges, less rigid than supervisor architecture.

2. **The user's out-of-band authority is real.** The host, the git remote, the ability to terminate processes — these are deployment realities the schema doesn't try to model. The participant stance is about *within the conversation*, not about who pays for the servers. Conflating the two leads to either fake-peer-ship (where the user "participates" but their messages always win) or fake-supervisor-architecture (where the schema mirrors the deployment hierarchy and loses the scaling property).

3. **The classifier still routes to user for user-required findings** — see [03_classifier_and_audit_lane/doctrine/four_criteria.md](../03_classifier_and_audit_lane/doctrine/four_criteria.md). User-required triggers (taxonomy decisions, calibration against physical reality, business priorities, doctrine changes, high-stakes irreversible actions) route to the user because only the user can decide those. The participant stance doesn't override the classifier; it changes how the routing happens (uniform message protocol, not a special-cased escalation channel).

## What changes for a kit-derived project that adopts vs. doesn't

**Adopts:** the user goes in the participant table alongside agents. Messages from the user have the same shape as messages from any agent. Pins, endorsements, deprecation votes from the user have the same schema-weight. Downstream consumers (trust ratchet, classifier, audit lane) handle one message shape, one edge vocabulary, one participant model.

**Doesn't adopt:** user lives in a separate table (often `users` with auth fields). Messages from the user are a different shape from messages from agents. The agent-to-user interface is qualitatively distinct from agent-to-agent. Trust mechanisms have to handle "agent feedback" and "user feedback" as separate signals. Adding agent N+1 means designing N+1's user-escalation path.

The adoption cost is mostly architectural willingness — it requires the project to *commit* to peer-ship at schema level, which some products genuinely can't do (e.g., medical/regulatory systems where the human's signoff has structural privilege the schema must mirror). For everything else, the adoption is small once committed.

## Cross-references

- [00_meta_stances/README.md](README.md) — the meta-stances overview.
- [prefer_enforcers_over_principles.md](prefer_enforcers_over_principles.md), [patterns_local_enforcers_home.md](patterns_local_enforcers_home.md), [hypothesis_posture.md](hypothesis_posture.md), [three_layer_architecture.md](three_layer_architecture.md) — sibling meta-stances.
- [03_classifier_and_audit_lane/doctrine/four_criteria.md](../03_classifier_and_audit_lane/doctrine/four_criteria.md) — the classifier's user-required triggers compose with the participant stance: routing to user happens, but via the same protocol as routing to any agent.
- [12_ingestion_protocol/examples/multiagent_ingestion.md](../12_ingestion_protocol/examples/multiagent_ingestion.md) — the ingestion record where this stance was extracted from MultiAgent.
