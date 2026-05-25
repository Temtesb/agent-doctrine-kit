-- thought_corpus_graph — typed-edge reasoning over a persistent thought corpus.
--
-- Derives from Foundations F1 (every row is an immutable temporal fact;
-- lifecycle transitions are state-transition events) and F2 (typed edges
-- are single-source-of-truth for relationships; thought_uid is single-
-- source-of-truth for idea-identity across supersession).
--
-- Append-only per F1. The only "mutations" are state-transition writes
-- that record the transition as a new event (state='superseded'/
-- 'rolled_back' with superseded_by pointer, read_log inserts).
--
-- Ingested from MultiAgent with two improvements:
--   1. PrizmForge-inspired thought_uid lineage (paragraphs.thought_uid
--      column + helper-computed inheritance via supersedes edges)
--   2. Schema-level CHECK for rationale on contradicts/supersedes
--      (MultiAgent enforces at API level only; this subsystem makes it
--      structural)

PRAGMA foreign_keys = ON;

-- ─────────────────────────────────────────────────────────────────────────
-- participants — every actor (user + agents) is one row
-- ─────────────────────────────────────────────────────────────────────────
--
-- Per the user-is-a-participant meta-stance, the user is a row here
-- alongside any agents. Uniform protocol; downstream consumers handle
-- one shape.

CREATE TABLE IF NOT EXISTS participants (
    name TEXT PRIMARY KEY,
    display_name TEXT NOT NULL,
    -- Absolute path/URI to the participant's grounding doctrine.
    -- NULL for the user (their corpus is accumulated experience, not a file).
    origin_corpus TEXT,
    -- Free-text describing when this participant typically operates
    -- (e.g., 'user-driven', 'hourly run-loop', 'session-on-demand').
    active_cadence TEXT,
    registered_at TEXT NOT NULL DEFAULT (datetime('now')),
    notes TEXT
);

-- ─────────────────────────────────────────────────────────────────────────
-- messages — top-level contributions
-- ─────────────────────────────────────────────────────────────────────────

CREATE TABLE IF NOT EXISTS messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    thread_id TEXT NOT NULL,
    -- thread_active = 1 means the thread carries forward across days
    -- in default inbox queries; 0 means it's one-day-only.
    thread_active INTEGER NOT NULL DEFAULT 1 CHECK(thread_active IN (0, 1)),
    author TEXT NOT NULL REFERENCES participants(name),
    -- recipients: either the literal string 'all' (broadcast) or a
    -- JSON array of participant names. Both forms are accepted by readers.
    recipients TEXT NOT NULL,
    subject TEXT NOT NULL,
    body TEXT NOT NULL,
    -- State transitions: sent → superseded (replaced by a newer message
    -- via the superseded_by pointer) | rolled_back (the message was retracted,
    -- audit trail preserved per F1).
    state TEXT NOT NULL DEFAULT 'sent'
        CHECK(state IN ('sent', 'superseded', 'rolled_back')),
    superseded_by INTEGER REFERENCES messages(id),
    rollback_reason TEXT,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),

    -- Consistency: if state is superseded/rolled_back, the corresponding
    -- field must be populated.
    CHECK (state != 'superseded' OR superseded_by IS NOT NULL),
    CHECK (state != 'rolled_back' OR rollback_reason IS NOT NULL)
);

CREATE INDEX IF NOT EXISTS idx_msg_thread ON messages(thread_id, created_at);
CREATE INDEX IF NOT EXISTS idx_msg_author ON messages(author, created_at);
CREATE INDEX IF NOT EXISTS idx_msg_state ON messages(state) WHERE state != 'sent';

-- ─────────────────────────────────────────────────────────────────────────
-- paragraphs — voting/anchoring/edge-targeting unit
-- ─────────────────────────────────────────────────────────────────────────
--
-- A message decomposes into paragraphs on write. Each gets a stable UID
-- (`msg<id>-p<sequence>`) so edges can target individual claims.
--
-- thought_uid is the PrizmForge-inspired addition. A paragraph created
-- without supersession gets a fresh thought_uid (short UUID). A paragraph
-- with a supersedes edge to an earlier paragraph inherits the earlier
-- paragraph's thought_uid. The inheritance is performed at write time by
-- the helper; the schema just stores the result.

CREATE TABLE IF NOT EXISTS paragraphs (
    -- Composite UID: msg<id>-p<sequence>. Stable for the paragraph's lifetime.
    uid TEXT PRIMARY KEY,
    message_id INTEGER NOT NULL REFERENCES messages(id),
    -- Sequence within the message (1-indexed).
    sequence INTEGER NOT NULL,
    content TEXT NOT NULL,
    -- Idea-identity across supersession (the PrizmForge-inspired thought-UID).
    -- Computed at write time:
    --   - Paragraph with no supersedes edge: fresh short UUID
    --   - Paragraph with a supersedes edge: inherit from the superseded paragraph
    thought_uid TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),

    UNIQUE (message_id, sequence)
);

CREATE INDEX IF NOT EXISTS idx_para_thought ON paragraphs(thought_uid, created_at);
CREATE INDEX IF NOT EXISTS idx_para_message ON paragraphs(message_id, sequence);

-- ─────────────────────────────────────────────────────────────────────────
-- edges — typed relationships between paragraphs (and to external artifacts)
-- ─────────────────────────────────────────────────────────────────────────
--
-- Edges connect paragraphs to paragraphs (most common) or paragraphs to
-- external artifacts via URI (cites_artifact, anchors_to).
--
-- Schema-level CHECK improves on MultiAgent's API-only enforcement:
-- contradicts and supersedes structurally require rationale.

CREATE TABLE IF NOT EXISTS edges (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    edge_type TEXT NOT NULL CHECK(edge_type IN (
        'refines',         -- B sharpens or extends A
        'contradicts',     -- B disagrees with A; rationale REQUIRED
        'supports',        -- B agrees with A and adds evidence
        'references',      -- B cites A as context, no claim of agreement
        'supersedes',      -- B replaces A; A is now stale; rationale REQUIRED
        'derives_from',    -- B is a logical consequence of A
        'responds_to',     -- direct conversational reply
        'anchors_to',      -- B rests on doctrinal foundation A (often external URI)
        'cites_artifact',  -- B references an external artifact (commit, file, etc.)
        'endorsed_by',     -- participant explicitly agrees (stronger than read)
        'pinned_by',       -- participant pinned the paragraph as durable
        'deprecation_voted' -- participant voted to retire the paragraph
    )),
    -- from_para_uid is always a paragraph UID (the "source" of the edge).
    from_para_uid TEXT NOT NULL REFERENCES paragraphs(uid),
    -- to_target is either a paragraph UID OR an external URI (for
    -- anchors_to, cites_artifact). Validated by the helper, not the schema.
    to_target TEXT NOT NULL,
    -- Rationale: required for contradicts and supersedes (structural CHECK below).
    rationale TEXT,
    -- The participant who drew the edge.
    created_by TEXT NOT NULL REFERENCES participants(name),
    -- Optional weight (default 1.0) for emphasis. Reserved for future use.
    weight REAL NOT NULL DEFAULT 1.0,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    -- An edge can be superseded by a newer edge (e.g., the participant
    -- reconsidered). The superseded edge stays in the DB per F1.
    superseded_by INTEGER REFERENCES edges(id),

    -- Schema-level rationale enforcement for the structural edge types.
    -- Improvement over MultiAgent's API-level-only check.
    CHECK (
        edge_type NOT IN ('contradicts', 'supersedes')
        OR (rationale IS NOT NULL AND LENGTH(TRIM(rationale)) > 0)
    )
);

CREATE INDEX IF NOT EXISTS idx_edges_from ON edges(from_para_uid, edge_type);
CREATE INDEX IF NOT EXISTS idx_edges_to ON edges(to_target, edge_type);
CREATE INDEX IF NOT EXISTS idx_edges_type ON edges(edge_type, created_at)
    WHERE superseded_by IS NULL;
CREATE INDEX IF NOT EXISTS idx_edges_by ON edges(created_by, created_at);

-- ─────────────────────────────────────────────────────────────────────────
-- read_log — per-(message, participant) read receipts
-- ─────────────────────────────────────────────────────────────────────────
--
-- Separate from the edges table so read-event volume doesn't bloat
-- edge traversals. Used by the engagement-floor deprecation mechanism
-- in paragraphs_active.
--
-- Idempotent — re-reading the same message inserts a new row (preserving
-- the temporal record of when the participant most-recently engaged) but
-- the per-(message, participant) constraint via the helper deduplicates
-- if needed; the schema permits multiple reads-by-same-participant.

CREATE TABLE IF NOT EXISTS read_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    message_id INTEGER NOT NULL REFERENCES messages(id),
    participant TEXT NOT NULL REFERENCES participants(name),
    read_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_read_msg ON read_log(message_id, participant);
CREATE INDEX IF NOT EXISTS idx_read_recent ON read_log(participant, read_at DESC);

-- ─────────────────────────────────────────────────────────────────────────
-- paragraphs_active — projection of paragraph status (engagement-floor)
-- ─────────────────────────────────────────────────────────────────────────
--
-- Status logic (engagement-floor, NOT calendar-floor):
--   - 'pinned'      — any participant has a pinned_by edge on the paragraph
--   - 'rolled_back' — parent message state = 'rolled_back'
--   - 'deprecated'  — every participant that has read the parent message
--                     has voted to deprecate the paragraph (unanimity),
--                     AND no non-deprecation edge to the paragraph has
--                     been drawn since the most-recent deprecation vote
--   - 'active'      — otherwise
--
-- The engagement-floor replaces MultiAgent's 7-day calendar floor with
-- structural signal: if the paragraph has accumulated subsequent
-- structural use after a deprecation vote landed, it's demonstrably
-- still load-bearing.

CREATE VIEW IF NOT EXISTS paragraphs_active AS
WITH reader_counts AS (
    -- Distinct participants who have read the parent message
    SELECT
        p.uid AS para_uid,
        COUNT(DISTINCT rl.participant) AS reader_count
    FROM paragraphs p
    LEFT JOIN read_log rl ON rl.message_id = p.message_id
    GROUP BY p.uid
),
vote_counts AS (
    -- Distinct participants who have voted to deprecate the paragraph
    SELECT
        e.from_para_uid AS para_uid,
        COUNT(DISTINCT e.created_by) AS vote_count,
        MAX(e.created_at) AS last_vote_at
    FROM edges e
    WHERE e.edge_type = 'deprecation_voted' AND e.superseded_by IS NULL
    GROUP BY e.from_para_uid
),
engagement_after_vote AS (
    -- Any non-deprecation edge drawn after the most-recent deprecation vote
    -- demonstrates load-bearing-ness (engagement-floor signal).
    SELECT
        e.to_target AS para_uid,
        MAX(e.created_at) AS last_engagement_at
    FROM edges e
    JOIN vote_counts vc ON vc.para_uid = e.to_target
    WHERE e.edge_type NOT IN ('deprecation_voted', 'read_by')
      AND e.superseded_by IS NULL
      AND e.created_at > vc.last_vote_at
    GROUP BY e.to_target
),
pinned AS (
    SELECT DISTINCT from_para_uid AS para_uid
    FROM edges
    WHERE edge_type = 'pinned_by' AND superseded_by IS NULL
)
SELECT
    p.uid AS para_uid,
    p.message_id,
    p.sequence,
    p.thought_uid,
    p.content,
    p.created_at,
    CASE
        WHEN pn.para_uid IS NOT NULL THEN 'pinned'
        WHEN m.state = 'rolled_back' THEN 'rolled_back'
        WHEN rc.reader_count > 0
            AND vc.vote_count >= rc.reader_count
            AND ea.last_engagement_at IS NULL
            THEN 'deprecated'
        ELSE 'active'
    END AS status
FROM paragraphs p
JOIN messages m ON m.id = p.message_id
LEFT JOIN reader_counts rc ON rc.para_uid = p.uid
LEFT JOIN vote_counts vc ON vc.para_uid = p.uid
LEFT JOIN engagement_after_vote ea ON ea.para_uid = p.uid
LEFT JOIN pinned pn ON pn.para_uid = p.uid;
