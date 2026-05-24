# 11 — AI-dependency tracking

## The concept

> Per-rule notes that record which AI behaviors a rule depends on, which model versions the rule was validated against, what would falsify the rule under a new model, and the fallback when re-validation is needed. When a model upgrade ships, dependent rules get flagged for review rather than silently producing different outcomes.

**Derives from:** Foundations [E2](../01_foundations/E2_convergence_is_triangulation.md) (AI-dependent rules need cross-model corroboration to earn their place; the same model reasoning across rules is a shared-source factor) and [E1](../01_foundations/E1_corpus_is_hypothesis.md) (every AI-dependent rule is a hypothesis with a specific failure mode — model change — that must be falsifiable through validation).

## Why this matters for agent-governed systems

**This is the cross-cutting discipline uniquely critical for systems built around AI agents.**

PrizmForge-shape systems — multi-LLM, agent-consuming-doctrine — have a failure mode that no other discipline in this kit catches: **silent correctness loss from model upgrade**. When a model ships a new version and a previously-reliable principle starts producing different outcomes, the system keeps running, claims keep getting made, and the principles those claims rely on no longer hold. Without dependency tracking, you find out when something breaks in production rather than when the model changes.

Three structural reasons it matters more for these systems than for most projects:

**1. Multi-LLM architectures multiply the dependency surface.** A single-model project has one AI behavior to track. A multi-LLM project (OpenAI + Gemini + Claude in parallel) has multiple model behaviors, and rules that work with one model's behavior may not work with another's. Without explicit dependency tracking, the cross-model differences become emergent rather than enumerated.

**2. AI-consuming-doctrine is the entire stack.** Per the hypothesis-posture meta-stance ([00_meta_stances/hypothesis_posture.md](../00_meta_stances/hypothesis_posture.md)), AI agents read your doctrine — and every read is an opportunity for a model upgrade to silently change how the doctrine is interpreted. The dependency note is the structural safeguard.

**3. Cross-model corroboration is your scaling lever.** If you're already running multiple LLMs in parallel, you have an existing substrate for *independent triangulation* across models — which is the strongest evidence form per E2. Recording which rules require cross-model agreement vs. which can be validated against one model alone turns the multi-LLM design from a redundancy into an evidentiary advantage.

## What's in this directory

| File | Purpose |
|---|---|
| [doctrine/why_ai_dependent_rules_dont_promote.md](doctrine/why_ai_dependent_rules_dont_promote.md) | The principle that AI-dependent rules cap at the stack or project layer — they cannot promote to universal even if they meet the other elevation criteria. |
| [templates/dependency_note_template.md](templates/dependency_note_template.md) | The four-field per-rule note: which behavior, validated against, falsification, fallback. With worked example. |

## How to adopt

1. **Audit your existing rules for AI dependencies.** Walk through your doctrine. For each rule, ask: *"does this rule's correctness depend on a specific AI's behavior?"* Most rules don't (mechanical CI checks, schema constraints, deterministic computations). Some do (any rule whose application depends on AI judgment — classifier criteria, AI-output verification, prompt-based detection logic).

2. **Add the four-field dependency note to AI-dependent rules.** Use the template at [templates/dependency_note_template.md](templates/dependency_note_template.md). The four fields: AI behavior depended on, model versions validated against, falsification condition for new models, fallback when re-validation is pending.

3. **Wire the model-upgrade trigger.** When you upgrade a model anywhere in your system, search the codebase / doctrine for AI-dependency notes that reference the upgraded model. Those notes' rules need re-validation.

4. **Re-validate by running the rule's calibration against the new model.** For a classifier, run the new model on the existing calibration set and check whether the rule's outputs are still in the expected range. For an AI-output-verification rule, run a sample of historical AI outputs through the new model and check whether the verification verdicts still agree with reality.

5. **For rules that fail re-validation, route to the fallback.** This usually means routing affected findings to user review until the rule is re-derived for the new model. Don't auto-act on rules whose validation is pending — that's the silent-correctness-loss failure this discipline exists to prevent.

6. **Wire cross-model corroboration where the multi-LLM substrate exists.** For high-stakes AI-dependent rules, run the same input through two independent models and surface only findings both agree on. The structural triangulation per E2 is the strongest evidence form available.

## The discipline scales with the project

Day one might be three AI-dependency notes. Mature state might be twenty. The framework doesn't require completeness; it requires that whatever IS declared gets re-validated when models change. Coverage grows organically as new AI-dependent rules are added or recognized.

The bar for adding a dependency note is *"this rule's outcome would visibly differ if the model changed."* If you can't articulate the dependency, the rule probably isn't AI-dependent — or your understanding of how it works is incomplete (the second case is itself a finding worth surfacing).

## Tensions to name explicitly

1. **AI-dependency tracking imposes a cost on the project layer.** Every AI-dependent rule needs the note. Every model upgrade triggers re-validation. Cross-model corroboration calibration is an ongoing test surface. The cost is real; the alternative (silent correctness loss) is worse. A project still proving its architecture works at all may find this discipline a heavy lift — but the discipline can start sparse and grow, same as Data Contracts and the trust ratchet.

2. **AI-dependent rules cap at the stack or project layer.** Per the elevation protocol, they cannot promote to universal even if they meet the other three criteria. This is intentional — universal foundations must be AI-independent. See [doctrine/why_ai_dependent_rules_dont_promote.md](doctrine/why_ai_dependent_rules_dont_promote.md).

3. **The dependency note is a hypothesis itself.** You're claiming a specific AI behavior is what the rule depends on. That claim is your best understanding at the time of writing. New cases may reveal that the actual dependency is broader, narrower, or different than what you wrote. Per [E1](../01_foundations/E1_corpus_is_hypothesis.md), the dependency note is subject to revision when evidence warrants.

## Cross-references

- [00_meta_stances/hypothesis_posture.md](../00_meta_stances/hypothesis_posture.md) — the meta-stance that frames why this discipline exists.
- [01_foundations/E1_corpus_is_hypothesis.md](../01_foundations/E1_corpus_is_hypothesis.md) — the foundation behind AI-as-hypothesis framing.
- [01_foundations/E2_convergence_is_triangulation.md](../01_foundations/E2_convergence_is_triangulation.md) — the foundation behind cross-model corroboration.
- [03_classifier_and_audit_lane/](../03_classifier_and_audit_lane/) — the classifier itself is AI-dependent; the dependency note structure applies to it directly.
- [07_system_reviewer/](../07_system_reviewer/) — Layer 2 (AI architectural review) is AI-dependent and needs a note.
- [09_elevation_protocol/](../09_elevation_protocol/) — the protocol enforces that AI-dependent rules cap at the stack or project layer.
