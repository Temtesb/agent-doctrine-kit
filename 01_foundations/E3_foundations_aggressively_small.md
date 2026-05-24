# E3 — The foundational layer must be aggressively small

## Statement

A foundation earns its place by generating multiple operational rules, surviving the elevation protocol's adversarial checks, and explaining things existing foundations do not. Most insights resolve to *derivations* from existing foundations, not new foundations. A foundational layer that grows freely loses the property that makes it useful — it becomes another flat list with all the original problems.

## Type

Epistemic.

## Falsification condition

A demonstration that increasing the size of a foundational layer produces better operational outcomes than keeping it small. We have no such demonstration; theoretical work in axiom systems and engineering experience both push toward minimal-axiom foundations.

## Implies

- **The elevation protocol's gate must be high.** A candidate must explain things existing foundations do not, attract foundation-level tests, and survive across genuinely independent projects before it earns canonical status. See [09_elevation_protocol/](../09_elevation_protocol/) for the four-criteria gate.
- **The default disposition for any candidate foundation is "this is a derivation we hadn't articulated."** Most candidates resolve there. The candidate gets recorded at the right layer (operational rule, stack-layer pattern, or project-layer rule) rather than at the foundational layer.
- **Demotion is structurally necessary.** Without a path from "foundation" back to "operational rule" or "domain-specific pattern," the foundational layer can only grow. The elevation protocol's demotion mechanism is what keeps the layer small over time.
- **The proportion of insights that elevate to foundations should be small over time.** If most session insights elevate, the gate is too low. The healthy ratio is mostly-derivations, occasional-elevation.
- **Layered architecture is what makes elevation possible.** Without the universal/stack/project distinction (see [00_meta_stances/three_layer_architecture.md](../00_meta_stances/three_layer_architecture.md)), there's nowhere for an insight to land except at the foundational layer — which then bloats. The layering creates the structural homes where most insights naturally live.
- **Foundations should be aggressively reusable across domains.** A foundation that only applies to one project's domain is project-purpose, not universal. A foundation that only applies to one stack is stack-shape, not universal. The universality is the test.

## Anchor history

- **2026-04-28** — Elevated. Triggered by recognition that without explicit smallness discipline, the introspection mechanism for discovering foundations would over-elevate, defeating the foundational layer's purpose. Drawn from the analogy to scientific axiom systems where the foundational layer is tiny (a handful of axioms in arithmetic; a few field equations in physics) and most physics is *derived* from it rather than separately axiomatized.

## AI-dependency note

**An AI-assisted system is at higher risk of foundation-bloat than a human-only system because AI can produce articulate framings of new "foundations" cheaply.** The smallness discipline must be enforced more strictly here than in a slower, more manual context.

In practice, this means:

- The elevation protocol's "AI-drafted candidate" path includes additional skepticism on novelty claims — most AI-drafted candidates are derivations the AI hadn't recognized.
- When a candidate looks foundation-shaped, the default question is *"which existing foundation does this derive from?"* before *"is this a new foundation?"*
- The protocol's "independent triangulation" criterion is especially strict for AI-drafted candidates: the cross-project evidence must come from projects the candidate-drafting AI did not author, to avoid shared-source bias (E2).

## What derives from this foundation in this kit

- [09_elevation_protocol/](../09_elevation_protocol/) — the four-criteria gate (generative force, reduction-resistance, falsifiability, independent triangulation) is the operational form of the smallness discipline.
- The deliberate cap on this kit's foundation count at six (F1-F3, E1-E3). Future candidates may earn elevation, but the bar is what's documented in the elevation protocol — not enthusiasm.
- The [10_followups_patterns/](../10_followups_patterns/) directory exists at the stack layer, not the universal layer, because each pattern is a derivation from F1/F2/F3 applied to a specific stack shape. Promoting them to universal foundations would be over-elevation.
