-- fact_corrections — the canonical audit table for fact mutations.
--
-- Derives from Foundation F1 (time has direction).
--
-- Every UPDATE on a meaningful business column writes a row here in the
-- same transaction as the UPDATE. The row records what was overwritten,
-- what replaced it, why, and how confident the change is.
--
-- Append-only. No UPDATEs to this table; corrections to corrections
-- happen by inserting a new row that references the original.
--
-- Adapt to your schema:
-- 1. The `domain` CHECK lists your project's domains (auction_item /
--    inventory_item / etc.). One entry per domain that has meaningful
--    business columns governed by the audit-requires-correction rule.
-- 2. The FK columns reference your project's tables. One nullable FK
--    column per domain.
-- 3. The discriminator CHECK ties `domain` to which FK column is set,
--    so a row's `domain='auction_item'` is consistent with
--    auction_item_id being non-NULL and the other FKs being NULL.
--
-- The JSON encoding for prior_value / new_value lets any fact type
-- (bool, number, string, null, object) round-trip losslessly.

CREATE TABLE IF NOT EXISTS fact_corrections (
    id INTEGER PRIMARY KEY AUTOINCREMENT,

    -- Discriminator: which domain this correction applies to.
    -- Extend the CHECK list when you add a new audited domain.
    domain TEXT NOT NULL
        CHECK(domain IN ('auction_item', 'inventory_item', 'auction')),

    -- One FK column per audited domain. Exactly one is non-NULL per row.
    -- Adapt the table references to your project's schema.
    auction_item_id INTEGER REFERENCES auction_items(id) ON DELETE CASCADE,
    inventory_id   INTEGER REFERENCES inventory(id)      ON DELETE CASCADE,
    auction_id     INTEGER REFERENCES auctions(id)       ON DELETE CASCADE,

    -- The fact being corrected. Use the column name as the convention.
    -- Example: 'category_id', 'purchase_price', 'condition_grade'.
    fact_name TEXT NOT NULL,

    -- Prior and new values, JSON-encoded for type-preserving round-trip.
    -- prior_value is NULL when this is a first-write (no prior existed).
    -- new_value is NULL only when the correction sets the fact to NULL.
    prior_value TEXT,
    new_value   TEXT NOT NULL,

    -- Why the correction happened. Free-text; keep it short and concrete.
    -- Examples: 'invoice import', 'user typed correction', 'AI re-identified
    -- with corrected size_class as context'.
    reason TEXT NOT NULL,

    -- Confidence in the new value. Use:
    --   'high'   — receipt, ground-truth source, user-stated fact
    --   'medium' — AI inference, heuristic, derived from related facts
    --   'low'    — guess, default, awaiting verification
    confidence TEXT NOT NULL
        CHECK(confidence IN ('high', 'medium', 'low')),

    -- When the correction was recorded. Default: now.
    created_at TEXT NOT NULL DEFAULT (datetime('now')),

    -- Who/what initiated the correction. Examples:
    --   'invoice_import' (system, batch import)
    --   'user_correction' (manual edit)
    --   'ai_estimator' (AI inference call)
    --   '<user_email>' (specific user, when multi-user)
    created_by TEXT,

    -- Discriminator/FK consistency: domain must match which FK column is set.
    -- Extend the OR clauses when you add a new audited domain.
    CHECK (
        (domain = 'auction_item'
            AND auction_item_id IS NOT NULL
            AND inventory_id    IS NULL
            AND auction_id      IS NULL) OR
        (domain = 'inventory_item'
            AND auction_item_id IS NULL
            AND inventory_id    IS NOT NULL
            AND auction_id      IS NULL) OR
        (domain = 'auction'
            AND auction_item_id IS NULL
            AND inventory_id    IS NULL
            AND auction_id      IS NOT NULL)
    )
);

-- Indexes for the common query shapes.
-- 1. "Show me all corrections to this row, newest first" — frequent in retrospection.
-- 2. "Show me all corrections of this fact_name" — for pattern detection.
-- 3. "Show me all corrections by this source in a window" — for source audit.

CREATE INDEX IF NOT EXISTS idx_fc_auction_item
    ON fact_corrections(auction_item_id, created_at DESC)
    WHERE auction_item_id IS NOT NULL;

CREATE INDEX IF NOT EXISTS idx_fc_inventory
    ON fact_corrections(inventory_id, created_at DESC)
    WHERE inventory_id IS NOT NULL;

CREATE INDEX IF NOT EXISTS idx_fc_auction
    ON fact_corrections(auction_id, created_at DESC)
    WHERE auction_id IS NOT NULL;

CREATE INDEX IF NOT EXISTS idx_fc_fact_name
    ON fact_corrections(fact_name, created_at DESC);

CREATE INDEX IF NOT EXISTS idx_fc_created_by
    ON fact_corrections(created_by, created_at DESC)
    WHERE created_by IS NOT NULL;
