# Doctrine excerpt — per-edit gating vs per-finding classification

This extends the four-criteria classifier (see [four_criteria.md](four_criteria.md)) to a finer-grained sibling concern: gating individual code edits through review, not just findings.

**Origin:** Ingested from PrizmForge — see [../../12_ingestion_protocol/examples/prizmforge_ingestion.md](../../12_ingestion_protocol/examples/prizmforge_ingestion.md).

---

## Per-finding vs per-edit gating

The base classifier (four_criteria.md) operates on **findings** — dissonances, architecture proposals, integrity violations, lesson candidates. These are *meta-events* about the codebase: something was detected, named, and surfaced for triage.

PrizmForge introduces a complementary mechanism that operates on **edits** — individual file modifications proposed by an agent. The two are sibling concerns at different granularity:

- **Per-finding classification** decides: *"this finding routes to user judgment or to agent lane."*
- **Per-edit gating** decides: *"this code edit applies via the standard pipeline or requires deeper review."*

A finding may generate zero, one, or many edits when it's resolved. The classifier handles the finding's routing; the edit pipeline handles each generated edit's safety.

## The per-edit pipeline shape

PrizmForge's sequential mutation pathway: **Developer → Proposal → Reviewer → Application.** Each edit is:

1. **Drafted** by the developer agent against the file's current state, capturing the file's content-hash and targeted line-GUIDs (see [13_safe_code_modification/](../../13_safe_code_modification/) for the safety primitives).
2. **Recorded** as a proposal row with state `pending`.
3. **Reviewed** by the reviewer agent, which either:
   - Approves: state transitions to `approved`, queued for application.
   - Rejects: state transitions to `rejected` with rationale; the developer can re-draft.
4. **Applied** by the application step, which verifies the proposal is still applicable (content-hash still matches) and either writes the edit or rejects as `conflicted`.

Parallel analytical work (junior reviewer, security reviewer, archivist, report builder) runs alongside without affecting state — analysis is parallel; mutation is sequential.

## When to use per-edit gating

The pipeline is valuable when:

- **Multiple agents modify the same codebase** — the gating prevents silent overwrites and surfaces conflicts before they corrupt state.
- **Edits have consequences beyond code correctness** — security implications, performance regressions, downstream-system effects. The reviewer can apply scoped review criteria.
- **Edit volume is high enough that uniform review costs too much** — the gate allows specialization (e.g., trivial fixes route to junior reviewer; security-sensitive edits route to security reviewer).

When NOT to use per-edit gating:

- **Single-agent workflows** — one agent drafting and applying its own edits doesn't need the cross-agent coordination the pipeline provides.
- **Trivial edits with no risk surface** — purely mechanical changes (typo fixes, comment updates) may not warrant pipeline overhead. The trust ratchet (see four_criteria.md §3c) handles this at finding-level; at edit-level, equivalent ratcheting can decide which edit shapes bypass review.

## Composition with the base classifier

The two mechanisms compose:

1. A finding surfaces (integrity violation, dissonance, etc.).
2. The classifier (four_criteria.md) routes the finding to agent or user lane.
3. If routed to agent lane, the agent's resolution may include code edits.
4. Each edit flows through the per-edit pipeline.
5. The trust ratchet operates at finding-shape granularity; an edit-shape ratchet can operate independently at edit granularity (e.g., per-file-path patterns, per-edit-pattern).

This composition lets the system gate at both layers — *"is this kind of finding agent-resolvable?"* AND *"is this specific edit safe to apply?"* — without one layer subsuming the other.

## Cross-references

- [four_criteria.md](four_criteria.md) — the per-finding base classifier.
- [per_agent_vs_per_shape.md](per_agent_vs_per_shape.md) — the granularity-of-trust question this concept raises.
- [../../13_safe_code_modification/](../../13_safe_code_modification/) — the safe-editing primitives that make the application step structurally safe.
- [../../12_ingestion_protocol/examples/prizmforge_ingestion.md](../../12_ingestion_protocol/examples/prizmforge_ingestion.md) — the full ingestion record.
