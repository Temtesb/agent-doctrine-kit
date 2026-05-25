# 12 — Ingestion protocol

## The concept

> A structured process for incorporating external artifacts (other projects, papers, libraries, books, conversations) into the kit's structural framework. The output of an ingestion is **skeleton-shaped** — properly anchored to foundations, fitted into existing subsystems or proposed as new ones, with explicit provenance recording — so that external ideas can flow in without erasing their attribution and without forcing the kit into shapes it can't reason about.

**Derives from:** Foundations [F1](../01_foundations/F1_time_has_direction.md) (ingestion is itself a historical event with a timestamp; provenance is the F1 application to where ideas came from) and [E2](../01_foundations/E2_convergence_is_triangulation.md) (an external artifact is one more independent source whose convergence with internal patterns IS evidence — but only if its independence is honored at ingestion time, not erased by absorption).

## Why this exists

A kit whose structural commitments make it unable to incorporate external work is structurally xenophobic — calcified around whatever its early authors happened to think, with no path for genuine external input. The elevation protocol ([09_elevation_protocol/](../09_elevation_protocol/)) handles promotion of patterns surfaced *inside* skeleton-derived projects. It does not handle ingestion of work that exists *independently* of the skeleton.

This is the missing concept that closes that gap.

The biological analog is digestion. You don't reject food because it didn't grow in your body; your digestive system breaks it down into constituent molecules and re-assembles them into your own proteins. The structural commitment is *"only my own protein shapes get incorporated,"* but the *process* is fully open to foreign input — and that openness is what makes the system viable.

For a kit governing agent-modified codebases, the parallel: external artifacts (PrizmForge, research papers, peer projects, libraries) routinely contain valuable primitives that the kit hasn't independently derived. The ingestion protocol is the structured digestion process: break the artifact down, identify what's load-bearing, anchor each piece to a foundation, fit into subsystems, and record honest provenance.

## What's in this directory

| File | Purpose |
|---|---|
| [doctrine/five_step_process.md](doctrine/five_step_process.md) | The five-step ingestion procedure: source analysis, principle extraction, subsystem fit assessment, adaptation, provenance recording. |
| [templates/ingestion_record_template.md](templates/ingestion_record_template.md) | The template for documenting one ingestion event. Lives wherever your project tracks structural additions. |
| [examples/prizmforge_ingestion.md](examples/prizmforge_ingestion.md) | The worked first case — PrizmForge run through the ingestion protocol, with per-primitive derivation analysis and subsystem-fit assessment. Serves as both reference example and the actual ingestion record. |

## How to use the protocol

1. **You encounter an external artifact that looks valuable.** A paper describes a primitive your codebase doesn't have; another project has solved a problem you're hitting; a book chapter formalizes a pattern you've been ad-hoc using.

2. **Decide whether ingestion is warranted.** Not every external artifact needs ingestion. The bar: the artifact contains primitives that would have value across multiple projects and that the kit hasn't independently derived. If it's a one-off fix specific to your current project, just adopt it directly; ingestion is for things that earn a place in the kit's reusable layer.

3. **Run the five steps** ([doctrine/five_step_process.md](doctrine/five_step_process.md)). The steps are sequential but each step's depth varies with the artifact's complexity. A short paper might be one afternoon's work; a full system like PrizmForge might be several sessions.

4. **Document the ingestion** ([templates/ingestion_record_template.md](templates/ingestion_record_template.md)). The record is the F1-honored history of what came from where — future readers should be able to trace any kit primitive back to its actual origin.

5. **The ingested primitives land in the kit** as new or extended subsystem files. The provenance record stays as the audit trail; the ingested primitives don't need *inline* attribution every time they're referenced (that would be inefficient), but they must be reachable from the record.

## Why this matters specifically for agent-governed systems

Agent-modified codebases have a higher rate of external-pattern encounter than human-only codebases. Every agent session can read papers, browse other projects, surface analogous patterns from training data, propose patterns from adjacent domains. Without a structured ingestion process, every encountered external pattern either:

- **Gets absorbed silently** — re-implemented without attribution, the kit's evolution becomes opaque about where ideas came from
- **Gets rejected by reflex** — because it doesn't already fit the kit's idiom, the kit becomes a structural echo chamber
- **Gets imported wholesale** — accumulating surface area that competes with the kit's own architecture

The ingestion protocol provides the third path: structured digestion with honest provenance. External work flows in; structural compliance flows out; the kit's evolution stays auditable.

## Tensions to name explicitly

1. **Adaptation isn't compatibility — it's reinterpretation.** An ingested primitive almost never lands looking identical to its source. The source's idioms, dependencies, and authorial choices get translated into the kit's idiom. This is honest about what's happening; it's not theft because step 5 records provenance.

2. **Provenance recording cost.** Step 5 adds bookkeeping. The benefit is auditable evolution; the cost is the overhead of recording where every primitive came from. The tradeoff favors recording for any ingestion of substance; for tiny adoptions (a one-line idiom from a Stack Overflow answer) the overhead may exceed the benefit and inline attribution in the code may be enough.

3. **The ingestion can fail at step 3 (subsystem fit).** Some external primitives don't fit any existing subsystem and don't justify a new subsystem either. The honest answer is: the primitive isn't a fit for this kit. Record the analysis (so future ingestion attempts don't re-derive it) and don't force the import.

4. **External authorship is not erased by ingestion.** The source's attribution stays in the provenance record. The kit may re-implement the primitive in its own idiom, but the intellectual debt is acknowledged. Future readers who want to dig into the original source can find it.

## Cross-references

- [09_elevation_protocol/](../09_elevation_protocol/) — the sibling protocol that handles promotion of internally-surfaced patterns. The two protocols share the structural concern (when does something earn a place at a higher layer) but operate on different inputs (internal-sighting vs. external-artifact).
- [00_meta_stances/patterns_local_enforcers_home.md](../00_meta_stances/patterns_local_enforcers_home.md) — the meta-stance about enforcer placement; ingested primitives follow the same placement logic as internally-derived ones.
- [examples/prizmforge_ingestion.md](examples/prizmforge_ingestion.md) — the seed-evidence ingestion case that motivated this concept's existence.
