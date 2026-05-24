# 01 — Foundations

The universal-layer doctrine. Six foundational invariants — three physical/logical (F1-F3) and three epistemic (E1-E3) — that apply to any project of any shape and from which every stack-layer and project-layer rule derives.

Per the smallness discipline (E3), the foundational layer is aggressively small. New foundations earn elevation only when they survive the protocol's adversarial checks: generative force, reduction-resistance, falsifiability, and independent cross-project triangulation.

## The six foundations

| File | Type | Statement (one sentence) |
|---|---|---|
| [F1_time_has_direction.md](F1_time_has_direction.md) | Physical/Logical | Past events cannot be unmade. What was true at a given moment remains true about that moment forever. |
| [F2_logic_holds.md](F2_logic_holds.md) | Physical/Logical | Numbers behave as numbers. Logical inference is valid. A statement cannot simultaneously be true and false in the same sense. |
| [F3_information_asymmetric_durability.md](F3_information_asymmetric_durability.md) | Physical/Logical | Information takes work to preserve and zero work to destroy. Once destroyed, recovery is impossible without a prior copy. |
| [E1_corpus_is_hypothesis.md](E1_corpus_is_hypothesis.md) | Epistemic | Every rule in the corpus is the current best understanding, anchored to a stated reason, subject to revision. The corpus is not authority. |
| [E2_convergence_is_triangulation.md](E2_convergence_is_triangulation.md) | Epistemic | Convergence of multiple independent sources strengthens evidence but is not proof. Sources that share a blind spot can converge on something wrong. |
| [E3_foundations_aggressively_small.md](E3_foundations_aggressively_small.md) | Epistemic | A foundation earns its place by generating multiple operational rules, surviving elevation, and explaining things existing foundations don't. Most insights resolve to derivations, not new foundations. |

## The 6-field structure

Each foundation declares:

- **Statement** — the rule, in one sentence, sharp enough to fit on a sticky note.
- **Type** — Physical/Logical (true about reality regardless of choice) or Epistemic (true about how knowledge is acquired and validated).
- **Falsification condition** — what would prove this foundation wrong. A foundation without a falsification condition is suspect; record it explicitly.
- **Implies** — operational rules and patterns that derive from this foundation. Not exhaustive; grows as derivations are recognized.
- **Anchor history** — when this foundation was elevated, what triggered the elevation, and any subsequent revisions.
- **AI-dependency note** — if any of the implied rules depend on a current AI's behavior (model, capabilities), this is recorded explicitly so that future model changes flag the rules for review.

This structure is the universal-layer enforcement of the hypothesis-posture meta-stance (see [00_meta_stances/hypothesis_posture.md](../00_meta_stances/hypothesis_posture.md)). It tells the reading agent not just *what* the foundation claims but *what would prove it wrong*, *what derives from it*, and *when and why it was added*. Rules without these fields are followed because they're written down; rules with them are followed because the reader can verify the derivation still holds.

## How to read these

A new contributor (human or AI) coming to a project built on this kit should:

1. Read this README.
2. Read each foundation in order F1 → E3.
3. Internalize the falsification conditions — these are the conditions under which the foundation itself could be wrong.
4. Read the elevation protocol ([09_elevation_protocol/](../09_elevation_protocol/)) to understand how this layer evolves.
5. Open the project's own doctrine (CLAUDE.md or equivalent). Every rule there should anchor to a foundation here.
6. If a rule's anchor is unclear, that's a gap to file — not a rule to follow uncritically.

## Cross-references

- [00_meta_stances/](../00_meta_stances/) — the meta-stances that frame how foundations are held.
- [09_elevation_protocol/](../09_elevation_protocol/) — the discipline for adding, revising, or demoting foundations.
- [11_ai_dependency_tracking/](../11_ai_dependency_tracking/) — how AI-dependency notes work at scale for derived rules, not just for foundations themselves.
