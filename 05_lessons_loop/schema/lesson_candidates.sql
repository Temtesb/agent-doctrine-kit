-- lesson_candidates — append-only candidate table for repeated-pattern detection.
--
-- Derives from Foundations F1 (each row is an event, lifecycle
-- transitions happen via UPDATE-of-status with decided_at) and E1
-- (the suggested_invariant and suggested_doctrine_update fields are
-- AI hypotheses; the user's status decision is the verification).
--
-- Rows are written once at detection time. The only updates allowed
-- are the lifecycle transitions:
--   - status: pending → accepted/rejected/suppressed/duplicate
--   - decided_at, decided_by, decision_notes
--   - invariant_test_path, invariant_test_generated_at (when stub generator runs)
--   - pattern_library_entry (when stub generator appends to PATTERNS.md)
--
-- The snapshot fields (distinct_check_count, distinct_check_ids,
-- total_violation_count, window_days) are frozen at detection time and
-- never updated. Re-evaluation of the same principle later creates a
-- new candidate row, not an update.

CREATE TABLE IF NOT EXISTS lesson_candidates (
    id INTEGER PRIMARY KEY AUTOINCREMENT,

    -- When the detection logic fired. Default: now.
    detected_at TEXT NOT NULL DEFAULT (datetime('now')),

    -- The governing principle the detected pattern violates. Use the
    -- anchor format your project uses (§N.M / F1 / E2 / P00N).
    governing_principle TEXT NOT NULL,

    -- Snapshot of the detection state — frozen at detected_at.
    -- distinct_check_count: how many distinct integrity check names
    --   contributed violations under this principle within the rolling
    --   window. Used by the dual-trigger detector to fire on "distinct
    --   checks ≥ 3" OR "total violations ≥ 100" (both surface different
    --   shapes of recurrence).
    distinct_check_count INTEGER NOT NULL,

    -- JSON-encoded list of the distinct check names that contributed.
    -- Used by the AI drafter to ground the suggestion in concrete
    -- examples ("the same principle was violated by checks X, Y, Z").
    distinct_check_ids TEXT NOT NULL,

    -- Total violating row count summed across the contributing checks
    -- within the window. Snapshot at detected_at; not refreshed.
    total_violation_count INTEGER NOT NULL,

    -- Window length in days at detection time. Adapt the default in
    -- your detection code; the field records what was used.
    window_days INTEGER NOT NULL,

    -- AI-drafted suggestions. Populated when the candidate is created
    -- (the drafter runs once, immediately, in the same transaction).
    -- NULL on AI failure (rate limit, parse error, no key) — the user
    -- can still accept the candidate and write the suggestion manually.
    -- Per E1, these are hypotheses; the user's decision is verification.
    suggested_invariant       TEXT,
    suggested_doctrine_update TEXT,

    -- Lifecycle status. Per F1, transitions write decided_at +
    -- decided_by + the new status; never silently overwrite earlier
    -- rows.
    --
    -- - pending: awaiting user decision
    -- - accepted: user confirmed the pattern; stub generator should run
    -- - rejected: user dismissed the pattern; not real or not worth enforcing
    -- - suppressed: real pattern but user explicitly doesn't want enforcement
    --   (e.g., the failure mode is acceptable in this project's context)
    -- - duplicate: pattern overlaps with an earlier candidate; reference that one
    status TEXT NOT NULL DEFAULT 'pending'
        CHECK(status IN ('pending', 'accepted', 'rejected', 'suppressed', 'duplicate')),
    decided_at     TEXT,
    decided_by     TEXT,
    decision_notes TEXT,

    -- Stub-generator outputs. Set when the generator runs on an
    -- accepted candidate. The generator is idempotent — these fields
    -- being non-NULL means the stub already exists; the generator
    -- skips the candidate on a re-run.
    --
    -- invariant_test_path: where the generated test file lives, e.g.,
    --   'tests/test_arch_invariants_candidate_42.py'
    -- invariant_test_generated_at: when the generator ran
    -- pattern_library_entry: the P00N anchor appended to PATTERNS.md
    --   (atomic with invariant_test_path — the generator writes both
    --   or neither)
    invariant_test_path         TEXT,
    invariant_test_generated_at TEXT,
    pattern_library_entry       TEXT
);

-- Indexes for the common query shapes.
-- 1. "Show me all pending candidates" — for the user decision queue.
-- 2. "Group candidates by principle" — for trend analysis.
-- 3. "Show me accepted candidates without generated artifacts" — for
--    the stub generator's catch-up pass.

CREATE INDEX IF NOT EXISTS idx_lc_status
    ON lesson_candidates(status, detected_at);

CREATE INDEX IF NOT EXISTS idx_lc_principle
    ON lesson_candidates(governing_principle, status);

CREATE INDEX IF NOT EXISTS idx_lc_accepted_pending_stub
    ON lesson_candidates(status, invariant_test_generated_at)
    WHERE status = 'accepted' AND invariant_test_generated_at IS NULL;
