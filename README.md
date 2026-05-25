# agent-doctrine-kit

A modular reference kit of patterns for building **agent-governed codebases** — systems where AI agents propose, review, and apply code changes, and where the doctrine the agents read shapes what they do.

Each directory is one concept. Each is self-contained: a `README.md` orients you, and (where applicable) three companion files give you a schema you can copy into your migrations, a doctrine excerpt you can adapt into your governance docs, and an enforcer (test, decorator, check) that makes the principle self-honoring.

**Take what's useful; discard the rest.** Per the hypothesis-posture meta-stance (see `00_meta_stances/hypothesis_posture.md`), this kit is the current best understanding of a layered architecture for agent-driven systems. It is not gospel. Every file in here is a working hypothesis that survived contact with a real production project; that doesn't make any of it right for yours.

---

## Map of the kit

| Dir | Concept | Layer | Files |
|---|---|---|---|
| [00_meta_stances/](00_meta_stances/) | Three meta-stances: enforcers over principles, patterns-are-local-enforcers-are-the-home, the hypothesis posture; plus the three-layer architecture | meta | 5 |
| [01_foundations/](01_foundations/) | The six foundational invariants (F1-F3 physical/logical, E1-E3 epistemic) with full 6-field structure each | universal | 7 |
| [02_audit_as_shape/](02_audit_as_shape/) | "Audit is the shape of the data, not a feature." Every meaningful state change writes an append-only audit row in the same transaction. | universal → stack | 4 |
| [03_classifier_and_audit_lane/](03_classifier_and_audit_lane/) | The four-criteria agent-vs-user classifier; `auto_resolutions` audit lane; trust ratchet keyed on change shape (not actor) | stack | 4 |
| [04_pre_flight_and_invariants/](04_pre_flight_and_invariants/) | The five-question design-time pre-flight + the `_KNOWN_ALLOWED` ratchet pattern for architecture invariant tests | stack + project | 3 |
| [05_lessons_loop/](05_lessons_loop/) | `lesson_candidates` table + the stub generator that auto-emits draft invariant tests from accepted candidates | stack + project | 4 |
| [06_patterns_and_dissonance/](06_patterns_and_dissonance/) | `PATTERNS.md` for resolved patterns + the dissonance ledger for unresolved tensions; entry templates for both | project | 3 |
| [07_system_reviewer/](07_system_reviewer/) | Two-layer System Reviewer: Layer 1 deterministic CI self-audit, Layer 2 AI architectural review — distinct from any per-proposal reviewer | stack | 3 |
| [08_data_contracts/](08_data_contracts/) | Declarative registries: fact_owners, computed_values, business_events — single source of truth that tests verify against reality | stack | 4 |
| [09_elevation_protocol/](09_elevation_protocol/) | How patterns climb layers based on evidence — multi-project triangulation, anti-collinearity discipline, demotion as a real operation | cross-layer | 3 |
| [10_followups_patterns/](10_followups_patterns/) | Three stack-layer enforcers ready to lift: static-coupling invariants, background-process git-lock coordination, reflective-layer freshness audit | stack | 4 |
| [11_ai_dependency_tracking/](11_ai_dependency_tracking/) | Per-rule notes recording AI-behavior dependencies + model versions validated against + falsification + fallback. Closes the silent-model-upgrade gap. | cross-cutting | 3 |
| [12_ingestion_protocol/](12_ingestion_protocol/) | Five-step process for incorporating external artifacts (other projects, papers, libraries) into the kit while preserving structural integrity and recording honest provenance. Includes two worked cases (PrizmForge and MultiAgent). | cross-layer | 5 |
| [13_safe_code_modification/](13_safe_code_modification/) | Line-GUID editing + content-hash optimistic concurrency + post-write invalidation. Ingested from PrizmForge per 12's protocol. Addresses line-number drift and concurrent overwrite — failure modes agent-modified codebases hit at higher intensity than single-author. | stack | 4 |
| [14_thought_corpus_graph/](14_thought_corpus_graph/) | Typed-edge reasoning over a persistent message + paragraph corpus. Twelve edge types with schema-enforced rationale on the structural ones. PrizmForge-inspired thought-UID lineage so idea-identity survives supersession. Engagement-floor deprecation. Ingested from MultiAgent. | stack | 4 |

---

## How to use this kit

**To browse / understand:** start with [00_meta_stances/README.md](00_meta_stances/README.md), then [01_foundations/README.md](01_foundations/README.md), then any concept directory that catches your eye. Each concept's README is ~60-100 lines; you can decide depth as you go.

**To adopt one concept:** read that directory's README, then copy the schema/doctrine/enforcer files into the corresponding locations in your project (your migrations dir, your governance docs, your tests dir). Adapt naming to your project; the structure transplants directly. Each file states inline what it depends on and what it expects.

**To adopt the whole stack:** read [BACKGROUND.md](BACKGROUND.md) for the full narrative of how the pieces compose (originally written as a long-form proposal to a specific project, but the framing applies generally). Then walk the concept directories in order — 00 → 14 — building toward integration.

**To extend:** the elevation protocol ([09_elevation_protocol/](09_elevation_protocol/)) describes how new patterns earn promotion from project-layer sighting to stack-layer enforcer. The ingestion protocol ([12_ingestion_protocol/](12_ingestion_protocol/)) describes how external artifacts (other projects, papers) get broken down and incorporated. Together they cover both internally-surfaced and externally-sourced additions to the kit.

---

## Where this comes from

This kit is the project-layer extract from a three-layer doctrine system:

- **Universal layer** — `Cornerstones`: the F1-F3 + E1-E3 foundational invariants, plus the elevation protocol and lessons archive.
- **Stack layer** — `NewProjectSkelleton`: the Python+SQLite-specific derivation of those foundations, with ten subsystems and FOLLOWUPS items staged for promotion.
- **Project layer** — `TradeDesk`: the first project built on the skeleton, a single-user autonomous-agent operation where the patterns earned their first sightings.

The kit was assembled in 2026-05 as a transplantable reference for adjacent agent-governed projects.

---

## License

MIT. See [LICENSE](LICENSE).

## Contributing

This is a snapshot, not a maintained library. If a pattern here surfaces a gap or you have a sibling pattern, open an issue with the seed evidence (the concrete case that revealed the gap) and the proposed shape. Per the elevation protocol, *patterns are local sightings; enforcers are the home* — new entries earn their place by evidence, not by enthusiasm.
