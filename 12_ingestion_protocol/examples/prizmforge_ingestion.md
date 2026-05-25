# Ingestion record — PrizmForge

**Ingested on:** 2026-05-24
**Ingested by:** Initial analysis pass; worked example for the ingestion protocol
**Source artifact:** https://github.com/seakintruth/PrizmForge
**Source version:** main @ ~26 commits (at time of analysis)
**Source license:** (not yet specified at source; treat as all-rights-reserved until clarified, with attribution required)
**Status:** Analysis complete; ingestion of selected primitives recommended but not yet executed (decision left to kit maintainer per the protocol's principle that ingestion is a deliberate act)

## Why this ingestion was undertaken

PrizmForge is an autonomous multi-agent system for governed code modification. It contains primitives the kit hasn't independently derived — particularly around the mechanics of safe code editing under concurrent modification — and surfaced as a candidate for ingestion during a comparative architecture discussion. The kit's existing subsystems handle doctrine governance and audit-as-shape-of-data, but don't currently address the specific concern of *"how do you safely apply an edit to a file when other agents might be modifying it concurrently?"* PrizmForge addresses this concern directly.

This is also the seed-evidence case for the ingestion protocol itself — the first concrete artifact to run through the five steps.

---

## Step 1 — Source analysis

### Primitives identified

- **Line-GUID editing.** Each line in a tracked file gets a stable UUID. Edits reference UUIDs rather than line numbers. Surrounding insertions/deletions don't invalidate edit references.
- **Content-hash optimistic concurrency.** Before an edit is applied, the file's current content hash is compared against the hash the proposal was drafted against. Mismatch → proposal rejected as `conflicted`; no application.
- **Sequential mutation pathway.** All file modifications flow through a defined sequence: Developer (proposes) → Proposal (recorded) → Reviewer (gates) → Application (materialized to disk). Parallel paths are analytical only; mutation is sequential.
- **Multi-agent population with defined roles.** The system has multiple agent types: developer, reviewer, junior reviewer, security reviewer, archivist, report builder. Each has scoped responsibilities; parallel analysis agents inform without mutating.
- **Resource Controller.** Token-budget tracking, rate limiting, prioritization under budget constraint. Allocates AI calls across competing agent demands.
- **agent_profiles table.** Per-agent metrics tracked: tokens used, feedback value generated, efficiency. Used by the Resource Controller for adaptive prioritization.
- **Pydantic validation throughout.** All operations validated through Pydantic schemas at boundaries.
- **Post-write invalidation of overlapping proposals.** When a file changes, proposals targeting overlapping line-GUIDs in that file are automatically invalidated.

### Principles articulated

- **Mutation is sequential; analysis is parallel.** The system's safety derives from gating *every* mutation through the same review pathway, while allowing analytical work to run concurrently without affecting state.
- **Line position is volatile; line identity is stable.** A line's location can shift due to surrounding changes; its semantic identity (what it represents) shouldn't depend on its position.
- **Optimistic concurrency over locking.** Don't lock files during edit drafting; detect conflicts at application time via content hash.
- **Agent budgets are bounded; allocation must be deliberate.** Tokens, API calls, and time all have ceilings; the system makes allocation decisions explicit rather than first-come-first-served.

### Anti-patterns the source responds to

- **Line-number-based diffs becoming stale.** A diff drafted against lines 50-55 becomes invalid when an earlier edit inserts 10 lines above; the diff applies to the wrong place.
- **Last-write-wins overwriting concurrent work.** Two agents editing the same file without coordination — one of their edits silently loses.
- **Reviewer-as-bottleneck under uniform gating.** Every change requiring the same level of review regardless of risk; review becomes the rate limiter.
- **Token-budget exhaustion mid-operation.** Running out of API budget partway through a multi-step operation leaves the system in inconsistent state.

### Assumptions the source makes

- **The system is multi-agent.** Single-agent projects don't need the proposal/review pipeline; PrizmForge's value scales with the number of concurrent modifiers.
- **Files are line-structured text.** Line-GUIDs are line-granular; the approach doesn't naturally extend to binary files or to non-line-structured formats (though the underlying concept of stable identifiers could).
- **Modification is the primary workload.** Read-only or read-mostly workloads don't benefit from the editing-safety primitives; PrizmForge's overhead pays off when modifications are frequent.
- **Python 3.12+, SQLite, and an LLM endpoint are available.** Standard PrizmForge runtime requirements.

---

## Step 2 — Principle extraction (per primitive)

### Primitive: Line-GUID editing

**Source description:** Each line in a tracked file gets a stable UUID. Edits reference UUIDs; surrounding changes don't invalidate edit references.

**Derivation:** Foundation [F2](../../01_foundations/F2_logic_holds.md) (single source of truth: the GUID is the canonical identifier for the line, not the line's position which is volatile and can disagree between read time and write time).

**Derivation rationale:** F2 requires that a given fact have one value. A line's identity is the fact; the line's position is a property of the file's current state. Conflating identity with position means two readers can have different "true" answers about which line is which — a non-contradiction violation at the file-modification layer. The line-GUID separates identity from position, restoring single-source-of-truth for line identity. Further: per F1 (time has direction), the GUID-to-content mapping IS the temporal record; later mutations are correctly attributed to the GUID, preserving the audit trail.

**Outcome:** `derivation_found` (F2 primary, F1 secondary)

### Primitive: Content-hash optimistic concurrency

**Source description:** Before an edit is applied, the file's current content hash is compared against the hash the proposal was drafted against. Mismatch → proposal rejected as `conflicted`.

**Derivation:** Foundations [F1](../../01_foundations/F1_time_has_direction.md) and [F2](../../01_foundations/F2_logic_holds.md). F2 because the proposal's assumptions about the file's state must still hold at application time — otherwise the proposal is acting on a file that no longer exists in the form it assumed (non-contradiction violation). F1 because the file's state at proposal-draft time and the file's state at apply time are two distinct temporal facts; the hash makes the difference between them queryable.

**Derivation rationale:** The mechanism is exactly the F1+F2 pair applied to "is the world I'm acting on still the world I assumed?" Locking-based concurrency would also satisfy this, but at the cost of contention. The hash-comparison approach honors the foundations without serializing access.

**Outcome:** `derivation_found` (F1+F2 jointly)

### Primitive: Sequential mutation pathway

**Source description:** All file modifications flow through Developer → Proposal → Reviewer → Application. Parallel paths are analysis-only.

**Derivation:** Foundation [E1](../../01_foundations/E1_corpus_is_hypothesis.md) (every proposed change is a hypothesis that needs verification before becoming load-bearing) plus the meta-stance [prefer enforcers over principles](../../00_meta_stances/prefer_enforcers_over_principles.md) (the sequential pathway is a structural enforcer that makes the hypothesis-verification gate impossible to bypass).

**Derivation rationale:** The principle "untested code shouldn't ship" is universally accepted; PrizmForge instantiates it as a structural pathway rather than a documentation principle. The interesting derivation choice: by making mutation sequential and analysis parallel, PrizmForge surfaces the *epistemic asymmetry* between proposing and verifying — propose-many-things-in-parallel is fine because proposals are hypotheses; mutate-in-parallel is unsafe because mutations are facts.

**Outcome:** `derivation_found` (E1 primary, prefer-enforcers meta-stance as method)

### Primitive: Multi-agent population with defined roles

**Source description:** Developer, Reviewer, Junior Reviewer, Security Reviewer, Archivist, Report Builder — each with scoped responsibilities.

**Derivation:** Foundation [E2](../../01_foundations/E2_convergence_is_triangulation.md) (independent agents probe from different angles; convergence across roles is triangulation; divergence between roles surfaces issues no single agent would catch).

**Derivation rationale:** The role-defined agent population is the operational form of E2 — different evaluators apply different criteria. The kit's [07_system_reviewer/](../../07_system_reviewer/) has a two-layer version of this (deterministic Layer 1 + judgment Layer 2); PrizmForge has an N-layer version with finer-grained specialization.

**Outcome:** `derivation_found` (E2; closely related to the kit's existing two-layer System Reviewer)

### Primitive: Resource Controller

**Source description:** Token-budget tracking, rate limiting, prioritization under constraint.

**Derivation:** Foundation [F3](../../01_foundations/F3_information_asymmetric_durability.md) (AI budget is finite information-state; running out has persistent consequences — failed operations, partial state, incomplete work) plus project-purpose foundations around cost discipline that any AI-consuming project will declare.

**Derivation rationale:** Token budgets are an instance of finite resource with asymmetric durability — you can't "un-spend" tokens already burned. The Resource Controller is the structural mechanism that makes the budget bound load-bearing rather than aspirational.

**Outcome:** `derivation_found` (F3 + project-purpose foundations)

### Primitive: agent_profiles tracking

**Source description:** Per-agent metrics: tokens used, feedback value, efficiency.

**Derivation:** Foundation [F1](../../01_foundations/F1_time_has_direction.md) (the agent's behavior over time is a temporal fact that must be queryable) plus an interesting partial overlap with the kit's trust ratchet ([03_classifier_and_audit_lane/](../../03_classifier_and_audit_lane/)) — but PrizmForge's tracking is per-*agent*, not per-*change-shape*. The kit's framing argues per-shape is the right grain.

**Derivation rationale:** This is a case where the source's primitive (per-agent metrics) and the kit's primitive (per-shape trust) are addressing related concerns with different granularities. Ingestion would benefit from naming this difference rather than choosing one — both granularities have value in different contexts. The kit's framing is opinionated about per-shape being structurally superior because trust survives agent turnover; PrizmForge's framing optimizes for understanding individual agent contribution. Both are valid; the kit might want to offer both as composable primitives.

**Outcome:** `derivation_requires_new_framing` (F1 + the per-shape-vs-per-agent distinction needs articulating as a kit-level discipline)

### Primitive: Pydantic validation throughout

**Source description:** All operations validated through Pydantic schemas at boundaries.

**Derivation:** Foundation [F2](../../01_foundations/F2_logic_holds.md) applied to API contracts (the contract has one canonical shape; deviation is non-contradiction).

**Derivation rationale:** This is a stack-specific choice (Pydantic) implementing a stack-agnostic principle (validate inputs at boundaries). The kit's "Errors" / "Interface" subsystem space already covers this concern; ingestion would be a minor extension (or just a stack-choice note).

**Outcome:** `derivation_found` (F2; minor stack-specific extension)

### Primitive: Post-write invalidation of overlapping proposals

**Source description:** When a file changes, proposals targeting overlapping line-GUIDs are automatically invalidated.

**Derivation:** Foundation [F1](../../01_foundations/F1_time_has_direction.md) (post-write is a temporal event; downstream state must reflect it) plus consistency with the content-hash concurrency primitive above.

**Derivation rationale:** This is the natural complement to content-hash concurrency — instead of detecting the conflict at apply-time and rejecting one proposal, the system can detect overlap at change-time and invalidate dependent proposals proactively. It's the same F1+F2 concern at a different point in the lifecycle.

**Outcome:** `derivation_found` (F1+F2; pairs with content-hash primitive)

---

## Step 3 — Subsystem fit assessment (per primitive)

### Strong candidates for ingestion

**Line-GUID editing** and **content-hash optimistic concurrency** are mutually-reinforcing primitives that don't currently have a home in the kit. They share concerns (safe editing under concurrent modification) and their value is greatest when both are present.

**Recommended action:** Propose a new concept directory **`13_safe_code_modification/`** containing both primitives, anchored to F1+F2. Files would be README + schema (the line-GUID tracking table) + doctrine (the principles around line identity stability and optimistic concurrency) + code (the helper functions for hashing and GUID assignment).

This is a new-subsystem outcome from Step 3, justified because:
- The concern is structurally distinct from the kit's existing concept directories
- It applies broadly to any agent-modified codebase regardless of multi-agent shape
- The primitives are simple enough to implement cleanly in the kit's idiom
- Future ingestions of related work (collaborative-editing CRDTs, semantic merge tools, etc.) would have a natural home

**Post-write invalidation** would also land in `13_safe_code_modification/` as the lifecycle complement to content-hash concurrency.

### Moderate candidates

**Sequential mutation pathway** is interesting but its fit is less clear. The principle (gate every mutation through a review pathway) is universally applicable, but the *specific shape* (Developer → Proposal → Reviewer → Application as named stages) is opinionated about workflow.

**Recommended action:** Extend [03_classifier_and_audit_lane/](../../03_classifier_and_audit_lane/) with an addition that explicitly addresses *per-edit* mutation gating, distinct from the existing per-*finding* classification. The current kit covers "how do you classify a finding for routing"; PrizmForge's pathway covers "how do you gate every code edit through review." Related concerns but different grain.

This is a subsystem-extension outcome from Step 3.

**Multi-agent population** has clear derivation (E2) but its fit depends on the consuming project's shape. The kit's [07_system_reviewer/](../../07_system_reviewer/) has the two-layer version that captures the essential pattern; the N-role version (junior/security/archivist/report builder) is project-shape specific.

**Recommended action:** Update [07_system_reviewer/](../../07_system_reviewer/) with a section noting that the two-layer structure can be generalized to N layers for projects with multi-agent populations, citing PrizmForge as the worked example. Don't ingest the specific role taxonomy — let consuming projects derive their own role structure if they need one.

**Resource Controller** partially overlaps with the AI subsystem the kit's source skeleton already has (NewProjectSkelleton Subsystem 8). The skeleton's AI subsystem covers cost tracking and rate limiting at a basic level; PrizmForge adds adaptive prioritization under budget constraint.

**Recommended action:** Extend the AI subsystem (or add an adjacent one) with the adaptive-prioritization primitive. This is a clear minor extension.

### Marginal candidates

**agent_profiles tracking** raised the per-agent-vs-per-shape distinction. Both have value; neither subsumes the other.

**Recommended action:** Add a doctrine entry to [03_classifier_and_audit_lane/](../../03_classifier_and_audit_lane/) explicitly naming both granularities and when each is appropriate. The kit currently advocates per-shape (and gives strong reasons); the addition would acknowledge that per-agent has complementary value and the two can coexist.

**Pydantic validation throughout** is a stack-choice (Pydantic specifically) implementing a principle the kit already covers.

**Recommended action:** No ingestion. The principle (validate at boundaries) is in the kit; the tool choice (Pydantic) is project/stack-layer and doesn't earn its own elevation.

### No-fit outcomes

None at this analysis depth. All identified primitives have at least a moderate path to ingestion. This is itself a finding worth noting — PrizmForge and the kit are operating in genuinely complementary spaces with little redundant coverage.

---

## Step 4 — Adaptation notes (per primitive to be ingested)

For the strong candidates (line-GUID editing + content-hash concurrency), adaptation would involve:

- **Line-GUID assignment.** PrizmForge assigns UUIDs at file-tracking-init time; adaptation would honor the kit's idiom of declarative-vocabulary files (the GUID-to-line-content mapping is reference data, not behavior).
- **Hash comparison at apply time.** Implementation as a context manager or decorator that wraps any edit application, mirroring the kit's existing decorator patterns ([04_pre_flight_and_invariants/](../../04_pre_flight_and_invariants/) for the ratchet style).
- **Schema for line-GUID tracking.** A SQLite table storing `(file_path, line_guid, current_line_number, line_content_hash, last_modified)`. Indexed for efficient lookup at both proposal-draft time and apply time.
- **Cross-references.** The safe-code-modification subsystem cites F1+F2 in its derives-from header. The audit-as-shape-of-data subsystem ([02_audit_as_shape/](../../02_audit_as_shape/)) should cross-reference safe-code-modification as the line-grain complement to its row-grain audit primitives.

**Gaps surfaced during adaptation analysis:**

1. **PrizmForge doesn't specify how line-GUIDs interact with binary files or whitespace-significant formats.** The kit's adaptation would need to either match this limitation or explicitly extend it.

2. **PrizmForge's conflict resolution is reject-as-conflicted.** No automatic merge attempt. The kit's adaptation should preserve this conservatism (per the [hypothesis posture](../../00_meta_stances/hypothesis_posture.md) — automatic conflict resolution requires confidence the kit hasn't yet earned).

3. **PrizmForge doesn't address how line-GUIDs themselves are versioned.** If the GUID-assignment algorithm changes, existing line-GUIDs need to remain valid. The kit's adaptation should include a versioning header on the GUID-tracking table (per F1 — schema evolution is itself a fact subject to F1).

4. **AI-dependency status of GUID assignment.** If GUID assignment is deterministic (hash of original content + timestamp), no AI dependency. If GUID assignment uses any AI judgment (e.g., semantic line identity), the [11_ai_dependency_tracking/](../../11_ai_dependency_tracking/) discipline applies. PrizmForge's docs aren't entirely clear; the adaptation should default to fully-deterministic.

---

## Step 5 — Provenance summary

### What would be ingested (if the kit maintainer approves)

| Primitive | Source location | Landed at | Adaptation scope |
|---|---|---|---|
| Line-GUID editing | PrizmForge `file_editing/` | `13_safe_code_modification/` (new) | New subsystem |
| Content-hash optimistic concurrency | PrizmForge `core/` | `13_safe_code_modification/` | New subsystem |
| Post-write invalidation | PrizmForge `core/` | `13_safe_code_modification/` | New subsystem (paired with above) |
| Sequential mutation pathway (per-edit gating) | PrizmForge `workflow/` | Extension to `03_classifier_and_audit_lane/` | Subsystem extension |
| N-layer reviewer generalization | PrizmForge `agents/` | Extension to `07_system_reviewer/` | Subsystem extension |
| Adaptive prioritization under budget | PrizmForge `core/` | Extension to source skeleton's AI subsystem | Subsystem extension |
| Per-agent vs per-shape trust granularities | PrizmForge `audit/` | Extension to `03_classifier_and_audit_lane/` | Doctrine addition |

### What would NOT be ingested

| Primitive | Reason | Status |
|---|---|---|
| Pydantic-specific validation | Stack-tool choice; principle already covered | Closed (no ingestion needed) |
| Specific role taxonomy (junior/security/archivist) | Project-shape specific; generalization is what's worth ingesting | Closed (covered by N-layer generalization above) |

### Cross-references that would be created

- `13_safe_code_modification/` references F1 and F2 in its derives-from header
- [02_audit_as_shape/](../../02_audit_as_shape/) gets cross-reference to `13_` as the line-grain complement to its row-grain audit
- [03_classifier_and_audit_lane/](../../03_classifier_and_audit_lane/) extended with per-edit gating section, cross-referencing PrizmForge
- [07_system_reviewer/](../../07_system_reviewer/) extended with N-layer generalization note, cross-referencing PrizmForge

### Attribution

PrizmForge by seakintruth (https://github.com/seakintruth/PrizmForge) is the source for the safe-code-modification primitives. The line-GUID and content-hash-concurrency mechanisms originated there; the kit's adaptation translates them into the kit's structural idiom (foundations-anchored, ratchet-patterned, doctrine-documented). The intellectual debt is acknowledged here; specific cross-references will live in the adapted subsystem files.

### Open questions / followups

1. **Should `13_safe_code_modification/` be added now or deferred?** The analysis supports the addition, but the decision to actually create the subsystem is the kit maintainer's. This ingestion record makes the case; it doesn't make the change.

2. **License clarification needed.** PrizmForge's repo doesn't currently specify a license. Before any code-level adaptation, the kit should reach out to clarify whether the source allows derivative work and under what terms.

3. **PrizmForge as an ongoing dialog partner.** The patterns the kit doesn't currently address that PrizmForge does (per-edit safety, multi-agent populations) suggest reciprocal ingestion may also be appropriate — PrizmForge might benefit from ingesting some of the kit's primitives (audit-as-shape-of-data, hypothesis posture, AI-dependency tracking). The agent-doctrine-kit repo itself was shared with PrizmForge as a starting point for that direction.

4. **The per-agent vs per-shape trust question.** This needs more analysis before ingestion. The kit's current position favors per-shape strongly; PrizmForge's existence suggests per-agent has more value than that position acknowledges. A future kit revision could synthesize both granularities into a richer trust framework.

5. **Versioning the line-GUID algorithm.** Adaptation gap surfaced in Step 4 — the algorithm itself needs a version field on the tracking table. The schema design should incorporate this from the start rather than retrofit later.
