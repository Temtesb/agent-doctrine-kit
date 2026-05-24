# Doctrine excerpt — the classifier's four criteria

Place this in your governance doc as the agent-vs-user classification policy. Adapt the doctrine pointers and severity examples to your project's domain.

---

## Agent-resolvable vs. user-required routing

**Derives from:** Foundations [F2](../../01_foundations/F2_logic_holds.md) (single classifier verdict per finding) and [E2](../../01_foundations/E2_convergence_is_triangulation.md) (trust ratchet as structural convergence-counting).

Every finding (dissonance, architecture proposal, integrity violation, lesson candidate) routes to one of two lanes:

- **Agent lane** — the agent acts on the finding directly; the action lands with an `auto_resolutions` row; the user sees a digest, not item-by-item approvals.
- **User lane** — the finding routes to the user's decision queue; the user makes the call.

The classification is mechanical, not discretionary. The criteria below are the gate.

### Agent-resolvable — all four must hold

A finding is **agent-resolvable** if and only if all four of these criteria are satisfied:

1. **Doctrine names the answer.** A clause in this project's doctrine, the stack-layer doctrine, or the universal foundations unambiguously specifies the fix shape for this class of change. *"The doctrine could be interpreted to support the fix"* does not satisfy this criterion; the bar is *"the doctrine names this fix shape"*.

2. **A pattern exists to mirror.** The codebase or pattern library contains at least one prior implementation of this fix shape. Greenfield work without precedent does not satisfy this criterion — the agent has no template to follow that has survived contact with reality.

3. **Verification is mechanical.** An architecture invariant test, integrity check, contract test, or existing test suite verifies the change's correctness without subjective judgment. *"The change looks right"* does not satisfy this criterion; the bar is *"a test passes or fails to confirm"*.

4. **Being wrong is reversible.** The change is contained in code or schema; `git revert` undoes it; the change does not commit money, publish customer-facing content, delete historical data, modify security/access controls, or take any other action with persistent external consequences.

If any of the four is false, the finding routes to user.

### User-required — any of these triggers forces user routing

A finding routes to **user-required** if any of these apply, regardless of the four-criteria gate:

- **Taxonomy decision** — what category should exist; what a status value means; what doctrine clauses should say. The system can produce candidates; only the user decides.
- **Calibration against physical reality** — whether an AI identification matches the actual object; whether a measurement is correct; whether an external system's output reflects the world.
- **Business priority** — a target rate, a tolerance threshold, a strategic emphasis between competing valid options.
- **Doctrine change** — modification of universal foundations or project-layer rules, or addition of new ones.
- **High-stakes irreversible action** — real money out, real customer-facing publication, deletion of historical data, modification of security or access controls.
- **Cross-layer change** — a change at the universal or stack layer (vs. project layer). The elevation protocol governs these explicitly; they route to user as part of that protocol.

### Default at the boundary

When fewer than four agent-resolvable criteria pass AND no user-required trigger clearly fires, the finding routes to user. **Conservative bias at the ambiguous boundary** is preserved — the right place for it.

### The classifier's output

For each finding the classifier produces:

- `requires_user_judgment: bool` — the routing decision
- `classifier_criteria_met: dict` — which criteria fired (for audit and ratchet)

Both are recorded on the finding (or on the `auto_resolutions` row, if the agent acts on it). The `classifier_criteria_met` field is what the trust ratchet groups by; rolled-back resolutions are evidence that the criteria as written produced the wrong call for that shape.

## The trust ratchet — when do shapes earn reduced surfacing?

Trust is keyed on **change shape**, not actor: the fingerprint of `(finding_source_type, governing_principle, change_pattern)`.

- **N=5 default threshold:** after 5 resolutions of the same shape, with 0 reverts, the shape is "trusted."
- **Trusted shapes stop appearing in the daily digest.** Their resolutions still land in `auto_resolutions` and remain revertable; the surface stops surfacing them.
- **Any revert event resets trust to 0 for that shape** and re-engages digest surfacing.
- **Trust can be earned, lost, and re-earned.** The full history is in `auto_resolutions`; the ratchet's current state is a projection over that history (per F1, no overwriting).

### Implementation as a query

The ratchet doesn't need its own table. It's a query against `auto_resolutions`:

```sql
-- Shapes that have earned trust (accepted ≥ 5, reverts = 0)
WITH shape_stats AS (
    SELECT
        finding_source_type,
        governing_principle,
        -- Adapt the change_pattern fingerprint to your project. A
        -- common shape is the first significant word of change_summary
        -- after stop-word filtering, but project-specific patterns are
        -- usually better.
        substr(change_summary, 1, 40) AS change_pattern,
        COUNT(*) AS total,
        SUM(CASE WHEN rolled_back_at IS NULL THEN 1 ELSE 0 END) AS accepted,
        SUM(CASE WHEN rolled_back_at IS NOT NULL THEN 1 ELSE 0 END) AS reverted
    FROM auto_resolutions
    GROUP BY finding_source_type, governing_principle, change_pattern
)
SELECT * FROM shape_stats
WHERE accepted >= 5 AND reverted = 0;
```

The daily digest filters resolutions whose `(type, principle, pattern)` matches a row in the trusted set.

## Cross-references

- [../../02_audit_as_shape/](../../02_audit_as_shape/) — `auto_resolutions` is a sibling audit lane to `fact_corrections`.
- [../../04_pre_flight_and_invariants/](../../04_pre_flight_and_invariants/) — design-time prevention catches most violations before they ever surface as findings; the classifier sees what slips through.
- [../../07_system_reviewer/](../../07_system_reviewer/) — Layer 2 evaluates whether the classifier's calibration is still appropriate as the codebase evolves.
- [../../11_ai_dependency_tracking/](../../11_ai_dependency_tracking/) — the classifier itself is AI-dependent; model upgrades trigger re-validation.
