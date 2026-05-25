# 14 — Thought corpus graph

## The concept

> Typed-edge reasoning over a persistent thought corpus. **Messages** are coherent contributions from one participant; on write they decompose into **paragraphs** with stable per-paragraph identifiers (`msg<id>-p<seq>`). **Edges** are typed relationships between paragraphs (refines / contradicts / supports / supersedes / derives_from / responds_to / anchors_to / cites_artifact / endorsed_by / pinned_by / deprecation_voted) with required rationale on the structural ones. **Read receipts** are tracked separately to feed the engagement-based deprecation mechanism. A **thought-UID** lineage (PrizmForge-inspired) computed from supersession edges lets you query *"all expressions of this idea over time"* as a first-class operation.

**Derives from:** Foundations [F1](../01_foundations/F1_time_has_direction.md) (every message, paragraph, and edge is an immutable temporal fact; lifecycle transitions are state-transition events) and [F2](../01_foundations/F2_logic_holds.md) (typed edges are single-source-of-truth for the relationship between two paragraphs; thought-UID is single-source-of-truth for idea-identity across supersession). The PrizmForge-inspired thought-UID extension applies F2 at idea-grain the same way [13_safe_code_modification/](../13_safe_code_modification/) applies it at line-grain.

**Ingested from MultiAgent** with a PrizmForge-inspired enhancement — see [12_ingestion_protocol/examples/multiagent_ingestion.md](../12_ingestion_protocol/examples/multiagent_ingestion.md) for the full ingestion record.

## Why this matters for agent-governed systems

Cross-session memory in agent-governed systems has a structural shape problem. Plain message logs preserve *what was said* but not *how claims relate*. A "supersedes" relationship between two claims is just a hyperlink; the system can't reason about "all supersessions in the last week" or "all paragraphs that build on this one" without typed edges.

Typed-edge reasoning solves that. Each relationship type carries semantic content the system can query: `contradicts` surfaces unresolved disagreements; `supersedes` surfaces the lineage of revised claims; `anchors_to` surfaces which doctrinal foundations are most-cited; `endorsed_by` distinguishes "the reader has seen this" from "the reader explicitly agrees with this."

For multi-agent systems specifically, this matters because:

- **Disagreement gets structural preservation, not silent collapse.** A contradicting paragraph stays in the corpus alongside the paragraph it contradicts; both are queryable; the disagreement is data, not a problem to make go away.

- **Cross-session continuity becomes computable.** *"What was the lineage of the decision to use X?"* becomes a graph traversal rather than a manual archeology project.

- **Engagement-based deprecation lets the corpus naturally compact.** Paragraphs that nobody builds on after their first deprecation vote collapse out of default views; paragraphs that get refined, supported, or contradicted demonstrate load-bearing-ness through that engagement.

## What's in this directory

| File | Purpose |
|---|---|
| [schema/thought_corpus_graph.sql](schema/thought_corpus_graph.sql) | DDL for participants + messages + paragraphs + edges + read_log + `paragraphs_active` view. Includes schema-level CHECK constraints for required rationale (improvement over MultiAgent's API-only enforcement) and the PrizmForge-inspired `thought_uid` column on paragraphs. |
| [doctrine/typed_edge_reasoning.md](doctrine/typed_edge_reasoning.md) | The principles: typed edges over plain hyperlinks, paragraph-level granularity, append-only state-transitions, engagement-based deprecation, thought-UID lineage as the PrizmForge-inspired enhancement. Includes decision triggers for which edge type to draw. |
| [code/thought_corpus_helpers.py](code/thought_corpus_helpers.py) | Python helper module mirroring MultiAgent's `multiagent.py` API surface, with type hints and dataclass returns: `register_participant`, `write_message`, `read_inbox`, `mark_read`, `anchor`, `cite_artifact`, `contradict`, `supersede`, `pin`, `vote_deprecate`, `endorse`, `respond_to`, plus the new `thought_lineage` query helper. |

## How to adopt

1. **Copy the schema** into your migrations directory. The tables are independent of your project's domain schema; this sits alongside as cross-conversation infrastructure.

2. **Copy the doctrine** into your governance doc. Place it under the section governing inter-conversation or inter-agent communication.

3. **Copy the helpers** into your runtime. Adapt the imports and connection management to your project's DB layer.

4. **Wire participation into your agents' startup protocol.** Each agent that writes to the corpus needs to register itself once (idempotent), then post messages on every interaction worth preserving.

5. **Optional but recommended — wire the engagement-floor deprecation.** The `paragraphs_active` view does the computation; consumers query the view rather than the raw paragraphs table. This is what makes the corpus naturally compact over time.

6. **Optional — wire thought-UID lineage.** The `thought_uid` is computed from supersession edges; the helpers expose `thought_lineage(thought_uid)` which returns all paragraphs in the lineage ordered chronologically. Useful for *"what's the full history of this idea?"* queries.

## The PrizmForge-inspired thought-UID enhancement

The kit's [13_safe_code_modification/](../13_safe_code_modification/) subsystem ingested PrizmForge's line-GUID concept: each line of code gets a stable identifier that survives surrounding insertions and deletions. This subsystem applies the same insight one layer up — *each idea* (not each paragraph-expression-of-an-idea) gets a stable identifier that survives supersession.

The mechanism:

- A paragraph created with no supersession edge gets a fresh `thought_uid` (generated as a short UUID).
- A paragraph with a `supersedes` edge to an earlier paragraph *inherits* the earlier paragraph's `thought_uid`.
- The lineage is computed from the supersession edge graph; the `thought_uid` is the cached anchor that makes the query fast.

This is honest about what supersession means: the new paragraph and the superseded one are two expressions of the same idea at different moments. Plain UIDs treat them as unrelated; the thought-UID treats them as a lineage. Queries like *"show me all expressions of thought T over time"* become a single index lookup rather than a recursive edge traversal.

Per [01_foundations/F2_logic_holds.md](../01_foundations/F2_logic_holds.md): the idea is the fact; the paragraph is the expression at a moment. Conflating them by using only paragraph-UIDs means the system can't reason about idea-identity across expressions. The thought-UID restores single-source-of-truth for idea-identity.

**Lineage-only thought-UID, not AI-assigned.** Per the hypothesis posture, an AI judging *"these two paragraphs express the same thought"* would be hypothesis (and would need an AI-dependency note). Computing thought-UID from supersession edges keeps it deterministic — the supersession edge is the explicit declaration that links the expressions; the thought-UID is the cached lookup.

## Tensions to name explicitly

1. **Paragraph-granularity assumption.** Some content doesn't decompose cleanly into paragraphs — a single sentence claim or a code block that's structurally one unit. The schema handles this by allowing single-paragraph messages; the convention is *"one full thought per paragraph row,"* which means very short messages may have just one paragraph and that's fine.

2. **The unanimous-readers deprecation mechanism (now engagement-floor)** still requires every reader to vote before collapse. A single reader who never engages further can block deprecation of an otherwise-stale paragraph. Acceptable risk for the current scale; if the corpus grows large enough that this becomes friction, the mechanism can be refined (e.g., majority-of-readers + engagement-floor instead of unanimity).

3. **Schema-level rationale enforcement is stricter than MultiAgent's.** MultiAgent enforces rationale on `contradicts` and `supersedes` at API level; this subsystem enforces at schema level via CHECK constraint. The trade: stronger guarantee at the cost of slightly-less-flexible migrations (changing the enforced-rationale set requires a schema change).

4. **AI-dependency notes apply to the *content* of edges, not the edge mechanism.** The decision to draw a specific edge (*"this paragraph contradicts that one"*) is AI judgment when agents draw it. Per [11_ai_dependency_tracking/](../11_ai_dependency_tracking/), edge-drawing predicates in automated paths need AI-dependency notes. The edge vocabulary itself is deterministic infrastructure.

5. **Read receipts are per-message, not per-paragraph.** Inherited from MultiAgent. Means the deprecation mechanism can't distinguish "the reader read paragraph p3 specifically" from "the reader opened the message containing p3." Acceptable for current use; refinement to per-paragraph reads would let finer-grained engagement-floor logic.

## Cross-references

- [12_ingestion_protocol/examples/multiagent_ingestion.md](../12_ingestion_protocol/examples/multiagent_ingestion.md) — the full ingestion record covering this subsystem's origin.
- [13_safe_code_modification/](../13_safe_code_modification/) — the line-grain sibling to this subsystem's idea-grain identity-stability concept.
- [00_meta_stances/user_is_a_participant.md](../00_meta_stances/user_is_a_participant.md) — the meta-stance that grounds the user-and-agents-in-one-registry choice.
- [06_patterns_and_dissonance/](../06_patterns_and_dissonance/) — the dissonance ledger pattern that this subsystem's `contradicts` edge type makes structurally first-class.
- [01_foundations/F1_time_has_direction.md](../01_foundations/F1_time_has_direction.md) and [F2_logic_holds.md](../01_foundations/F2_logic_holds.md) — the foundations this subsystem implements.
