# Doctrine excerpt — the decision trigger

Place this in your governance doc (CLAUDE.md or equivalent) under the section governing data mutations. The decision trigger is the structural cue that fires at the agent's write moment.

---

## Corrections are events, not overwrites

**Derives from:** Foundation [F1 — time has direction](../../01_foundations/F1_time_has_direction.md).

Fact corrections record prior value, new value, reason, confidence, timestamp; they never silently overwrite. The pattern generalizes — any mutation of a meaningful fact should leave a trail. Direct UPDATE statements that replace a value without recording its prior state are a smell.

**Falsification condition:** A scheme that preserves prior values *without* a paired audit row — for example, a temporal database that automatically versions every column. Under such a scheme, the explicit `fact_corrections` row is redundant. If your project adopts such a scheme, this rule is a candidate for revision.

### The decision trigger

**Before writing any UPDATE that replaces an existing value in a meaningful business column, pause and ask:**

> *"Am I overwriting a prior value that some future reader might want to know about?"*

If the answer is yes, write a `fact_corrections` row in the same transaction as the UPDATE. Required fields:

- `prior_value` and `new_value`, JSON-encoded for type-preserving round-trip
- `reason` — short and concrete (`'invoice import'`, `'user typed correction'`, `'AI re-identified with corrected size_class as context'`)
- `confidence` — `'high'` for receipts and ground-truth sources, `'medium'` for AI/heuristic, `'low'` for guesses
- `created_by` — the source (`'invoice_import'`, `'user_correction'`, `'ai_estimator'`, or a user identifier)

This applies whether the correction is user-initiated or system-derived. New writers default to writing the audit row; the bar to skip it is *"this is a first write, no prior value exists"* — not convenience.

### Meaningful business columns

A column is "meaningful" if a future reader might reasonably ask *"what was this before?"* Examples that almost always qualify:

- Core lifecycle / state — `current_stage`, `status`, `decision`
- Money — `sale_price`, `purchase_price`, `cost_basis`, fees, premiums
- Identity / classification — `title`, `description`, `condition_grade`, `category_id`
- FK rewrites (re-pointing parentage) — `auction_item_id`, `inventory_id`, signature/group IDs
- Append-only event prices — observation prices in comp tables, snapshot prices

Examples that usually do NOT qualify (lifecycle-transition timestamps where the column transition itself IS the audit):

- `voided_at`, `closed_at`, `cancelled_at`, `ended_at` — these are pure NULL→timestamp transitions; the timestamp arrival is the new fact and there is nothing prior to overwrite

The list is project-specific; declare it explicitly. See [08_data_contracts/](../../08_data_contracts/) for how to formalize the list as a declarative registry.

### Why this matters

If the only way to ask *"what did this row look like a week ago?"* is to dig through Git history of database backups, the schema is wrong. The event log should make that question answerable from the live DB. Detection of drift, pattern recognition across corrections, trust ratcheting on change shapes — all depend on this property.

This is the per-row, fine-grained sibling of the lifecycle-events pattern: lifecycle transitions go in a `pipeline_events` (or equivalent) table; fact corrections go in `fact_corrections`. Together they make the historical state of any row reconstructable from the live DB.

### Audit row patterns

**First write** (no prior value): write the row to the business table normally. No `fact_corrections` row needed unless your project requires audit on first writes too (rare).

**Correction** (prior value exists): write the UPDATE to the business table AND insert a `fact_corrections` row in the same transaction. Both succeed or both fail.

**Bulk re-import** (large set of corrections): same pattern, one `fact_corrections` row per business-table row corrected, all wrapped in one transaction or batched transactions. The audit volume is the cost of the audit being the shape of the data; budget accordingly.

**System-derived correction** (AI re-identifies, scheduled re-import, etc.): same pattern, with `created_by` indicating the source and `confidence='medium'` (lower than user-stated corrections because the source itself is hypothesis, per [E1](../../01_foundations/E1_corpus_is_hypothesis.md)).

### The structural enforcer

The architecture invariant test at [../enforcer/test_update_requires_fact_correction.py](../enforcer/test_update_requires_fact_correction.py) catches violations at CI time. Per the *prefer enforcers over principles* meta-stance, the test is the primary mechanism; this doctrine entry exists to explain *why* the test exists, not to enforce the rule on its own.
