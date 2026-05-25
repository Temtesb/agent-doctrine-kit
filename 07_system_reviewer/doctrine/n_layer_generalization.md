# Doctrine excerpt — N-layer generalization of the System Reviewer

The base two-layer System Reviewer doctrine (see [two_layers.md](two_layers.md)) defines Layer 1 (deterministic) and Layer 2 (AI architectural review). PrizmForge generalizes this to an N-layer review population with specialized roles: developer, primary reviewer, junior reviewer, security reviewer, archivist, report builder.

**Origin:** Ingested from PrizmForge — see [../../12_ingestion_protocol/examples/prizmforge_ingestion.md](../../12_ingestion_protocol/examples/prizmforge_ingestion.md).

---

## The two-layer pattern is one shape; N-layer is another

The kit's two-layer System Reviewer is the *minimum viable* version of structural triangulation per [E2](../../01_foundations/E2_convergence_is_triangulation.md):

- **Layer 1** catches mechanical drift via deterministic checks.
- **Layer 2** catches conceptual drift via AI architectural review.

Two layers from genuinely different angles is triangulation. Two is sufficient when the codebase's review surface is moderate and the agent population is small.

When the agent population grows and the codebase's review surface diversifies, N-layer specialization becomes feasible. PrizmForge's agent population:

- **Developer agent** — proposes edits.
- **Primary reviewer** — gates each proposal on overall safety.
- **Junior reviewer** — checks code style and routine correctness; runs in parallel as analytical agent.
- **Security reviewer** — applies threat modeling to security-sensitive edits.
- **Archivist** — preserves historical state and decision rationale.
- **Report builder** — summarizes activity for human consumption.

Each role applies *scoped review criteria* — different perspectives on the same proposal. Convergence across roles is triangulation; divergence surfaces issues no single role would catch.

## When N-layer is justified

The two-layer pattern works for most kit-derived projects. N-layer generalization is justified when:

- **Multiple agents are operating concurrently** — the agent population is already there; specialization is an organizing-cost reduction, not a new cost.
- **Review criteria genuinely differ by domain** — code-style review and security review involve different reasoning shapes; conflating them in one reviewer wastes context.
- **Specialization improves throughput** — when each specialized reviewer can review its scope faster than a generalist reviewer applying all criteria at once.
- **The codebase's risk surface diversifies** — security-sensitive code paths warrant dedicated review; routine paths don't need the same depth.

When NOT to generalize to N layers:

- **Single-agent project** — one agent serving as both developer and reviewer is fine; the conflict of interest is real but bounded.
- **Two-agent project with clear roles** — the two-layer pattern already triangulates; adding more reviewers risks producing convergence-without-pressure (more agents agreeing for the same reason).
- **The roles wouldn't have genuinely different criteria** — three reviewers all applying the same general criteria add cost without adding triangulation.

## Composition with the base two-layer pattern

N-layer specialization doesn't replace the Layer 1 / Layer 2 distinction; it extends Layer 2.

- **Layer 1 stays the deterministic CI-check layer.** Mechanical drift, contract coverage, doc-code alignment, registry consistency. One mechanism; doesn't need specialization.
- **Layer 2 generalizes from "one AI reviewer" to "an N-role review population."** Each role is a specialized version of Layer 2 — applying judgment, but with scoped criteria.

The convergence-across-roles is what E2 cares about: different agents applying different criteria reaching the same conclusion IS triangulation; reaching different conclusions IS the disagreement that surfaces real issues.

## Implementation notes

For projects adopting N-layer:

- Each role gets a dedicated prompt template that scopes its review criteria.
- Reviews run in parallel (per PrizmForge's "analysis is parallel" principle).
- A coordinator (or the primary reviewer) aggregates results and decides next action.
- Divergence between roles is preserved in the audit trail (per F1) — the disagreement is data.

Anchor the role population to the project's needs: a code-modification system needs different roles than a documentation-generation system needs different roles than a data-pipeline system. The N is not magic; it's whatever the project's review surface justifies.

## Cross-references

- [two_layers.md](two_layers.md) — the base two-layer pattern this generalizes.
- [../../03_classifier_and_audit_lane/doctrine/per_edit_gating.md](../../03_classifier_and_audit_lane/doctrine/per_edit_gating.md) — per-edit gating composes with N-layer review at the apply step.
- [../../01_foundations/E2_convergence_is_triangulation.md](../../01_foundations/E2_convergence_is_triangulation.md) — the foundation behind structural triangulation.
- [../../12_ingestion_protocol/examples/prizmforge_ingestion.md](../../12_ingestion_protocol/examples/prizmforge_ingestion.md) — the ingestion record where this generalization was first surfaced.
