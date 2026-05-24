-- auto_resolutions — the audit lane for agent-resolved findings.
--
-- Derives from Foundation F1 (time has direction) and F2 (single source
-- of truth for the classifier's verdict on each finding).
--
-- Every finding that the classifier (see ../doctrine/four_criteria.md)
-- routes to the agent lane, and that the agent then acts on, produces
-- one row here. The row records:
--   - which finding type drove the resolution
--   - what changed (one-line summary)
--   - which commit landed the change
--   - test results bracketing the change
--   - which doctrine clause justified the routing
--   - which classifier criteria matched
--
-- Append-only per F1. The only permitted mutation is the
-- (rolled_back_at + rollback_reason) pair, populated by a post-revert
-- hook when the user reverts the agent's commit. A revert event drops
-- the trust score for the resolution's "shape" (governing_principle +
-- finding_source_type + change-pattern fingerprint) back to 0 and
-- re-engages digest surfacing for that shape.
--
-- Surfaced via a daily digest in the morning briefing (or equivalent)
-- until the trust ratchet has enough data to suppress well-understood
-- shapes.

CREATE TABLE IF NOT EXISTS auto_resolutions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,

    -- When the agent resolved the finding. Default: now.
    resolved_at TEXT NOT NULL DEFAULT (datetime('now')),

    -- What kind of finding drove this resolution. Extend the CHECK list
    -- when you add new finding-source types.
    finding_source_type TEXT NOT NULL CHECK(
        finding_source_type IN (
            'dissonance',                 -- a recorded tension between principles
            'architecture_proposal',      -- a structural proposal from the System Reviewer
            'integrity_violation',        -- an integrity check that fired
            'lesson_candidate'            -- a repeated-pattern detection
        )
    ),

    -- Stable reference to the source finding. Format depends on the
    -- finding_source_type — for example, the row ID in the dissonance
    -- ledger, the proposal's anchor (P-NNN), or the lesson_candidate's
    -- primary key. Keep as TEXT to allow flexible reference formats.
    finding_source_id TEXT NOT NULL,

    -- One-sentence summary of what the agent changed. Keep concise;
    -- the commit message has the full detail.
    change_summary TEXT NOT NULL,

    -- The Git SHA of the resolution commit. Use the full 40-character
    -- hash for stability; the digest displays the short form.
    commit_sha TEXT NOT NULL,

    -- Test outcomes bracketing the change.
    -- tests_passed_before: count of tests passing before the change.
    -- tests_passed_after: count after the change.
    -- NULL is allowed if your project doesn't have a uniform test count
    -- (e.g., distinct test suites with different totals); prefer to
    -- populate with the count from the suite most relevant to the change.
    tests_passed_before INTEGER,
    tests_passed_after  INTEGER,

    -- Which doctrine clause justified the routing decision. Use the
    -- anchor format your project uses — `§N.M` (CLAUDE.md section),
    -- `F1`/`E2` (universal foundation), `P00N` (pattern library entry).
    -- The classifier records this; the trust ratchet groups by it.
    governing_principle TEXT NOT NULL,

    -- JSON-encoded record of which classifier criteria matched. Example:
    --   '{"doctrine_names_answer": true,
    --     "pattern_exists": true,
    --     "verification_mechanical": true,
    --     "reversible": true,
    --     "user_required_triggers": []}'
    -- Stored as TEXT for SQLite portability; parse with json.loads.
    classifier_criteria_met TEXT NOT NULL,

    -- Rollback pair — populated by the post-revert hook when the user
    -- reverts the agent's commit. NULL means the resolution is still
    -- accepted (or hasn't yet been reverted). Once populated, immutable;
    -- a second revert produces a new auto_resolutions row referencing
    -- the rollback as its own change_summary.
    rolled_back_at  TEXT,
    rollback_reason TEXT
);

-- Indexes for the common query shapes.
-- 1. "Show me resolutions from the past 24 hours" — daily digest.
-- 2. "Show me all resolutions of this shape" — trust ratchet aggregation.
-- 3. "Find resolution by source finding" — when investigating a revert.

CREATE INDEX IF NOT EXISTS idx_ar_resolved_at
    ON auto_resolutions(resolved_at DESC);

CREATE INDEX IF NOT EXISTS idx_ar_shape
    ON auto_resolutions(governing_principle, finding_source_type, resolved_at DESC);

CREATE INDEX IF NOT EXISTS idx_ar_source
    ON auto_resolutions(finding_source_type, finding_source_id);

CREATE INDEX IF NOT EXISTS idx_ar_rolled_back
    ON auto_resolutions(rolled_back_at)
    WHERE rolled_back_at IS NOT NULL;
