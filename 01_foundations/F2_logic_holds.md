# F2 — Mathematics and logic hold

## Statement

Numbers behave as numbers. Logical inference is valid. A statement cannot simultaneously be true and false in the same sense at the same time.

## Type

Physical/Logical.

## Falsification condition

A coherent demonstration that the laws of arithmetic or classical logic fail. Cannot exist within a system that uses those laws to make the demonstration.

## Implies

- **Single source of truth.** A given fact has one value; two storage locations disagreeing about the same fact mean at least one is wrong. If denormalization is genuinely needed for performance, document the cache, the source, and the refresh path covering create/update/delete.
- **Foreign key consistency.** A reference points to exactly one entity; polymorphic FKs are smells. Every FK must declare `ON DELETE CASCADE` or `ON DELETE RESTRICT` explicitly — never leave it to the database's silent default.
- **Atomicity in cross-table updates.** Multiple tables representing one logical state must remain consistent; transactions enforce this. A business event that touches N tables must wrap all N writes in a single transaction.
- **One formula per calculation.** Two implementations of the same formula will diverge unless kept structurally identical; extract the formula into one function and call it everywhere.
- **Deterministic computation.** Same inputs, same outputs. Non-determinism in calculation paths is a defect.
- **Computed values are outputs, not inputs.** Users correct the underlying facts that the formula consumes; the formula recomputes downstream. UI must never expose a direct-edit field for a computed value.
- **Canonical response shape.** Two endpoints with two different shapes for "success" or "failure" are two storage locations claiming to represent the same logical state. The shape must be canonical per system.
- **URL canonicalization.** When the same logical entity has multiple valid URL representations (with/without trailing slash, with/without slug, etc.), storing one form and looking up another is two storage locations claiming to represent the same fact. URL is data; the non-contradiction rule applies.

## Anchor history

- **2026-04-28** — Elevated. Triggered by recognition that the schema-discipline rules around single source of truth, FK policy, and computed values all derive from non-contradiction applied to data storage. Multiple rules at the stack layer (canonical response shape, atomicity wrapping, formula extraction) became explicable as instances of the same underlying foundation.

## AI-dependency note

None. F2 is independent of AI capabilities.

## What derives from this foundation in this kit

- [02_audit_as_shape/](../02_audit_as_shape/) — single source of truth applied to the historical record of fact mutations.
- [08_data_contracts/](../08_data_contracts/) — fact ownership registry, computed value contracts, business event transaction boundaries.
- [10_followups_patterns/static_coupling_invariants.md](../10_followups_patterns/static_coupling_invariants.md) — F2 at the file-boundary layer: a name on one side of a cross-file boundary must resolve to a definition on the other side.
