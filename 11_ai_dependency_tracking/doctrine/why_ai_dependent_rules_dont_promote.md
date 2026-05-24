# Doctrine excerpt — why AI-dependent rules don't promote to universal

Place this in your governance doc as the section governing how AI-dependency interacts with the elevation protocol.

---

## AI-dependent rules cap at the stack or project layer

**Derives from:** Foundations [E3](../../01_foundations/E3_foundations_aggressively_small.md) (the foundational layer must be aggressively small) and [E2](../../01_foundations/E2_convergence_is_triangulation.md) (cross-source independence is required for elevation; AI authorship is a shared-source factor that constrains universality claims).

A rule that has an AI-dependency note ([../templates/dependency_note_template.md](../templates/dependency_note_template.md)) cannot promote to the universal layer, even if it meets the other three elevation criteria (generative force, reduction-resistance, falsifiability).

### The reasoning

Universal-layer rules are physical/logical or epistemic invariants — true regardless of project, domain, or human choice. A rule whose correctness depends on a specific AI's behavior is, by construction, not universal:

- **It's contingent on the model.** A different model may produce different outcomes for the same rule, falsifying the rule's universality.
- **It's contingent on the deployment context.** A rule that works in a system using model X may not work in a system using model Y, or in a system that doesn't use AI at all.
- **It's contingent on the model's continued availability.** A model that's deprecated takes the rule with it (or forces the rule to be re-derived for a new model).

A universal foundation must hold in all of these conditions. AI-dependent rules don't.

### What this means operationally

- AI-dependent rules live at the **stack layer** (specific to a stack that includes a particular AI integration) or the **project layer** (specific to one project's AI configuration). They earn their place at those layers based on the elevation protocol's other criteria.

- An AI-dependent rule that has strong generative force, is reduction-resistant, falsifiable, and has cross-project triangulation across genuinely-independent projects... still caps at the stack layer. The AI-dependency is the structural reason it doesn't go higher.

- Universal-layer rules may IMPLY AI-dependent stack-layer rules. For example, E2 (convergence is evidence of triangulation) is a universal foundation; the operational rule *"use cross-model corroboration for high-stakes AI judgments"* is a stack-layer derivation that depends on AI behavior. The universal foundation stays universal; the operational derivation stays at the stack layer.

### The structural reason this matters

Without the cap, AI-dependent rules would accumulate at the universal layer over time. The universal layer would become bloated with rules that may not survive model upgrades — which violates [E3](../../01_foundations/E3_foundations_aggressively_small.md)'s smallness discipline and undermines [E1](../../01_foundations/E1_corpus_is_hypothesis.md)'s claim that universal foundations are working hypotheses that survive across genuinely-independent contexts.

The cap preserves the universal layer's property: rules that hold regardless of project, regardless of stack, regardless of which AI is in the loop. The cost is that some valuable insights stay at the stack layer rather than promoting — and that's the right cost.

### What if I want to elevate an AI-dependent rule anyway?

Two paths:

**1. Find the underlying AI-independent principle and elevate that.**

If an AI-dependent rule is genuinely producing universal-shape insights, those insights are usually surfacing an AI-independent foundation. For example, the rule *"AI output is hypothesis, not authority"* derives from E1 — the AI-dependency is incidental to the deeper principle (the corpus is hypothesis). The universal foundation E1 is what gets elevated; the AI-specific operational rule stays at the stack layer.

When you find yourself wanting to elevate an AI-dependent rule, try to articulate the AI-independent principle it instantiates. If you can, elevate that.

**2. If no AI-independent principle exists, the rule isn't universal.**

If the AI-dependency is essential to the rule's claim (not just incidental to its current implementation), the rule isn't universal. It's stack-shape. It earns its place at the stack layer.

### What this does NOT mean

- **AI-dependent rules aren't second-class.** They earn their place through the elevation criteria like any other rule. The cap is structural, not a judgment about their value.

- **AI-dependency notes don't preclude cross-model validation.** They REQUIRE it — the falsification condition is *"if cross-model agreement drops below threshold, the rule is suspect."* Cross-model validation is how AI-dependent rules earn their stack-layer status, not an obstacle to it.

- **The cap doesn't apply retroactively.** Existing universal foundations that turn out to have implicit AI-dependencies (because they were articulated under the assumption that AI was in the loop) need to be re-evaluated under the demotion mechanism. They might demote to stack layer, or the AI-dependency might turn out to be incidental. Either way, the re-evaluation is honest about the dependency.

### Cross-references

- [../README.md](../README.md) — the AI-dependency tracking concept overview.
- [../templates/dependency_note_template.md](../templates/dependency_note_template.md) — the per-rule note template.
- [../../09_elevation_protocol/doctrine/four_criteria.md](../../09_elevation_protocol/doctrine/four_criteria.md) — the elevation protocol that this cap is enforced through.
- [../../00_meta_stances/hypothesis_posture.md](../../00_meta_stances/hypothesis_posture.md) — the meta-stance that grounds AI-dependency tracking as a structural concern.
