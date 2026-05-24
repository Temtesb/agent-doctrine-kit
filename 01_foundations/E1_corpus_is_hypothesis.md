# E1 — The corpus is a hypothesis, not an authority

## Statement

Every rule in the corpus is the current best understanding, anchored to a stated reason, subject to revision when something deeper is discovered, when the rule's falsification condition is demonstrated, or when cross-project evidence reveals it was domain-specific. The corpus is not a list of true things; it is the set of working hypotheses under which the system currently operates.

## Type

Epistemic.

## Falsification condition

A demonstration that a corpus can be authoritative — known true a priori — without being subject to revision. Such a corpus would require access to truth that no subsequent evidence could overturn. We do not have such access; nothing we know is sealed.

## Implies

- **Every rule declares its anchor.** A rule without a stated foundation is suspect. The anchor is what lets a reader (human or AI) verify the derivation still holds rather than defer blindly.
- **Every rule has an anchor history.** When the rule was added, why, what triggered any subsequent re-anchoring. The history makes the rule a temporal artifact rather than an eternal one.
- **Every rule declares its falsification condition** where one is meaningful. The falsification condition surfaces what would change the rule, so agents confronting an edge case can ask *"are we in the falsification condition?"* and route accordingly.
- **The hypothesis posture changes how the corpus reads.** Newcomers (human or AI) read it as something to challenge from a position of derived foundations, not as gospel. See [00_meta_stances/hypothesis_posture.md](../00_meta_stances/hypothesis_posture.md) for the operational stance.
- **Demote is a real operation, not just elevate.** Foundations that fail under cross-project evidence get demoted to operational rules with the original elevation history preserved. See [09_elevation_protocol/](../09_elevation_protocol/) for the demotion path.
- **The corpus's own evolution is data.** The corpus tracks itself with the same temporal discipline F1 applies to project data — anchor histories, conversation records, candidate-but-not-yet-elevated entries archived rather than deleted.

## Anchor history

- **2026-04-28** — Elevated. Triggered by recognition that doctrine docs as written read like authority and made challenge structurally hard. The conversation that produced this elevation explicitly demonstrated that hypothesis-shaped revision works.

## AI-dependency note

**This foundation matters more under AI authorship than under human-only authorship.** An AI consuming an authority-shaped doc may follow it more rigidly than a human would; the hypothesis posture is the structural hedge against that. Specifically:

- A human reading *"always do X"* has natural skepticism and pushes back when the rule doesn't fit.
- An AI agent reading the same rule may follow it more literally — especially in ambiguous cases where a human would pause and a model defaults to compliance.
- Rigid compliance with stale rules is the failure mode. The falsification-condition and anchor-history fields are the structural cues that prevent it.

This dependency does not reduce E1's universality — the foundation holds independent of AI. The dependency is in how aggressively the discipline must be enforced: in an AI-consuming-doctrine system, hypothesis-posture fields on every rule are essential; in a human-only system, they are good practice but not load-bearing.

## What derives from this foundation in this kit

- [00_meta_stances/hypothesis_posture.md](../00_meta_stances/hypothesis_posture.md) — the operational stance for how doctrine is held.
- The 6-field structure that every foundation in [01_foundations/](.) declares (this file is itself the worked example).
- [09_elevation_protocol/](../09_elevation_protocol/) — the discipline for revising, promoting, or demoting rules based on evidence.
- [11_ai_dependency_tracking/](../11_ai_dependency_tracking/) — per-rule notes recording AI-behavior dependencies so model upgrades flag the dependent rules for review.
