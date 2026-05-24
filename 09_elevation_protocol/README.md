# 09 — Elevation protocol

## The concept

> How patterns climb layers based on evidence. A project-layer sighting earns promotion to a stack-layer enforcer when it meets four criteria: generative force, reduction-resistance, falsifiability, and independent triangulation across genuinely independent projects. Demotion is a real operation — foundations that fail under cross-project evidence get demoted back to operational rules, with the original elevation history preserved per F1.

**Derives from:** Foundations [E2](../01_foundations/E2_convergence_is_triangulation.md) (independent triangulation is the strongest evidence) and [E3](../01_foundations/E3_foundations_aggressively_small.md) (the foundational layer must be aggressively small; promotion is rare).

## Why this matters for agent-governed systems

Without an elevation protocol, lessons stay trapped at the layer where they were first observed. The same bug shape gets fixed in every project; the same insight gets re-derived in every codebase; the corpus grows wide but shallow.

With an elevation protocol, lessons climb based on evidence. A pattern observed in one project is a sighting. The same pattern observed in two genuinely-independent projects is a candidate for stack-layer promotion. A foundation observed in many projects with no falsification across stacks is a candidate for universal-layer status. The corpus deepens as evidence accumulates.

For agent-governed multi-project systems, the protocol is also load-bearing in the other direction: an agent operating on many repos needs a structural answer to *"is this fix specific to this repo, or do I see this in every repo of this shape?"* The protocol provides the question and the criteria for answering it.

## What's in this directory

| File | Purpose |
|---|---|
| [doctrine/four_criteria.md](doctrine/four_criteria.md) | The four-criteria gate that a candidate must pass to be promoted, the anti-collinearity discipline, and the demotion mechanism. |
| [templates/promotion_proposal_template.md](templates/promotion_proposal_template.md) | Template for filing a promotion proposal — the structured document that a candidate goes through during the protocol. |

## How to adopt

1. **Adopt the four-criteria gate.** When a pattern from your project's `PATTERNS.md` looks like it might belong at a higher layer, walk it through the four criteria below. If all four pass, file a promotion proposal.

2. **Establish the staging surface.** Stack-layer candidates land in a `FOLLOWUPS.md` (or equivalent) at the stack-layer repo — that's the queue of patterns staged for promotion. Universal-layer candidates land in a `CANDIDATES/` directory at the universal-layer repo with one file per candidate, named with date and short title.

3. **Wire the cross-project evidence collection.** This is the most operationally-significant piece. A pattern promoted on evidence from only one project is over-elevated. The protocol requires evidence from N≥2 genuinely-independent projects — and "independent" means meeting the anti-collinearity test (different authors, different AIs, different stacks where possible, different domains).

4. **Wire demotion.** When cross-project evidence shows that an existing foundation or stack-layer rule fails (the bug shape doesn't actually recur; the fix shape doesn't generalize; the principle was domain-specific all along), the demotion path moves the rule back to its appropriate layer. The original elevation history is preserved per F1; demotion adds context, never overwrites.

5. **Surface promotion candidates in the digest.** New stack-level candidates in FOLLOWUPS.md show up in the daily digest (or weekly, depending on cadence) so the user sees what's been proposed. The user is the decision-maker for elevation — the agent surfaces, the user decides.

## The four-criteria gate (summary)

A candidate passes the gate if all four hold:

1. **Generative force** — the candidate explains multiple operational rules, not just one. Foundations that generate only one derived rule are usually that derived rule, mis-classified.

2. **Reduction-resistance** — the candidate doesn't already derive from existing foundations. Most candidates fail here: they're derivations someone hadn't recognized. The default disposition is *"this is a derivation we hadn't articulated."*

3. **Falsifiability** — the candidate declares what would prove it wrong. A foundation without a falsification condition is suspect — it might be belief rather than principle.

4. **Independent triangulation** — N≥2 genuinely-independent projects surface the same pattern. Independence is the criterion that's hardest to satisfy in practice; see the anti-collinearity discipline in [doctrine/four_criteria.md](doctrine/four_criteria.md).

A candidate that passes three criteria but fails one stays at its current layer with the candidate's analysis recorded. Re-evaluation happens when new evidence accumulates.

## The anti-collinearity discipline

From [E2](../01_foundations/E2_convergence_is_triangulation.md):

> If all projects in your portfolio share an author, an LLM, a stack, and a domain shape, *"three projects converge"* is mostly evidence that the author is consistent, not that the conclusion is true.

For elevation purposes, "genuinely independent" means:

- **Different stacks** — Python+SQLite vs Rust+Postgres vs TypeScript+Prisma. Same conclusion across different stacks is much stronger than same conclusion across three forks of the same stack.
- **Different domains** — financial vs medical vs gaming vs developer-tools. Same conclusion across different domains rules out domain-specificity.
- **Different authors or AI models** — same author and same AI is one perspective, even across three projects. Triangulation requires the perspectives to be genuinely different.

Most projects in any given portfolio will share many factors. The discipline isn't to refuse promotion until perfectly independent evidence appears (it almost never will); it's to be honest about the evidence's actual evidential weight. A candidate with three same-author same-AI same-stack sightings is weaker evidence than two genuinely-independent sightings — and the protocol should acknowledge that explicitly when proposing promotion.

## Cross-references

- [00_meta_stances/three_layer_architecture.md](../00_meta_stances/three_layer_architecture.md) — the structural model that makes promotion meaningful.
- [00_meta_stances/patterns_local_enforcers_home.md](../00_meta_stances/patterns_local_enforcers_home.md) — the meta-stance about how project sightings and stack enforcers relate.
- [01_foundations/E2_convergence_is_triangulation.md](../01_foundations/E2_convergence_is_triangulation.md) — the foundation behind the independent-triangulation criterion.
- [01_foundations/E3_foundations_aggressively_small.md](../01_foundations/E3_foundations_aggressively_small.md) — the foundation behind the strict gate.
- [10_followups_patterns/](../10_followups_patterns/) — three patterns currently staged for stack-layer promotion, each with seed evidence.
- [11_ai_dependency_tracking/](../11_ai_dependency_tracking/) — AI-dependent rules cap at the stack or project layer; the protocol enforces this.
