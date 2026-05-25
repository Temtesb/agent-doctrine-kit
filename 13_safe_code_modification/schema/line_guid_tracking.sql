-- line_guid_tracking — stable per-line identifiers for safe code modification.
--
-- Derives from Foundation F1 (the file's state is a temporal fact;
-- the GUID-to-content mapping IS the temporal record) and F2 (the
-- GUID is single-source-of-truth for line identity, distinct from
-- the line's volatile position).
--
-- Each row records one line in one tracked file:
--   - The line's stable GUID (deterministic from content + offset
--     at tracking-init time)
--   - The line's current position in the file (updated on every apply)
--   - The line's content hash (updated on every apply)
--   - When the row was last touched
--
-- Append-only-with-state-transitions per F1: rows are inserted on
-- file-tracking-init or on new-line insertion; updated on line-content
-- change (the update IS the state transition recording new content +
-- new position). Lines that are deleted get marked deleted_at + their
-- row remains for historical lookup (per F1 — deletion is itself a
-- fact subject to F1).
--
-- The algorithm_version field on the tracking row exists to support
-- future GUID-algorithm migrations without invalidating existing GUIDs.

CREATE TABLE IF NOT EXISTS line_guid_tracking (
    -- Composite primary key: file + GUID
    file_path TEXT NOT NULL,
    line_guid TEXT NOT NULL,

    -- Current state (updated on each apply that affects this line)
    current_line_number INTEGER NOT NULL,
    content_hash TEXT NOT NULL,             -- SHA-256 of current line content
    content TEXT NOT NULL,                  -- the current content itself (for read-without-file)

    -- Origin state (set at first-tracking time, never updated)
    original_content_hash TEXT NOT NULL,
    original_line_number INTEGER NOT NULL,
    tracking_started_at TEXT NOT NULL DEFAULT (datetime('now')),

    -- Version of the GUID-assignment algorithm used to assign this GUID.
    -- Allows future algorithm migrations: a new algorithm's GUIDs use a
    -- higher version number; existing rows keep their original assignment.
    algorithm_version INTEGER NOT NULL DEFAULT 1,

    -- Lifecycle state. Per F1, deletion is a state transition recorded
    -- as a timestamp + reason rather than a row removal.
    deleted_at TEXT,
    deleted_reason TEXT,

    -- Last apply that touched this row
    last_apply_at TEXT NOT NULL DEFAULT (datetime('now')),
    last_apply_proposal_id TEXT,            -- audit trail back to the proposal

    PRIMARY KEY (file_path, line_guid),

    CHECK (
        (deleted_at IS NULL AND deleted_reason IS NULL) OR
        (deleted_at IS NOT NULL AND deleted_reason IS NOT NULL)
    )
);

-- ─────────────────────────────────────────────────────────────────────────
-- file_state_snapshots — per-file content-hash snapshots for the
-- optimistic-concurrency check.
-- ─────────────────────────────────────────────────────────────────────────
--
-- When a proposal is drafted, the file's full-content hash is recorded
-- here as the "drafted_against" snapshot. At apply time, the current
-- file hash is computed and compared. Mismatch → proposal rejected as
-- conflicted; the file moved between draft and apply.

CREATE TABLE IF NOT EXISTS file_state_snapshots (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    file_path TEXT NOT NULL,

    -- The full-file content hash (SHA-256 of file bytes) at the
    -- moment this snapshot was captured.
    full_content_hash TEXT NOT NULL,

    -- When the snapshot was captured.
    captured_at TEXT NOT NULL DEFAULT (datetime('now')),

    -- What captured the snapshot. Examples:
    --   'proposal_draft' — captured when a proposal targeting this file was drafted
    --   'edit_apply' — captured immediately after an apply landed
    --   'manual_resync' — captured by a user-initiated resync command
    captured_by TEXT NOT NULL,

    -- Optional reference to the proposal/event that triggered the capture.
    triggering_proposal_id TEXT
);

-- ─────────────────────────────────────────────────────────────────────────
-- Indexes
-- ─────────────────────────────────────────────────────────────────────────

-- Lookup by file + GUID — the hot path for both edit-draft and edit-apply.
-- (Already covered by the primary key but explicit for clarity.)

-- Lookup current state of all lines in a file, ordered by current line number
-- — used at apply time to compute the new file content from the GUID table.
CREATE INDEX IF NOT EXISTS idx_lgt_file_order
    ON line_guid_tracking(file_path, current_line_number)
    WHERE deleted_at IS NULL;

-- Lookup deleted lines for a file (historical queries).
CREATE INDEX IF NOT EXISTS idx_lgt_deleted
    ON line_guid_tracking(file_path, deleted_at)
    WHERE deleted_at IS NOT NULL;

-- Snapshot lookup by file, newest first — used by the apply-time check
-- to find "what was this file's state when the proposal was drafted?"
CREATE INDEX IF NOT EXISTS idx_fss_file_recent
    ON file_state_snapshots(file_path, captured_at DESC);

-- Snapshot lookup by triggering proposal — used by the post-write
-- invalidation pass.
CREATE INDEX IF NOT EXISTS idx_fss_proposal
    ON file_state_snapshots(triggering_proposal_id)
    WHERE triggering_proposal_id IS NOT NULL;
