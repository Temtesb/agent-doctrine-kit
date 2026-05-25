# Doctrine excerpt — conditional doctrine

The kit's existing layer model (universal / stack / project — see [00_meta_stances/three_layer_architecture.md](../../00_meta_stances/three_layer_architecture.md)) assumes that doctrine at each layer is *universal within its scope*. A universal-layer rule holds for any project; a stack-layer rule holds for any project of that stack shape; a project-layer rule holds for that one project.

Some rules don't fit. They're real, they're true, but their applicability is conditional on context — a configuration choice, a deployment topology, a runtime population, a phase of project maturity. Filing them as universal-within-scope is dishonest; skipping them entirely loses the lesson.

This doctrine entry names the **conditional doctrine** shape as a first-class concept and gives it a place in the kit.

---

## The principle

> A rule is **conditional** when its applicability depends on a named context that the consuming project must check against its current configuration. Conditional rules are filed alongside universal rules in their layer, but with an explicit `**Applies when:**` clause that names the activating condition(s). A project that doesn't currently meet the condition records the rule as informational ("if we ever do X, this rule activates") rather than as enforced doctrine.

**Derives from:** The tension between [E3](../../01_foundations/E3_foundations_aggressively_small.md) (the foundational layer must be aggressively small; over-elevation is a structural failure mode) and the observed reality that some real, recurring patterns are context-dependent rather than universal. Filing conditional rules as universal violates E3 by elevating something that isn't universal; refusing to file them at all loses lessons that genuinely matter under their activating conditions.

Also derives from the *tension-celebration* framing implicit in [00_meta_stances/hypothesis_posture.md](../../00_meta_stances/hypothesis_posture.md): if doctrine is held as hypothesis, then *"this rule holds under these conditions and not others"* is a legitimate hypothesis shape. The system that pretends all rules are universal is making a stronger claim than it can support.

---

## Why this shape matters

A historical analogy makes the case. Put Newton and Einstein in the same room and ask them to describe the universe with full agreement. They can't — not because either is wrong, but because human understanding is still limited enough that the tension between their frameworks is genuine. Newton's mechanics is *conditional doctrine*: it applies when velocities are much less than the speed of light and gravitational fields are weak. Within those conditions, it's correct and useful. Outside them, relativity supersedes. Pretending Newton is universal makes navigation wrong at GPS scales; pretending Einstein eliminates Newton makes engineering needlessly complex at human scales. The mature stance is *both are correct under their conditions; the conditions distinguish them*.

Software systems have the same shape at smaller scale. A rule like *"durable-state writes must route through a designated host-resident agent"* is true and load-bearing when multiple agent runtimes operate concurrently against shared host-resident DBs. It's pure overhead when there's a single runtime or when runtimes don't share state. Filing it as universal stack-layer doctrine asks every project to implement coordination machinery they don't need; refusing to file it at all means the lesson has to be re-learned every time someone sets up multi-runtime operation.

Conditional doctrine acknowledges that complex systems can lead to conclusions that don't fully reconcile, and that's okay. The goal isn't to eliminate the tension by forcing one rule to cover all cases; it's to honor truth by naming the conditions under which each rule applies.

---

## The structural shape

A conditional doctrine entry has the same fields as any other doctrine entry (Derives from, Falsification condition, Anchor history, AI-dependency note) PLUS:

- **Applies when:** — a named, queryable condition. Examples:
  - *"Multiple agent runtimes operate concurrently against the same host-resident DB."*
  - *"The project has crossed N active concurrent users where N > the message-queue throughput."*
  - *"The system is deployed in a regulated environment requiring audit-trail preservation."*

- **Doesn't apply when:** — the negative condition, equally explicit. Helps the consuming project recognize when the rule is noise rather than load-bearing.

- **Detection mechanism:** — how a consuming project knows whether the condition holds. May be a simple check ("we have a launchd plist running the run-loop" → multi-runtime is active), a configuration flag, or a deployment-topology fact.

- **What changes when the condition activates:** — concrete description of what enforcement looks like once the rule is in play. Distinguishes "we should think about this" from "we have to do X."

- **What changes when the condition deactivates:** — the de-activation path. Conditions change. A project that activates a conditional rule should also know how to deactivate it cleanly without losing the audit trail of when the rule was in force.

---

## Where conditional doctrine lives

In each subsystem directory, alongside universal doctrine, distinguished by the **Applies when:** clause. The kit's existing subsystems can host conditional rules:

- [10_followups_patterns/](../../10_followups_patterns/) — stack-layer enforcers. Some patterns there are universal (static-coupling invariants apply to any HTML+JS+Python project); others are conditional (sandbox-vs-host routing applies only when multi-runtime is active). The conditional ones declare their **Applies when:**.

- [03_classifier_and_audit_lane/](../../03_classifier_and_audit_lane/) — the per-edit gating doctrine (see [per_edit_gating.md](../../03_classifier_and_audit_lane/doctrine/per_edit_gating.md)) is conditional on the project having multiple agents modifying the same codebase. The doctrine could be reworked with an **Applies when:** to make the conditionality explicit (currently it's implicit in the *"when to use"* section).

- [07_system_reviewer/](../../07_system_reviewer/) — the N-layer generalization (see [n_layer_generalization.md](../../07_system_reviewer/doctrine/n_layer_generalization.md)) is conditional on the agent population being diverse enough to justify specialization. Currently it's framed as "when to generalize"; could be sharpened with **Applies when:** semantics.

A natural retrospective audit: walk existing doctrine and ask, *"is this rule actually universal in its scope, or is it conditional?"* Some current rules will turn out to be conditional that were filed as universal.

---

## What this does NOT mean

- **Not every rule needs conditional framing.** Most rules genuinely are universal within their scope. F1 holds for any project; the audit-as-shape-of-data principle applies anywhere a system stores facts. Conditional framing is for the rules where it's load-bearing — where pretending the rule is universal would mislead, AND skipping it entirely would lose the lesson.

- **Not an escape hatch.** *"This rule is conditional, so I don't have to follow it"* is not the move. The move is *"this rule has these conditions; let me check whether my project meets them."* If it does, the rule applies; if it doesn't, the rule informs rather than enforces.

- **Not a substitute for the elevation protocol.** A rule that surfaces in multiple independent projects under different conditions might still earn elevation — but the elevated form would be the conditional rule, not a forced universalization. The elevation protocol's criteria still apply; conditionality is a property of the rule, not a workaround.

---

## Cross-references

- [00_meta_stances/three_layer_architecture.md](../../00_meta_stances/three_layer_architecture.md) — the layer model conditional doctrine extends.
- [00_meta_stances/hypothesis_posture.md](../../00_meta_stances/hypothesis_posture.md) — the meta-stance that grounds conditionality as a legitimate hypothesis shape.
- [10_followups_patterns/sandbox_vs_host_routing.md](../../10_followups_patterns/sandbox_vs_host_routing.md) — the first worked-example of conditional stack-layer doctrine.
- [01_foundations/E3_foundations_aggressively_small.md](../../01_foundations/E3_foundations_aggressively_small.md) — the foundation that conditional doctrine helps protect (over-universalization is itself an E3 violation).
