"""Thought-corpus helpers — typed-edge reasoning over a persistent corpus.

Derives from Foundations F1 (append-only with state-transitions as events)
and F2 (typed edges and thought-UIDs as single-source-of-truth for
relationships and idea-identity respectively).

Ingested from MultiAgent's multiagent.py with two improvements:
  1. PrizmForge-inspired thought_uid lineage (computed from supersession
     edges at write time; deterministic, not AI-judged)
  2. Schema-level enforcement of rationale on contradicts/supersedes
     (improvement enforced at the DB layer; helpers also validate early)

API surface mirrors MultiAgent for familiarity, with dataclass returns
and type hints for static analysis.
"""

from __future__ import annotations

import json
import sqlite3
import uuid
from contextlib import contextmanager
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterator, Optional, Sequence, Union

# ─── Default DB path ─────────────────────────────────────────────────────
# Adapt for your project. The helper functions accept an explicit conn
# parameter; this default is just for module-level convenience.

DEFAULT_DB_PATH = Path.home() / "thought_corpus.db"

# Edge types whose rationale is structurally required.
RATIONALE_REQUIRED = {"contradicts", "supersedes"}


# ─── Data shapes ────────────────────────────────────────────────────────


@dataclass
class Message:
    id: int
    thread_id: str
    thread_active: bool
    author: str
    recipients: Union[str, list[str]]
    subject: str
    body: str
    state: str
    superseded_by: Optional[int]
    rollback_reason: Optional[str]
    created_at: str


@dataclass
class Paragraph:
    uid: str
    message_id: int
    sequence: int
    content: str
    thought_uid: str
    created_at: str
    status: str = "active"  # populated when read via paragraphs_active


@dataclass
class Edge:
    id: int
    edge_type: str
    from_para_uid: str
    to_target: str
    rationale: Optional[str]
    created_by: str
    weight: float
    created_at: str
    superseded_by: Optional[int]


@dataclass
class InboxEntry:
    message: Message
    paragraphs: list[Paragraph]


# ─── Connection management ──────────────────────────────────────────────


@contextmanager
def _open_conn(conn: Optional[sqlite3.Connection] = None,
               db_path: Path = DEFAULT_DB_PATH) -> Iterator[sqlite3.Connection]:
    """Open a connection (or use the provided one). Ensures foreign_keys=ON."""
    if conn is not None:
        yield conn
        return
    own = sqlite3.connect(str(db_path))
    own.row_factory = sqlite3.Row
    own.execute("PRAGMA foreign_keys = ON")
    try:
        yield own
        own.commit()
    finally:
        own.close()


# ─── Participant registration ──────────────────────────────────────────


def register_participant(
    name: str,
    display_name: str,
    origin_corpus: Optional[str] = None,
    active_cadence: Optional[str] = None,
    notes: Optional[str] = None,
    conn: Optional[sqlite3.Connection] = None,
) -> None:
    """Idempotent participant registration.

    Re-registering an existing participant updates descriptive fields
    (display_name, origin_corpus, active_cadence, notes) without changing
    registered_at.
    """
    with _open_conn(conn) as c:
        c.execute(
            """
            INSERT INTO participants (name, display_name, origin_corpus,
                                       active_cadence, notes)
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(name) DO UPDATE SET
                display_name = excluded.display_name,
                origin_corpus = excluded.origin_corpus,
                active_cadence = excluded.active_cadence,
                notes = excluded.notes
            """,
            (name, display_name, origin_corpus, active_cadence, notes),
        )


# ─── Message + paragraph writing ───────────────────────────────────────


def write_message(
    thread_id: str,
    author: str,
    recipients: Union[str, Sequence[str]],
    subject: str,
    body: str,
    thread_active: bool = True,
    responds_to_msg_id: Optional[int] = None,
    supersedes_para_uid: Optional[str] = None,
    supersedes_rationale: Optional[str] = None,
    conn: Optional[sqlite3.Connection] = None,
) -> int:
    """Append a message; decompose body into paragraph rows; optionally
    auto-draw a responds_to edge AND/OR a supersedes edge.

    If supersedes_para_uid is provided:
      - supersedes_rationale must be non-empty (CHECK constraint will
        otherwise reject the edge)
      - the new message's paragraph(s) inherit the superseded paragraph's
        thought_uid (lineage)
    Otherwise each new paragraph gets a fresh thought_uid.

    Returns the new message's id.
    """
    if isinstance(recipients, (list, tuple)):
        recipients_text = json.dumps(list(recipients))
    else:
        recipients_text = recipients  # e.g., the literal string 'all'

    if supersedes_para_uid and not (supersedes_rationale or "").strip():
        raise ValueError(
            "supersedes_rationale is required when supersedes_para_uid is set"
        )

    paragraphs_text = [p.strip() for p in body.split("\n\n") if p.strip()]
    if not paragraphs_text:
        paragraphs_text = [body.strip()]

    with _open_conn(conn) as c:
        # Determine the thought_uid for the new paragraphs.
        if supersedes_para_uid:
            row = c.execute(
                "SELECT thought_uid FROM paragraphs WHERE uid = ?",
                (supersedes_para_uid,),
            ).fetchone()
            if row is None:
                raise ValueError(
                    f"supersedes_para_uid {supersedes_para_uid!r} not found"
                )
            inherited_thought = row["thought_uid"]
        else:
            inherited_thought = None

        cur = c.execute(
            """
            INSERT INTO messages
                (thread_id, thread_active, author, recipients, subject, body)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (thread_id, 1 if thread_active else 0, author, recipients_text,
             subject, body),
        )
        msg_id = cur.lastrowid

        for seq, content in enumerate(paragraphs_text, start=1):
            uid = f"msg{msg_id}-p{seq}"
            thought_uid = inherited_thought or _short_uuid()
            c.execute(
                """
                INSERT INTO paragraphs
                    (uid, message_id, sequence, content, thought_uid)
                VALUES (?, ?, ?, ?, ?)
                """,
                (uid, msg_id, seq, content, thought_uid),
            )

        # Auto-edge: responds_to (whole-message reply).
        if responds_to_msg_id is not None:
            # Target the responds_to at the responder's first paragraph
            # pointing at the parent message's first paragraph.
            first_uid = f"msg{msg_id}-p1"
            parent_first = c.execute(
                "SELECT uid FROM paragraphs WHERE message_id = ? AND sequence = 1",
                (responds_to_msg_id,),
            ).fetchone()
            if parent_first:
                _insert_edge(
                    c, "responds_to", first_uid, parent_first["uid"],
                    rationale=None, created_by=author,
                )

        # Auto-edge: supersedes (paragraph-level replacement).
        if supersedes_para_uid:
            first_uid = f"msg{msg_id}-p1"
            _insert_edge(
                c, "supersedes", first_uid, supersedes_para_uid,
                rationale=supersedes_rationale, created_by=author,
            )

        return msg_id


def _short_uuid() -> str:
    """Short UUID for thought_uid. Format: 't-' + 12 hex chars."""
    return f"t-{uuid.uuid4().hex[:12]}"


# ─── Edge writing ──────────────────────────────────────────────────────


def _insert_edge(conn, edge_type: str, from_para_uid: str, to_target: str,
                 rationale: Optional[str], created_by: str,
                 weight: float = 1.0) -> int:
    """Internal — insert an edge row. Helpers validate edge_type and
    rationale before calling this."""
    cur = conn.execute(
        """
        INSERT INTO edges
            (edge_type, from_para_uid, to_target, rationale, created_by, weight)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (edge_type, from_para_uid, to_target, rationale, created_by, weight),
    )
    return cur.lastrowid


def _require_rationale(edge_type: str, rationale: Optional[str]) -> None:
    if edge_type in RATIONALE_REQUIRED and not (rationale or "").strip():
        raise ValueError(
            f"edge_type {edge_type!r} requires non-empty rationale"
        )


def add_edge(edge_type: str, from_para_uid: str, to_target: str,
             created_by: str, rationale: Optional[str] = None,
             weight: float = 1.0,
             conn: Optional[sqlite3.Connection] = None) -> int:
    """Generic edge insertion with validation."""
    _require_rationale(edge_type, rationale)
    with _open_conn(conn) as c:
        return _insert_edge(c, edge_type, from_para_uid, to_target,
                            rationale, created_by, weight)


# Convenience wrappers per edge type. All accept (para_uid, created_by, ...).


def refines(from_para: str, to_para: str, created_by: str,
            conn: Optional[sqlite3.Connection] = None) -> int:
    return add_edge("refines", from_para, to_para, created_by, conn=conn)


def supports(from_para: str, to_para: str, created_by: str,
             conn: Optional[sqlite3.Connection] = None) -> int:
    return add_edge("supports", from_para, to_para, created_by, conn=conn)


def contradicts(from_para: str, to_para: str, created_by: str,
                rationale: str,
                conn: Optional[sqlite3.Connection] = None) -> int:
    """contradicts REQUIRES rationale."""
    return add_edge("contradicts", from_para, to_para, created_by,
                    rationale=rationale, conn=conn)


def supersede(from_para: str, to_para: str, created_by: str,
              rationale: str,
              conn: Optional[sqlite3.Connection] = None) -> int:
    """supersedes REQUIRES rationale.

    Note: when superseding via write_message(supersedes_para_uid=...),
    the helper auto-draws this edge AND inherits the thought_uid.
    Calling supersede() directly draws the edge without thought_uid
    inheritance — use the write_message path for new lineage.
    """
    return add_edge("supersedes", from_para, to_para, created_by,
                    rationale=rationale, conn=conn)


def references(from_para: str, to_para: str, created_by: str,
               conn: Optional[sqlite3.Connection] = None) -> int:
    return add_edge("references", from_para, to_para, created_by, conn=conn)


def derives_from(from_para: str, to_para: str, created_by: str,
                 conn: Optional[sqlite3.Connection] = None) -> int:
    return add_edge("derives_from", from_para, to_para, created_by, conn=conn)


def anchor(para_uid: str, doctrine_uri: str, agent: str,
           rationale: Optional[str] = None,
           conn: Optional[sqlite3.Connection] = None) -> int:
    """Anchor a paragraph to a doctrinal source. Rationale optional but
    useful when the connection isn't obvious."""
    return add_edge("anchors_to", para_uid, doctrine_uri, agent,
                    rationale=rationale, conn=conn)


def cite_artifact(para_uid: str, artifact_uri: str, agent: str,
                  conn: Optional[sqlite3.Connection] = None) -> int:
    """Cite an external artifact (commit, file, plan entry)."""
    return add_edge("cites_artifact", para_uid, artifact_uri, agent, conn=conn)


def endorse(para_uid: str, agent: str,
            conn: Optional[sqlite3.Connection] = None) -> int:
    """Explicit endorsement — stronger signal than just reading."""
    return add_edge("endorsed_by", para_uid, para_uid, agent, conn=conn)


def pin(para_uid: str, agent: str, rationale: Optional[str] = None,
        conn: Optional[sqlite3.Connection] = None) -> int:
    """Pin a paragraph as durable (exempts from deprecation collapse)."""
    return add_edge("pinned_by", para_uid, para_uid, agent,
                    rationale=rationale, conn=conn)


def vote_deprecate(para_uid: str, agent: str,
                   conn: Optional[sqlite3.Connection] = None) -> int:
    """Vote to retire a paragraph. Deprecation activates when:
    (a) all readers of the parent message have voted AND
    (b) no non-deprecation edge has been drawn since the most-recent vote.
    """
    return add_edge("deprecation_voted", para_uid, para_uid, agent, conn=conn)


# ─── Reading ───────────────────────────────────────────────────────────


def read_inbox(participant: str, include_active_threads: bool = True,
               conn: Optional[sqlite3.Connection] = None) -> list[InboxEntry]:
    """Return today's messages + active-thread carryforward for participant.

    Excludes messages the participant has already read AND that aren't on
    an active thread (they're already-read AND already-stale).
    """
    with _open_conn(conn) as c:
        # Daily scope: messages from current local day, plus active-thread
        # messages from any day. The caller decides which to mark_read.
        rows = c.execute(
            """
            SELECT m.*
            FROM messages m
            WHERE m.state = 'sent'
              AND (
                  date(m.created_at) = date('now')
                  OR (m.thread_active = 1)
              )
              AND (
                  m.recipients = 'all'
                  OR m.recipients LIKE ?
              )
            ORDER BY m.created_at
            """,
            (f'%"{participant}"%',),
        ).fetchall()

        result = []
        for row in rows:
            paras = c.execute(
                """
                SELECT uid, message_id, sequence, content, thought_uid, created_at
                FROM paragraphs
                WHERE message_id = ?
                ORDER BY sequence
                """,
                (row["id"],),
            ).fetchall()
            result.append(InboxEntry(
                message=_row_to_message(row),
                paragraphs=[_row_to_paragraph(p) for p in paras],
            ))
        return result


def mark_read(message_id: int, participant: str,
              conn: Optional[sqlite3.Connection] = None) -> None:
    """Record that participant has read this message. Required for the
    unanimity-of-readers deprecation computation."""
    with _open_conn(conn) as c:
        c.execute(
            "INSERT INTO read_log (message_id, participant) VALUES (?, ?)",
            (message_id, participant),
        )


def thought_lineage(thought_uid: str,
                    conn: Optional[sqlite3.Connection] = None) -> list[Paragraph]:
    """Return all paragraphs in a thought's lineage, ordered chronologically.

    The PrizmForge-inspired query: see all expressions of an idea over time
    as a single index lookup, regardless of which messages they appear in.
    """
    with _open_conn(conn) as c:
        rows = c.execute(
            """
            SELECT uid, message_id, sequence, content, thought_uid, created_at
            FROM paragraphs
            WHERE thought_uid = ?
            ORDER BY created_at ASC
            """,
            (thought_uid,),
        ).fetchall()
        return [_row_to_paragraph(r) for r in rows]


def get_paragraph_status(para_uid: str,
                         conn: Optional[sqlite3.Connection] = None) -> str:
    """Read the status from paragraphs_active view."""
    with _open_conn(conn) as c:
        row = c.execute(
            "SELECT status FROM paragraphs_active WHERE para_uid = ?",
            (para_uid,),
        ).fetchone()
        return row["status"] if row else "unknown"


# ─── Row conversion helpers ────────────────────────────────────────────


def _row_to_message(row: sqlite3.Row) -> Message:
    return Message(
        id=row["id"],
        thread_id=row["thread_id"],
        thread_active=bool(row["thread_active"]),
        author=row["author"],
        recipients=row["recipients"],
        subject=row["subject"],
        body=row["body"],
        state=row["state"],
        superseded_by=row["superseded_by"],
        rollback_reason=row["rollback_reason"],
        created_at=row["created_at"],
    )


def _row_to_paragraph(row: sqlite3.Row) -> Paragraph:
    return Paragraph(
        uid=row["uid"],
        message_id=row["message_id"],
        sequence=row["sequence"],
        content=row["content"],
        thought_uid=row["thought_uid"],
        created_at=row["created_at"],
    )


# ─── Notes ─────────────────────────────────────────────────────────────
#
# DIFFERENCES FROM MULTIAGENT's multiagent.py:
#
# 1. Thought-UID lineage (new). write_message accepts a
#    supersedes_para_uid+supersedes_rationale pair; when provided, the
#    new paragraphs inherit the superseded paragraph's thought_uid.
#    thought_lineage() exposes the lineage query.
#
# 2. Schema-level rationale enforcement (improvement). The CHECK
#    constraint on edges rejects empty rationale for contradicts/
#    supersedes at the DB layer; the helpers also validate early with
#    a clearer error.
#
# 3. Type hints + dataclass returns (kit idiom). MultiAgent's helpers
#    return raw dicts; this version returns Message / Paragraph /
#    Edge / InboxEntry dataclasses for static analysis.
#
# 4. Engagement-floor in paragraphs_active (replaces 7-day calendar
#    floor). The view computation is in the schema; helpers consume
#    it via get_paragraph_status.
#
# WHAT'S DELIBERATELY OUT OF SCOPE:
#
# 1. Per-paragraph read receipts. MultiAgent tracks reads at message
#    granularity. Per-paragraph would let finer-grained engagement-floor
#    logic but adds significant write volume. Acceptable for now.
#
# 2. Cross-corpus federation. This subsystem handles a single corpus
#    instance. Federation across multiple corpora is future work.
#
# 3. Privacy / access control. All paragraphs visible to all participants
#    by default. Projects with privacy needs can add visibility columns
#    or scope-aware read helpers.
#
# 4. Automatic AI judgment for thought-UID assignment. The thought-UID
#    is inherited only via explicit supersedes edges. AI deciding
#    "these two paragraphs express the same thought" would be hypothesis
#    per E1 and would need an AI-dependency note.
