# Doctrine excerpt — typed-edge reasoning over a thought corpus

Place this in your governance doc as the section governing cross-conversation or inter-agent communication.

---

## The principles

### 1. Typed edges over plain hyperlinks

Every relationship between two paragraphs should be a *typed edge*, not a plain link or inline citation. Twelve types in the vocabulary; each carries semantic content the system can query.

**Derives from:** Foundation [F2](../../01_foundations/F2_logic_holds.md) — the relationship between two paragraphs is itself a fact that should have one canonical form. Plain hyperlinks are untyped; *"B references A"* could mean "B supports A" or "B contradicts A" or "B was written in response to A" — the system can't distinguish without typed edges.

The vocabulary:

| edge_type | meaning |
|---|---|
| `refines` | B sharpens or extends A |
| `contradicts` | B disagrees with A; **rationale required** |
| `supports` | B agrees with A and adds evidence |
| `references` | B cites A as context, no claim of agreement |
| `supersedes` | B replaces A; A is now stale; **rationale required** |
| `derives_from` | B is a logical consequence of A |
| `responds_to` | direct conversational reply (auto-drawn by `write_message(..., responds_to_msg_id=N)`) |
| `anchors_to` | B rests on doctrinal foundation A (often an external URI) |
| `cites_artifact` | B references an external artifact (commit SHA, file URI, plan entry) |
| `endorsed_by` | participant explicitly agrees with the paragraph (stronger signal than read_by) |
| `pinned_by` | participant pinned the paragraph as durable (exempts from deprecation) |
| `deprecation_voted` | participant voted to retire the paragraph from default views |

### 2. Paragraph-level granularity

Messages are top-level coherent contributions; paragraphs are the unit of lifecycle reasoning. Each paragraph gets a stable UID (`msg<id>-p<sequence>`) and accumulates edges over time independently of its message's other paragraphs.

**Derives from:** Foundation [F1](../../01_foundations/F1_time_has_direction.md) (paragraph-level lifecycle — pinned, voted, contradicted — is finer-grained than message-level lifecycle, and that grain matters for retrospective reasoning) and [F2](../../01_foundations/F2_logic_holds.md) (the right granularity for single-source-of-truth on individual claims).

Convention: one full thought per paragraph row. A single-sentence message has one paragraph; a multi-paragraph message has multiple, each independently citable. Decomposition happens at write time per the helper.

### 3. Append-only with state-transitions as events

Per Foundation [F1](../../01_foundations/F1_time_has_direction.md), rows are append-only. The only "mutations" are state-transition writes that record the transition as a new event:

- `messages.state = 'superseded'` + `superseded_by` pointer (the supersession is the event; the old message stays)
- `messages.state = 'rolled_back'` + `rollback_reason` (the rollback is the event; the message stays)
- New `read_log` rows for each read receipt
- New `pinned_by`, `deprecation_voted`, `endorsed_by` edges for each lifecycle action

The schema deliberately doesn't permit UPDATE statements on the content fields. To "fix a typo," write a new message that `supersedes` the old. The supersession is a fact future readers may need.

### 4. Engagement-floor for paragraph deprecation

A paragraph collapses out of default views (`paragraphs_active.status = 'deprecated'`) when:

- Every participant that has read the parent message has voted to deprecate the paragraph (unanimity-of-readers), AND
- No non-deprecation edge to the paragraph has been drawn since the most-recent deprecation vote (engagement-floor)

The engagement-floor replaces a calendar-based time floor with a structural signal: if the paragraph has accumulated subsequent structural use after a deprecation vote landed, it's demonstrably still load-bearing.

**Derives from:** Foundations [F1](../../01_foundations/F1_time_has_direction.md) (the engagement timestamp is itself a temporal fact) and [E2](../../01_foundations/E2_convergence_is_triangulation.md) (unanimity-of-readers + absence-of-subsequent-engagement is structural triangulation across two independent signals that the paragraph has stopped being load-bearing).

Pinned paragraphs (any participant pinned them) are exempt from collapse. Collapsed paragraphs stay in the DB forever — findable by explicit query, excluded only from default views.

### 5. Thought-UID lineage (PrizmForge-inspired)

Each paragraph carries a `thought_uid` — a stable identifier for the *idea* the paragraph expresses, distinct from the paragraph's own UID (which identifies the *expression* at a moment). The thought-UID is inherited from the superseded paragraph when a `supersedes` edge is drawn at write time; otherwise it's fresh.

**Derives from:** Foundation [F2](../../01_foundations/F2_logic_holds.md) applied to idea-identity. The idea is the fact; the paragraph is the expression at a moment. Conflating them by using only paragraph-UIDs means the system can't reason about idea-identity across expressions. The thought-UID restores single-source-of-truth for idea-identity.

**Mechanism (deterministic, not AI-judged):**

- A paragraph created without a `supersedes` edge gets a fresh `thought_uid` (short UUID).
- A paragraph created with a `supersedes` edge inherits the superseded paragraph's `thought_uid`.
- The lineage is computed at write time by the helper; the schema stores the cached anchor.

**What this enables:**

- Query *"all expressions of thought T over time"* as a single index lookup
- Surface the full revision history of a claim without recursive edge traversal
- Compute the *most-recent expression of an idea* by ordering thought-UID matches by `created_at DESC`

**Why not AI-judged:** an AI deciding *"these two paragraphs express the same thought"* would be hypothesis (per [E1](../../01_foundations/E1_corpus_is_hypothesis.md)) and would require AI-dependency tracking. Computing thought-UID from the explicit supersession edge keeps it deterministic — the supersession declaration is the human/agent's structural commitment; the thought-UID is the cached consequence.

---

## Decision triggers — which edge type to draw

When you're about to make a contribution that relates to an existing paragraph, ask:

| If you're | Draw |
|---|---|
| Building on a paragraph's claim | `supports` (you agree and add evidence) or `refines` (you sharpen or extend) |
| Disagreeing with a paragraph's claim | `contradicts` (REQUIRES rationale explaining the disagreement) |
| Replacing a paragraph's claim | `supersedes` (REQUIRES rationale; thought-UID inherits) |
| Citing a paragraph as context only | `references` (no claim of agreement) |
| Logically deriving from a paragraph | `derives_from` |
| Directly replying to a message | `responds_to` (auto-drawn by `write_message(..., responds_to_msg_id=N)`) |
| Citing doctrinal foundation | `anchors_to` (target is usually external URI) |
| Citing external artifact | `cites_artifact` (target is commit/file/plan-row URI) |
| Explicitly endorsing | `endorsed_by` (stronger signal than just reading) |
| Pinning as durable | `pinned_by` |
| Voting to retire | `deprecation_voted` |

When a claim could draw multiple edges (e.g., it both supports an earlier claim AND derives_from another), draw both. Edges are append-only and cheap; the graph richness comes from explicit relationships.

When a claim makes a substantive contribution WITHOUT any anchoring, that's itself information per the [hypothesis posture](../../00_meta_stances/hypothesis_posture.md): the absence-of-anchor is queryable. Either the claim is novel (may need elevation) or it's an unbacked assertion that should be challenged.

---

## What this doctrine does NOT cover

- **Cross-system message routing.** Once a message is in the corpus, the typed-edge layer covers reasoning about it. Getting messages *into* the corpus from agent runtimes is a separate concern (the helper module provides the API; routing of agents is project-specific).

- **Conflict resolution beyond `contradicts`.** Drawing a contradicts edge surfaces the disagreement structurally; the schema doesn't force resolution. Per [tension-celebration](../../00_meta_stances/hypothesis_posture.md), preserving the disagreement is often more honest than collapsing it. When resolution does happen, it's via dialog (and via `supersedes` edges if one paragraph genuinely replaces another).

- **Privacy/access control.** All paragraphs are visible to all participants by default. Projects with privacy needs can add a `visibility` field or scope reads through additional helpers; out-of-scope for the base subsystem.

- **Cross-corpus federation.** This subsystem is for a single corpus instance. Multiple corpora (e.g., one per project, federated through cross-corpus URIs) is a future concern.

## Cross-references

- [../README.md](../README.md) — the subsystem overview.
- [../schema/thought_corpus_graph.sql](../schema/thought_corpus_graph.sql) — the DDL these principles structure.
- [../code/thought_corpus_helpers.py](../code/thought_corpus_helpers.py) — the helper functions implementing the discipline.
- [../../00_meta_stances/user_is_a_participant.md](../../00_meta_stances/user_is_a_participant.md) — the meta-stance grounding the unified participant registry.
- [../../13_safe_code_modification/](../../13_safe_code_modification/) — the line-grain sibling of the idea-grain identity stability concept this subsystem applies.
- [../../12_ingestion_protocol/examples/multiagent_ingestion.md](../../12_ingestion_protocol/examples/multiagent_ingestion.md) — the ingestion record covering this subsystem's origin.
