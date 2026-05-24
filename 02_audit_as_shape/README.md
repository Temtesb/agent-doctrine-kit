# 02 — Audit is the shape of the data

## The concept

> Every meaningful state change writes an append-only audit row in the same transaction. The schema makes the history queryable; nothing has to be remembered to enable retrospection.

**Derives from:** Foundation [F1 — time has direction](../01_foundations/F1_time_has_direction.md). History must answer *"what was true at time T"*. Status fields that get overwritten erase the answer; append-only event logs preserve it.

## Why this matters for agent-governed systems

The most common failure mode in systems where state changes get persisted as status-field overwrites: *"I know it's in this state now, but I don't know how it got there, or who changed it, or what it was before, or what evidence drove the change."*

For agent-governed systems specifically, this failure compounds. Multiple agents propose, review, and apply changes. Each agent's actions are followed by other agents that depend on the historical record. Without the audit being the *shape of the data*, every retrospective question requires reconstruction from logs — which is slow, error-prone, and produces lower confidence than reading the substrate directly.

The substrate-as-audit shape enables:

- **Retrospection.** *"What changed in this row in the last 24 hours? Why? Who decided?"* — single query.
- **Pattern detection.** *"What kinds of changes are getting rolled back?"* — aggregation over the audit table.
- **Trust ratcheting.** *"How many times has this change shape succeeded without rollback?"* — see [03_classifier_and_audit_lane/](../03_classifier_and_audit_lane/) for the mechanism that depends on this substrate.
- **Cross-agent coordination.** A second agent reading a row can see *why* it was last modified and by whom, not just *what* the current value is.

## What's in this directory

| File | Purpose |
|---|---|
| [schema/fact_corrections.sql](schema/fact_corrections.sql) | The canonical audit table. Drops into your migrations directory; adapt the `domain` CHECK and FK columns to your schema. |
| [doctrine/decision_trigger.md](doctrine/decision_trigger.md) | The principle text that goes in your governance doc, with the decision-trigger question agents ask before any UPDATE. |
| [enforcer/test_update_requires_fact_correction.py](enforcer/test_update_requires_fact_correction.py) | The architecture invariant test that fails CI if any function UPDATEs a meaningful business column without writing to an audit table. Uses the `_KNOWN_ALLOWED` ratchet pattern. |

## How to adopt

1. **Copy the schema** ([schema/fact_corrections.sql](schema/fact_corrections.sql)) into your migrations directory. Adapt:
   - The `domain` CHECK to list your project's domains (auction_item / inventory_item / etc.)
   - The FK columns to reference your project's tables
   - The discriminator CHECK that ties `domain` to which FK column is set

2. **Copy the doctrine** ([doctrine/decision_trigger.md](doctrine/decision_trigger.md)) into your governance doc (CLAUDE.md or equivalent). Place it under the section governing data mutations. Adapt the project-name references but keep the decision trigger verbatim — it's the structural cue that fires at the agent's write moment.

3. **Copy the enforcer** ([enforcer/test_update_requires_fact_correction.py](enforcer/test_update_requires_fact_correction.py)) into your tests directory. Adapt:
   - `MEANINGFUL_BUSINESS_COLUMNS` to your project's column list
   - `AUDIT_TABLES` to your project's audit-table list
   - `_EXCLUDED_FILENAMES` to your schema-authority files (the test should skip migrations, schema DDL, etc.)
   - `_KNOWN_ALLOWED` starts empty; baseline current state by running the test, adding any legitimate exceptions with inline justification, then ratchet down over time

4. **Verify by running the test.** It should fail on any existing UPDATE that doesn't pair with an audit-table INSERT. Either fix the call site (add the audit row) or add the function to `_KNOWN_ALLOWED` with justification.

## Adapting beyond UPDATE

The pattern generalizes. Any mutation of a meaningful fact should leave a trail. Apply the same shape to:

- **Status transitions** — see [01_foundations/F1_time_has_direction.md](../01_foundations/F1_time_has_direction.md) on lifecycle events. A `pipeline_events` table (or equivalent) records every status transition with timestamp + reason + actor.
- **AI outputs** — see [10_followups_patterns/](../10_followups_patterns/) for the AI-output verification pattern. AI outputs route through audit/candidate tables before promotion to business columns.
- **Cached aggregates** — every cached aggregate carries an `as_of` timestamp so consumers can decide whether to recompute. The audit table for the underlying inputs is what makes the cache verifiable.

## Cross-references

- [01_foundations/F1_time_has_direction.md](../01_foundations/F1_time_has_direction.md) — the foundation this concept implements.
- [03_classifier_and_audit_lane/](../03_classifier_and_audit_lane/) — the `auto_resolutions` table is a sibling audit lane for agent-resolved findings; same shape, different scope.
- [04_pre_flight_and_invariants/](../04_pre_flight_and_invariants/) — the design-time pre-flight's second question asks "what's the audit trail?" — this concept is the structural answer.
- [05_lessons_loop/](../05_lessons_loop/) — `lesson_candidates` rows are themselves append-only per F1; the loop closes when a candidate is `accepted` and an invariant test is generated.
- [08_data_contracts/](../08_data_contracts/) — the fact ownership registry declares which columns are meaningful and which audit table they pair with.
