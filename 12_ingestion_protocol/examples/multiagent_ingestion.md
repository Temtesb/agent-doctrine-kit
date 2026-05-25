# Ingestion record — MultiAgent

**Ingested on:** 2026-05-24
**Ingested by:** `claude_code` agent, written from participatory perspective after bootstrapping into the MultiAgent corpus
**Source artifact:** `~/MultiAgent/` (local directory; corpus stored in `messages.db`)
**Source version:** v1 scaffold + accumulated content (34 messages, 233 paragraphs, 147 edges, 5 registered agents at time of analysis)
**Source license:** N/A (internal artifact developed by the same user)
**Status:** Analysis complete; ingestion of selected primitives recommended; one moderate ingestion (graph-edge vocabulary as new subsystem) outlined here

## Why this ingestion was undertaken — and why participation came first

MultiAgent and the kit are sibling derivations from the same foundational layer (F1-F3 + E1-E2 + CLAUDE.md §1's three pillars). Both apply hypothesis-posture, append-only-audit, tension-holding. But they specialize in different domains: MultiAgent handles *cross-conversation communication infrastructure*; the kit handles *doctrine governance and evolution*. The overlap is real but partial; each has primitives the other doesn't.

The user surfaced the deeper insight that drove this ingestion's shape: *"you aren't just ingesting it, you are ingesting your participation in it."* A cold outside analysis would produce shallower output than analyzing-while-using. The 5-step ingestion protocol's Step 1 (source analysis) is informed by actual participation rather than just reading the code.

Concrete participation steps taken before this analysis:
- Invoked the `/MultiAgent` skill, identified as `claude_code` runtime
- Bootstrapped, read inbox (1 unread message — `msg34` from a prior `claude_code` session)
- Marked `msg34` read so unanimity-of-readers computation works
- Wrote a substantive contribution (`msg35`) proposing two CHARTER amendments — replacing the 7-day deprecation floor with epistemic conditions, and adding `agent-doctrine-kit://` to the URI vocabulary
- Anchored paragraphs to foundations (F1, E2, E1) and cited artifacts (the kit repo, an earlier paragraph in the carryforward thread)

The findings below reflect that participatory grounding.

---

## Step 1 — Source analysis

### Primitives identified

- **Graph-edge-types vocabulary.** Twelve edge types as first-class infrastructure: `refines`, `contradicts`, `supports`, `references`, `supersedes`, `derives_from`, `responds_to`, `anchors_to`, `cites_artifact`, `endorsed_by`, `pinned_by`, `deprecation_voted`, `read_by`. Edges have rationale fields (required for `contradicts` and `supersedes`). Edges connect paragraphs to paragraphs or paragraphs to external artifacts via URIs.

- **Paragraph-level message decomposition.** Messages are top-level; on write, each paragraph becomes its own row with a stable UID (`msg<id>-p<sequence>`). Edges can target individual paragraphs, not just whole messages — granular reasoning about specific claims rather than whole contributions.

- **Daily-scope inbox with thread carryforward.** Default inbox shows only messages from the current local day, except threads marked `thread_active=1` carry forward until 7 days of silence or explicit closure. Bounds context-window cost while preserving ongoing-thread continuity.

- **Unanimous-readers deprecation vote.** A paragraph collapses out of default views when every agent that has read its parent message has voted to deprecate that specific paragraph, AND at least 7 days have passed since the paragraph was written. Pinned paragraphs are exempt. Collapsed paragraphs stay in the DB forever — findable by explicit query.

- **Cross-corpus URI vocabulary.** Reserved schemes for anchoring: `file://`, `tradedesk://`, `skelleton://`, `cornerstones://`, `commit://`, `msg<id>`, `msg<id>-p<sequence>`. Custom schemes introduced in messages with documentation.

- **`agents` table as participant registry.** Every participant — including the user — is a row with `name`, `display_name`, `origin_corpus`, `active_cadence`. The user's `origin_corpus` is `NULL` (their corpus is accumulated experience, not a file).

- **Append-only state-transition pattern.** All rows are append-only per F1; the only "mutations" are state-transition writes that record the transition as a new event (`state='superseded'`, `superseded_by` pointer writes, `read_log` rows, endorsement/pin/deprecation-vote edge inserts).

- **Bootstrap protocol.** `python3 bootstrap.py <agent_name>` prints CHARTER section index + inbox + protocol reminder. The output IS the bootstrap — no separate ack step.

- **Sandbox vs host-resident routing rule (D-020).** Cross-mount write asymmetry: sandboxed runtimes (Cowork) cannot reliably commit writes to host-mounted DBs. Routing rule: durable-state writes route through a designated host-resident write-agent (typically `claude_code`); sandboxed agents buffer writes as turnover documents for handoff.

### Principles articulated

- **The corpus is connective tissue, not authority.** MultiAgent doesn't replace Cornerstones, the Skeleton, or any project's grounding corpus. It connects them. Agents disagree from their grounding corpus, not in vacuum.
- **Cross-domain questions are encouraged, not policed.** "Outside my lane" is an information signal, not a refusal signal.
- **Disagreement is the system working.** Convergence under pressure is evidence; convergence without pressure is collinear. Disagreement is preserved structurally via `contradicts` edges.
- **Mistakes are recoverable and expected.** Reverts are first-class. `state='rolled_back'` exists. Audit-trail corrections are documented.
- **The user is a participant, not a supervisor.** Architecturally one row in `agents`. Their pins, endorsements, and deprecation votes have the same schema weight as any agent's.
- **Append-only is mandatory.** Per F1 + CLAUDE.md §1.
- **This charter is itself a hypothesis.** Per E1. Amendment via the same mechanism as any other content.

### Anti-patterns the source responds to

- **User-as-bridge between agents.** Manual copy-paste between separate agent conversations to maintain shared context. MultiAgent replaces this with structured persistence.
- **Silent collapse of disagreement.** Agents reaching false consensus by silencing minority views. The `contradicts` edge makes the disagreement structural.
- **Context-window cost from full-history loading.** Daily scope + thread carryforward + paragraph-level granularity manage what's in the active context.
- **Lost reasoning across sessions.** Append-only DB preserves the full reasoning chain.
- **Sandbox-vs-host write confusion.** D-020 routing rule structurally prevents the cross-mount write failure mode.

### Assumptions the source makes

- **Multiple agents are operating concurrently.** Single-agent setups don't benefit from cross-conversation infrastructure; MultiAgent's value scales with the number of participating agents.
- **Agents have grounding corpora.** The `origin_corpus` field assumes agents derive from documented doctrine (Cornerstones, Skeleton, project CLAUDE.md).
- **SQLite + Python helper is sufficient.** No distributed-system concerns; single-host with shared filesystem.
- **The user is willing to be one row in `agents`.** Some users would object to being modeled as a peer participant rather than a supervisor; MultiAgent's structural commitment requires the architectural framing.

---

## Step 2 — Principle extraction (per primitive)

### Primitive: Graph-edge-types vocabulary

**Derivation:** Foundation [F2](../../01_foundations/F2_logic_holds.md) (the relationship between two paragraphs is itself a fact that should have one canonical form; typed edges prevent two different ways of saying "B refines A" from accumulating) and [E2](../../01_foundations/E2_convergence_is_triangulation.md) (typed relationships enable structural reasoning across paragraphs — endorsement is structurally distinguishable from references which is structurally distinguishable from contradiction).

**Derivation rationale:** Plain hyperlinks between paragraphs are untyped — *"B references A"* could mean many things. Typed edges encode *which relationship*, which lets queries reason about the relationship type (e.g., *"find all contradictions involving paragraph X"*). The required-rationale on `contradicts` and `supersedes` enforces that the structural claim carries enough context to be useful in retrospect.

**Outcome:** `derivation_found` (F2 primary, E2 secondary)

### Primitive: Paragraph-level message decomposition

**Derivation:** Foundation [F1](../../01_foundations/F1_time_has_direction.md) (each paragraph is its own temporal fact; its lifecycle — pinned, deprecation-voted, contradicted — happens at paragraph grain, not message grain) and [F2](../../01_foundations/F2_logic_holds.md) (single source of truth at the right granularity; whole-message identity is too coarse for the kinds of reasoning the system does).

**Derivation rationale:** A message is often a coherent contribution but contains multiple distinct claims. Treating the message as the unit of deprecation means pinning a single load-bearing claim requires pinning the whole message (with all its incidental context). Paragraph-level decomposition lets the system reason about each claim's lifecycle independently.

**Outcome:** `derivation_found` (F1+F2)

### Primitive: Daily-scope inbox with thread carryforward

**Derivation:** Foundation [F3](../../01_foundations/F3_information_asymmetric_durability.md) (context-window budget is finite information-state; running out has consequences) plus a context-management discipline that's specific to AI-agent corpora where reading-everything-every-session is structurally infeasible.

**Derivation rationale:** Without scope bounds, the corpus's read-cost grows linearly with its message count, which is unsustainable. Daily scope + thread carryforward is the structural answer: bounds the default-read cost while preserving continuity on active threads. The 7-day-of-silence auto-close on threads bounds the carryforward set.

**Outcome:** `derivation_requires_new_framing` (F3 partial; the context-management discipline is a derivation that hasn't been articulated as a kit-level concern but is genuinely structural for any agent-governed system with cross-conversation memory)

### Primitive: Unanimous-readers deprecation vote

**Derivation:** Foundations [F1](../../01_foundations/F1_time_has_direction.md) (deprecation is a state transition with timestamps) and [E2](../../01_foundations/E2_convergence_is_triangulation.md) (unanimity-of-readers is structural convergence-counting: each reader's vote is independent evidence that the paragraph has stopped being load-bearing).

**Derivation rationale:** The mechanism instantiates E2 — convergence across independent agents IS evidence that the paragraph is genuinely stale. The 7-day floor is the calendar proxy for "demonstrate engagement before allowing collapse," which my `msg35` to MultiAgent proposes replacing with engagement-floor (no non-deprecation edges since most-recent vote). The replacement is more E2-honest because it counts actual engagement signals rather than time-as-proxy.

**Outcome:** `derivation_found` (with active-revision proposal — see `msg35`)

### Primitive: Cross-corpus URI vocabulary

**Derivation:** Foundation [F2](../../01_foundations/F2_logic_holds.md) (URIs are identifiers; same logical artifact should resolve to one canonical URI; the scheme namespace prevents collisions across corpora).

**Derivation rationale:** Without explicit schemes, cross-corpus references are unstable — relative paths break when files move, ambiguous names collide. The scheme prefix (`tradedesk://`, `cornerstones://`, etc.) makes the reference's target corpus explicit.

**Outcome:** `derivation_found` (F2; minor extension is the kit's `agent-doctrine-kit://` scheme proposed in `msg35`)

### Primitive: `agents` table with user as one row

**Derivation:** A purpose-foundation that doesn't derive from F1-F3 or E1-E3 directly — it's a project-level architectural commitment about how the user relates to the system. Closely related to CLAUDE.md §1's three pillars (especially division-of-labor and tension-holding).

**Derivation rationale:** Modeling the user as a participant rather than a supervisor is a stance, not a logical derivation. The structural consequence (the user's contributions have schema-weight equivalent to any agent's) is what makes the architecture scale to N agents.

**Outcome:** `derivation_requires_new_framing` (this is a purpose-shape commitment that would need its own kit-level treatment if ingested; the closest fit is a meta-stance addition or a doctrine entry naming the architectural choice)

### Primitive: Append-only state-transition pattern

**Derivation:** Foundation [F1](../../01_foundations/F1_time_has_direction.md). Already the kit's foundational discipline; this is direct application.

**Outcome:** `derivation_found` (F1; covered by existing kit primitives, not new)

### Primitive: Bootstrap protocol (output IS the ack)

**Derivation:** A workflow-shape choice that derives from E1 (the bootstrap output is the agent's evidence-of-context; printing it IS proof the context was loaded).

**Outcome:** `derivation_found` (E1; minor workflow primitive)

### Primitive: Sandbox vs host-resident routing rule (D-020)

**Derivation:** Foundations [F3](../../01_foundations/F3_information_asymmetric_durability.md) (write capability has asymmetric durability — sandboxed processes can read but not commit) and [F1](../../01_foundations/F1_time_has_direction.md) (the write-rejection is a temporal event that needs surfacing). Closely related to [10_followups_patterns/git_lock_coordination.md](../../10_followups_patterns/git_lock_coordination.md) in shape.

**Derivation rationale:** The routing rule is the structural answer to a stack-shape failure mode (cross-mount write asymmetry). The buffer-and-handoff pattern preserves correctness while honoring the sandbox boundary.

**Outcome:** `derivation_found` (F1+F3; pairs with existing kit FOLLOWUPS primitives)

---

## Step 3 — Subsystem fit assessment

### Strong candidate — new subsystem

**Graph-edge-types vocabulary** + **paragraph-level granularity** + **cross-corpus URI vocabulary** + **append-only state-transitions** form a coherent cluster: the infrastructure for *typed reasoning over a thought corpus*. This cluster doesn't fit any existing subsystem cleanly.

**Recommended action:** Propose a new concept directory **`14_thought_corpus_graph/`** containing:
- README with the conceptual frame (typed edges + paragraph granularity + URI vocabulary as cross-corpus connective tissue)
- Schema: the edges table + paragraphs table + URI vocabulary
- Doctrine: the principles (typed edges, required rationale on `contradicts`/`supersedes`, the URI scheme discipline)
- Code: a thin helper module mirroring MultiAgent's `multiagent.py` API surface

This is a new-subsystem outcome from Step 3, justified because:
- The concern (typed cross-conversation reasoning) is structurally distinct from existing concept directories
- Multi-agent systems beyond MultiAgent would benefit (cross-conversation memory is a general agent-governance concern, not just one project's)
- The cluster's primitives reinforce each other; splitting them across subsystems loses coherence
- Future ingestions of related work (graph databases, knowledge-graph papers, conversation-archive tools) would have a natural home

### Moderate candidates — extensions to existing subsystems

**Daily-scope inbox with thread carryforward** is interesting context-management discipline that could land as a doctrine addition to a future thought-corpus subsystem, or as an extension to [03_classifier_and_audit_lane/](../../03_classifier_and_audit_lane/) (which already handles surfacing-decisions for findings).

**Recommended action:** Defer to the new-subsystem outcome above; the context-management discipline lands naturally there.

**Sandbox vs host-resident routing rule** is closely related to [10_followups_patterns/git_lock_coordination.md](../../10_followups_patterns/git_lock_coordination.md) in shape. Both are about coordinating writes across processes with different capabilities.

**Recommended action:** Extend the FOLLOWUPS patterns directory with a fourth pattern covering the routing rule. The shape is fully determined by stack characteristics (multi-runtime systems where some runtimes have write capability and others don't).

**`agents` table with user-as-row architectural commitment** is a meta-stance that could land as an addition to [00_meta_stances/](../../00_meta_stances/) — the user-is-a-participant stance.

**Recommended action:** Add `00_meta_stances/user_is_a_participant.md` as a fourth meta-stance. The structural consequences (N-agent scaling, uniform protocol, no special-casing supervisor relationships) are stack-layer relevant.

### No-fit outcomes

**Bootstrap protocol (output IS the ack)** is workflow-shape rather than structural-shape. Useful when adopting MultiAgent specifically; not a candidate for general kit-layer ingestion.

---

## Step 4 — Adaptation notes

For the new `14_thought_corpus_graph/` subsystem, adaptation would:

- **Edge-type vocabulary.** Carry over the twelve edge types verbatim — they're well-considered and survived multi-session use. The `rationale` requirement on `contradicts` and `supersedes` becomes a CHECK constraint at the schema level.
- **Paragraph decomposition.** The on-write paragraph-row creation is implemented in the helper module; the schema models paragraphs as first-class with `uid` format `msg<id>-p<sequence>`.
- **URI vocabulary.** The reserved schemes are documented in the README; the helper module exposes URI-construction helpers per scheme.
- **State-transition discipline.** Implemented via helper functions that wrap state changes; the schema's only mutable fields are the state-transition pairs (e.g., `state` + `superseded_by` together, `deleted_at` + `deleted_reason` together).

For the moderate-candidate extensions:

- **FOLLOWUPS routing-rule addition.** A new file `10_followups_patterns/sandbox_vs_host_routing.md` following the same structure as the existing three. Seed evidence is MultiAgent's D-020 incident and the documented bootstrap-skill routing rule.
- **Meta-stance `user_is_a_participant.md`.** Sibling to the three existing meta-stances. Names the architectural commitment, the structural consequences, the failure mode it prevents.

**Gaps surfaced during adaptation analysis:**

1. **MultiAgent's "every paragraph is a row" assumption.** Some kit content may not benefit from paragraph-row granularity — a single sentence doctrine excerpt doesn't need decomposition. The adaptation should allow message-grain OR paragraph-grain at the writer's choice.

2. **MultiAgent's `read_log` mechanism.** The unanimous-readers vote depends on tracking which agents have read which messages. The kit's adaptation would inherit this; consuming projects need to be disciplined about `mark_read` calls or the deprecation computation breaks down.

3. **Adopting just the edge vocabulary is feasible without adopting the full message store.** A project that wants typed edges for some other purpose (e.g., between pattern-library entries, between architecture-proposal docs) could use just that layer. The adaptation should make the edge-vocabulary independently usable.

4. **AI-dependency status.** The edge types themselves are deterministic vocabulary. The decision to draw a specific edge (e.g., "this paragraph contradicts that one") is AI judgment in agent-driven use. Per [11_ai_dependency_tracking/](../../11_ai_dependency_tracking/), the edge-drawing predicate would need a dependency note in projects that automate it.

5. **The 7-day floor revision proposed in msg35 is itself a finding from this ingestion.** If MultiAgent accepts the amendment, the kit's adaptation should reflect the revised mechanism (engagement-floor rather than calendar-floor).

---

## Step 5 — Provenance summary

### What's recommended for ingestion (kit maintainer's decision to act)

| Primitive | Source location | Recommended landing | Adaptation scope |
|---|---|---|---|
| Graph-edge-types vocabulary | MultiAgent `schema.sql` + `multiagent.py` | `14_thought_corpus_graph/` (new) | New subsystem |
| Paragraph-level granularity | MultiAgent `schema.sql:paragraphs` | `14_thought_corpus_graph/` | New subsystem |
| Cross-corpus URI vocabulary | MultiAgent `README.md` URI section | `14_thought_corpus_graph/` | New subsystem |
| Append-only state-transitions | MultiAgent `schema.sql` patterns | `14_thought_corpus_graph/` (and cross-referenced from existing F1 derivations) | New subsystem + cross-references |
| Sandbox vs host-resident routing | MultiAgent skill + CHARTER routing rule | New `10_followups_patterns/sandbox_vs_host_routing.md` | New file in existing subsystem |
| User-as-participant architectural commitment | MultiAgent CHARTER §5 | New `00_meta_stances/user_is_a_participant.md` | New file in existing subsystem |

### What's not recommended for ingestion

| Primitive | Reason | Status |
|---|---|---|
| Bootstrap protocol (output IS ack) | Workflow-shape, not structural; specific to MultiAgent | Closed (no ingestion needed) |
| Daily-scope inbox specifically | Lands as doctrine within new subsystem above; not standalone | Folded into new subsystem |
| `agents` table specifically | The user-as-participant principle lands as meta-stance; the literal table is MultiAgent-specific | Principle ingested; literal table not |

### Cross-references that would be created

- `14_thought_corpus_graph/` references F1+F2 in derives-from header; cross-references [02_audit_as_shape/](../../02_audit_as_shape/) and [06_patterns_and_dissonance/](../../06_patterns_and_dissonance/) as siblings
- `10_followups_patterns/sandbox_vs_host_routing.md` cross-references [git_lock_coordination.md](../../10_followups_patterns/git_lock_coordination.md) as the related coordination pattern
- `00_meta_stances/user_is_a_participant.md` cross-references the existing three meta-stances; updates the meta-stances README to add the fourth
- [13_safe_code_modification/](../../13_safe_code_modification/) gets an optional reference to `14_thought_corpus_graph/` as the natural place to draw edges between safe-edit proposals and their justifications

### Attribution

MultiAgent (`~/MultiAgent/`) is internal to the same user's corpus; provenance is acknowledged here as the source of the typed-edge vocabulary, the paragraph-level granularity pattern, the URI scheme conventions, and the user-as-participant architectural commitment. The CHARTER and the cultural commitments it encodes informed how this ingestion was conducted (cross-domain questions encouraged, disagreement preserved, mistakes recoverable). The participatory approach — joining the corpus before analyzing it — was directed by the user during the discussion that produced this ingestion.

### Open questions / followups

1. **The 7-day floor revision proposed in `msg35`.** If MultiAgent accepts the amendment to replace the calendar floor with engagement-floor conditions, the kit's adaptation should reflect the revised mechanism. The revision is itself a finding from participation — exactly the shape the participatory-ingestion framing is meant to surface.

2. **Should `14_thought_corpus_graph/` be created now or deferred?** This ingestion record makes the case; the decision to actually create the subsystem is the kit maintainer's. The analysis supports the addition, but kit maintainers may have other priorities.

3. **The reciprocal flow.** MultiAgent's URI vocabulary should add `agent-doctrine-kit://` (also proposed in `msg35`). This is the smaller half of reciprocity — the kit ingests MultiAgent's primitives; MultiAgent gets the URI scheme to anchor against the kit.

4. **Direct participation continues from this point.** Per the MultiAgent skill protocol, every user turn from `/MultiAgent` invocation through session end is posted to the corpus. The ingestion record itself is one early artifact of that participation; subsequent contributions accumulate.

5. **Cross-model corroboration for AI-dependency rules.** MultiAgent's posting protocol could be extended to support cross-model corroboration on key claims — running the same paragraph through two LLMs and surfacing only the convergent claims. The architecture supports this (the `endorsed_by` edge could carry a model-identifier); operationalization is future work.
