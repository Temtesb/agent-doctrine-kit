# E2 — Convergence is evidence of triangulation, not proof of truth

## Statement

When multiple independent sources — minds, projects, tests, dimensions of analysis — converge on the same conclusion, the conclusion is more credible than if any one source held it alone. But convergence is not proof. Sources that share a blind spot can converge on something wrong, and the convergence itself does not detect the shared blind spot.

## Type

Epistemic.

## Falsification condition

A demonstrated procedure that produces provably true conclusions through convergence alone, with no external validation. No such procedure exists for non-trivial questions (the problem of induction; Gödel's incompleteness theorems).

## Implies

- **Triangulation across genuinely independent dimensions strengthens evidence; triangulation across collinear dimensions does not.** A principle confirmed by three different test types (unit, integration, end-to-end) is stronger evidence than the same principle confirmed by three near-identical unit tests.
- **Anti-collinearity discipline in project selection.** If all projects in your portfolio share an author, an LLM, a stack, and a domain shape, *"three projects converge"* is mostly evidence that the author is consistent, not that the conclusion is true. The elevation protocol weighs cross-project evidence with this in mind.
- **Shared-source bias is a real failure mode.** The user starting all projects and the same AI reasoning across them produces correlated rather than independent triangulation. Outside-source input (different humans, different LLMs, domain experts who have not seen the corpus) gets weighted more heavily when available.
- **Foundation-level tests must come from a different angle than the foundation's articulation.** Tests written by the proposer of a principle are weaker evidence than tests written from a stance that doesn't already share the proposer's framing.
- **Long-passing tests can be triangulating support, not invisible assumptions** — the multicollinearity vs. near-multicollinearity distinction. Genuinely independent probes of the same conclusion are robustness; identical probes are redundancy.
- **Prefer enforcers over principles.** This derives from E2: convergence on a documented principle is necessary but not sufficient evidence that the principle is honored at runtime; an enforcer is the structural mechanism that closes the gap between belief and verification.
- **Cross-model AI corroboration is a scaling lever.** A system running multiple LLMs in parallel has an existing substrate for *independent triangulation* across models — the strongest evidence E2 admits in an AI-consuming-doctrine context.

## Anchor history

- **2026-04-28** — Elevated. Triggered by the user explicitly calling out the caveat as worthy of enshrinement after a conversation demonstrated convergence behavior between two parties (user and AI) who shared significant overlap in framing and starting context. The convergence observed was real and informative, but its evidential weight was limited by the shared-source factor — surfacing that fact required the foundation.

## AI-dependency note

**The same Claude instance reasoning across projects is a major shared-source factor.** As AI capabilities and defaults change across model versions, the convergence pattern may shift; outputs that converged with one model version may not with another. Cross-model triangulation is a candidate mitigation but is not yet structured in most projects — it's the move that turns a multi-LLM architecture from a redundancy into an evidentiary advantage.

This foundation's implications scale with how much AI is in the loop. In a single-model project, the dependency is moderate. In a multi-LLM project (like an agent-governed code-modification system using OpenAI + Gemini + Claude in parallel), the dependency is central — the cross-model triangulation is a primary evidence mechanism the system can deliberately exploit.

## What derives from this foundation in this kit

- [00_meta_stances/prefer_enforcers_over_principles.md](../00_meta_stances/prefer_enforcers_over_principles.md) — the meta-stance that closes the principle-vs-runtime gap; derives directly from E2.
- [00_meta_stances/patterns_local_enforcers_home.md](../00_meta_stances/patterns_local_enforcers_home.md) — local convergence on a pattern is evidence; the enforcer is the reusable mechanism.
- [07_system_reviewer/](../07_system_reviewer/) — the two-layer reviewer is structural triangulation: Layer 1 catches mechanical drift, Layer 2 catches conceptual drift from a different angle.
- [09_elevation_protocol/](../09_elevation_protocol/) — multi-project triangulation as a promotion criterion; anti-collinearity discipline.
- [11_ai_dependency_tracking/](../11_ai_dependency_tracking/) — the per-rule discipline derives from E2: AI-dependent rules need cross-model corroboration to earn their place; model upgrades invalidate the prior convergence.
