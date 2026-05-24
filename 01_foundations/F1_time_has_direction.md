# F1 — Time has direction

## Statement

Past events cannot be unmade. Causality flows from earlier to later. What was true at a given moment remains true about that moment forever, even after the world changes.

## Type

Physical/Logical.

## Falsification condition

Demonstrated retrocausality — an effect that preceded its cause in the same reference frame. Not observed in any domain we operate in.

## Implies

- **Historical facts are immutable.** Records of what happened do not get DELETEd. Soft-void via lifecycle states (`closed`, `dismissed`, `voided`) with timestamps, never `DELETE FROM`.
- **Lifecycle transitions are events with timestamps.** Status columns are projections of the latest event, not the source of truth. A status field on its own is a label, not a state machine — every transition needs an event row with timestamp + reason + actor.
- **Audit is the shape of the data, not a feature added on top.** The schema must answer *"what was true at time T"* from its own structure. If the only way to answer is to dig through Git history of database backups, the schema is wrong.
- **Cached aggregates carry an `as_of` timestamp.** A cached value with no freshness signal is unverifiable. Consumers must be able to decide whether to recompute from the underlying event log.
- **Corrections are events.** A fact correction records prior value, new value, reason, confidence, timestamp; it never silently overwrites. See [02_audit_as_shape/](../02_audit_as_shape/) for the canonical `fact_corrections` table.
- **Schema migrations are append-only and ledger-tracked.** The history of schema evolution is itself a fact subject to F1. A migration runner with a `schema_versions` table is the structural form.
- **The corpus's own evolution is recorded.** Anchor histories on every foundation; conversation records for foundational dialogues; the elevation protocol's history of what was promoted/demoted when and why.

## Anchor history

- **2026-04-28** — Elevated. Triggered by a session evaluating one project's data structure that surfaced multiple schema-discipline violations all tracing back to "current state treated as source of truth" thinking. Multiple existing rules became explicable as instances of this deeper foundation; the elevation gate (generative force, reduction-resistance, independent cross-project triangulation) was satisfied.

## AI-dependency note

None. F1 is independent of AI capabilities.

## What derives from this foundation in this kit

- [02_audit_as_shape/](../02_audit_as_shape/) — every meaningful state change writes an append-only audit row in the same transaction.
- [03_classifier_and_audit_lane/](../03_classifier_and_audit_lane/) — the `auto_resolutions` table is append-only per F1; the only permitted mutation is `rolled_back_at + rollback_reason`.
- [05_lessons_loop/](../05_lessons_loop/) — `lesson_candidates` rows are written once at detection time and never updated; re-evaluation creates new candidate rows.
- The migration system at any stack layer — `schema_versions` ledger, never roll-back-as-DELETE.
