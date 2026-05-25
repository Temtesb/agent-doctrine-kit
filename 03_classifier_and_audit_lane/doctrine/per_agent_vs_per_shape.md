# Doctrine excerpt — per-agent vs per-shape trust granularities

The base classifier doctrine (four_criteria.md §3c) advocates per-*shape* trust: trust accrues to a fingerprint of `(finding_source_type, governing_principle, change_pattern)`, not to the individual agent producing the work.

PrizmForge's `agent_profiles` table tracks per-*agent* trust: tokens used, feedback value generated, efficiency per agent. The two are not in conflict — they're complementary granularities.

**Origin:** Ingested from PrizmForge — see [../../12_ingestion_protocol/examples/prizmforge_ingestion.md](../../12_ingestion_protocol/examples/prizmforge_ingestion.md).

---

## Both granularities have value; neither subsumes the other

**Per-shape trust** (the kit's existing position):

- **Strengths:** Survives agent turnover. A new agent immediately benefits from accumulated trust on well-understood shapes. Distinguishes risk by change-type rather than by who-made-it.
- **Weaknesses:** Doesn't capture "this specific agent is reliable" signal. A consistently-strong agent gets no benefit from its track record beyond what it contributes to shape-level accumulation. A consistently-weak agent's individual issues are invisible.

**Per-agent trust** (PrizmForge's position):

- **Strengths:** Captures agent-specific reliability. Useful for budget allocation (the Resource Controller can prefer high-feedback agents under constraint). Surfaces individual agent issues (an agent producing repeatedly-rejected proposals can be calibrated or retired).
- **Weaknesses:** Doesn't survive agent turnover (new agent starts at zero regardless of shape-pattern maturity). Risks creating a popularity contest among agents rather than measuring change-type safety.

## When to use which

- **Per-shape** for *routing decisions* — should this kind of finding go to agent lane or user lane? Should this kind of edit bypass review? The shape-level trust is what's load-bearing here.

- **Per-agent** for *resource allocation* — under budget constraint, which agents should get priority? Which agents need calibration? Which agents are accumulating costs without producing value? The agent-level metrics inform these decisions.

- **Both, in combination** for *post-mortem analysis* — *"this shape failed three times; was it the same agent each time, or different agents?"* The per-shape signal surfaces the failure mode; the per-agent breakdown surfaces whether the cause is an individual agent's issue or a structural shape problem.

## Recommended implementation

A kit-derived project that wants both granularities adds two complementary tables:

```sql
-- Per-shape trust (existing kit recommendation)
-- Lives in the auto_resolutions table aggregated by:
--   (finding_source_type, governing_principle, change_pattern)

-- Per-agent trust (PrizmForge-inspired)
CREATE TABLE agent_profiles (
    agent_id TEXT PRIMARY KEY,
    tokens_used INTEGER DEFAULT 0,
    feedback_value_generated REAL DEFAULT 0,
    proposals_drafted INTEGER DEFAULT 0,
    proposals_approved INTEGER DEFAULT 0,
    proposals_rejected INTEGER DEFAULT 0,
    proposals_rolled_back INTEGER DEFAULT 0,
    last_active_at TEXT,
    notes TEXT
);
```

The Resource Controller (or equivalent budget-allocation mechanism) reads `agent_profiles` for prioritization decisions; the classifier and trust ratchet read `auto_resolutions` aggregations for routing decisions. The two pipelines stay independent and don't compete.

## What this doctrine does NOT mean

- **Per-shape isn't deprecated.** The kit's primary trust mechanism remains per-shape; per-agent is a complementary signal, not a replacement.
- **Per-agent isn't unconditional.** An agent's per-agent metrics are themselves a hypothesis (per [01_foundations/E1_corpus_is_hypothesis.md](../../01_foundations/E1_corpus_is_hypothesis.md)). Agents whose metrics look strong but whose actual contributions are problematic surface that via the per-shape view (the shapes they produce get rolled back); the system shouldn't blindly trust per-agent scores.

## Cross-references

- [four_criteria.md](four_criteria.md) — the base classifier with per-shape trust ratchet.
- [per_edit_gating.md](per_edit_gating.md) — the per-edit pipeline that benefits from both granularities.
- [../../12_ingestion_protocol/examples/prizmforge_ingestion.md](../../12_ingestion_protocol/examples/prizmforge_ingestion.md) — the ingestion record where this granularity question was first surfaced.
