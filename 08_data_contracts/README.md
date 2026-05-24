# 08 — Data Contracts

## The concept

> Four sub-components, all declarative Python files. **Fact Ownership Registry** maps each core data concept to its single authoritative source. **Computed Value Contracts** declare every cached value's formula, inputs, refresh trigger, and the mutation paths that must call the trigger. **Business Event Boundaries** declare the tables each business event touches and assert atomicity. **Schema Introspection** verifies the database schema matches structural policies at DDL level.

**Derives from:** Foundation [F2](../01_foundations/F2_logic_holds.md) (single source of truth applied to data; atomicity in cross-table updates; one formula per calculation; non-contradiction at the schema level). Also [F1](../01_foundations/F1_time_has_direction.md) (computed values are events with timestamps; refresh contracts are temporal).

## Why this matters for agent-governed systems

Without declarative data contracts, the data shape's correctness lives in code that operates on it — distributed across handlers, derivable only by tracing every call site. When agents propose changes, they have to *infer* the contract from the code, and inferences can be wrong.

With declarative contracts:

- **The contract is the source of truth.** When the agent asks *"where does net_profit come from?"*, the answer is in `fact_owners.py`, one line.
- **Tests verify reality matches declaration.** If a handler is modified and stops calling the refresh trigger, the test catches it.
- **Coverage is queryable.** What % of tables have declarations? Where are the undeclared areas? The System Reviewer's Layer 1 ([07_system_reviewer/](../07_system_reviewer/)) measures this.
- **The agent's pre-flight has a structural answer to question 2 ("what's the audit trail?").** The fact_owners declaration names the audit table; the agent doesn't have to guess.

For agent-governed systems specifically, this addresses a failure mode that's near-invisible without the contracts: *silent divergence between intent and reality*. The code says one thing; the doctrine says another; nobody notices until something breaks. Contracts make the gap visible at CI time.

## What's in this directory

| File | Purpose |
|---|---|
| [templates/fact_owners.py](templates/fact_owners.py) | The Fact Ownership Registry template. One entry per core data concept, naming its source function, storage location, and refresh trigger if cached. |
| [templates/computed_values.py](templates/computed_values.py) | The Computed Value Contracts template. One entry per stored computed value, naming formula, inputs, refresh trigger, and every mutation path that must call the trigger. |
| [templates/business_events.py](templates/business_events.py) | The Business Event Boundaries template. One entry per business event that touches multiple tables, naming the tables and asserting atomicity. |

Schema introspection isn't a template — it's a set of tests that query the live schema and verify policies (every FK has explicit cascade; every status column has CHECK constraint; etc.). These are project-specific; the doctrine in [02_audit_as_shape/](../02_audit_as_shape/)'s `decision_trigger.md` is the most concrete pointer.

## How to adopt

Adoption is incremental. Start sparse, grow organically.

1. **Create `contracts/fact_owners.py`** with two or three entries for your most important concepts. The system doesn't require completeness — it requires that whatever IS declared gets mechanically verified.

2. **Add tests that verify the declarations.** The pattern:
   - For each `fact_owners` entry, verify the `source` function exists and is callable.
   - For each `computed_values` entry, verify the `refresh_trigger` exists and that every `mutation_paths` function calls it (regex or AST scan).
   - For each `business_events` entry, verify the `handler` function exists and that its body actually touches all `tables_touched` in a single transaction.

   These tests run as part of [07_system_reviewer/](../07_system_reviewer/)'s Layer 1.

3. **Grow coverage as patterns emerge.** When you find yourself asking *"where does this value really come from?"* more than once, add a fact_owner declaration. When you store a derived value for the first time, add a computed_values contract. When a business event touches more than one table, add a business_events declaration.

4. **Wire the contracts into the pre-flight.** When the agent's pre-flight question 1 asks *"what doctrine governs this change?"* and the change touches a declared fact, the contract IS the answer — *"this concept is owned by `calculations.compute_net_profit`; this change must preserve the contract."*

## The maturity progression

- **Day one:** Three fact owners. One business event. Zero computed values (assuming you compute everything at query time by default).

- **Month one:** Twenty fact owners. Five business events. Two or three computed values (with full mutation_path coverage).

- **Mature:** Most major concepts declared. The System Reviewer's contract-coverage check reports >70%. Computed values are rare and each has documented refresh paths covering create/update/delete.

The progression matters. Trying to declare everything on day one is over-investment in a structure that doesn't yet have signal about what's important. Trying to declare nothing leaves the failure mode (silent divergence) wide open. The middle path is *declare what's load-bearing today; grow as new load-bearing concepts surface*.

## Cross-references

- [02_audit_as_shape/](../02_audit_as_shape/) — `fact_corrections` is the audit table that fact_owners entries name as their audit surface.
- [04_pre_flight_and_invariants/](../04_pre_flight_and_invariants/) — the pre-flight's question 1 ("what doctrine governs?") reads the contracts as one of its doctrine sources.
- [07_system_reviewer/](../07_system_reviewer/) — Layer 1's contract-coverage check measures how much of the schema has declared contracts.
- [01_foundations/F2_logic_holds.md](../01_foundations/F2_logic_holds.md) — the foundation this entire concept implements.
