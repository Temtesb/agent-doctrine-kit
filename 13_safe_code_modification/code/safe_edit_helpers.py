"""Safe edit helpers — line-GUID assignment, content-hash concurrency, post-write invalidation.

Derives from Foundation F1 (the file's state across time is a temporal
fact recorded in the schema) and F2 (the GUID is single-source-of-truth
for line identity; the proposal's draft-time assumptions must still hold
at apply time).

Ingested from PrizmForge — see
../../12_ingestion_protocol/examples/prizmforge_ingestion.md.

Provides:
  - assign_line_guids(file_path, conn) — first-time tracking init
  - compute_file_hash(file_path) — full-file SHA-256
  - capture_file_snapshot(file_path, conn, captured_by, proposal_id)
  - verify_proposal_applicable(file_path, proposal_hash, conn)
  - apply_edit_with_concurrency_check(file_path, proposal, conn)
  - invalidate_overlapping_proposals(file_path, applied_guids, conn)

Adapt to your project:
  1. The proposal-row schema is assumed to have target_file_path,
     targeted_guids, drafted_against_hash, state, invalidation_reason.
     If your project's schema differs, adapt the column names in
     verify_proposal_applicable and invalidate_overlapping_proposals.
  2. The notify-author hook in invalidate_overlapping_proposals is a
     no-op by default; wire to your project's notification path.
  3. The GUID-assignment algorithm is SHA-1(content + offset); change
     it ONLY by bumping algorithm_version on the tracking table and
     keeping the old algorithm available for existing GUIDs.
"""

from __future__ import annotations

import hashlib
import sqlite3
import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import Optional


# ─── Constants ──────────────────────────────────────────────────────────

# Current algorithm version. Bump when changing GUID-assignment logic;
# the old algorithm must still be available for existing GUIDs.
GUID_ALGORITHM_VERSION = 1


# ─── Data shapes ────────────────────────────────────────────────────────


@dataclass
class LineTrackingRow:
    """One row from line_guid_tracking."""
    file_path: str
    line_guid: str
    current_line_number: int
    content_hash: str
    content: str
    original_content_hash: str
    original_line_number: int
    tracking_started_at: str
    algorithm_version: int
    deleted_at: Optional[str]
    deleted_reason: Optional[str]
    last_apply_at: str
    last_apply_proposal_id: Optional[str]


@dataclass
class ProposalApplicabilityResult:
    """Result of verifying a proposal can be applied."""
    applicable: bool
    reason: str                              # 'ok' | 'file_hash_mismatch' | 'guid_missing' | etc.
    expected_hash: Optional[str] = None
    actual_hash: Optional[str] = None
    missing_guids: Optional[list[str]] = None


# ─── GUID assignment ────────────────────────────────────────────────────


def _compute_line_guid(content: str, offset: int, algorithm_version: int = GUID_ALGORITHM_VERSION) -> str:
    """Deterministic GUID for a line.

    Algorithm v1: SHA-1 of (content + ':' + str(offset)) prefixed with
    the algorithm version. Deterministic so the same file content
    produces the same GUIDs on re-init.

    The offset distinguishes duplicate lines (e.g., blank lines, repeated
    boilerplate) that would otherwise collide.
    """
    if algorithm_version == 1:
        seed = f"{content}:{offset}".encode("utf-8")
        digest = hashlib.sha1(seed).hexdigest()
        return f"v1-{digest[:16]}"
    else:
        raise ValueError(f"Unsupported algorithm_version: {algorithm_version}")


def assign_line_guids(file_path: str, conn: sqlite3.Connection) -> int:
    """One-time initialization: assign GUIDs to every line in file.

    Idempotent — re-running on an already-tracked file is a no-op.
    Returns the number of newly-tracked lines.

    Raises FileNotFoundError if the file doesn't exist.
    """
    existing_count = conn.execute(
        "SELECT COUNT(*) FROM line_guid_tracking WHERE file_path = ?",
        (file_path,),
    ).fetchone()[0]
    if existing_count > 0:
        return 0  # already tracked

    text = Path(file_path).read_text()
    lines = text.splitlines(keepends=False)

    rows = []
    for line_number, content in enumerate(lines, start=1):
        guid = _compute_line_guid(content, line_number)
        content_hash = hashlib.sha256(content.encode("utf-8")).hexdigest()
        rows.append((
            file_path, guid, line_number, content_hash, content,
            content_hash, line_number, GUID_ALGORITHM_VERSION,
            None,  # last_apply_proposal_id
        ))

    conn.executemany(
        """
        INSERT INTO line_guid_tracking
            (file_path, line_guid, current_line_number, content_hash, content,
             original_content_hash, original_line_number, algorithm_version,
             last_apply_proposal_id)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        rows,
    )
    return len(rows)


# ─── Snapshot capture ───────────────────────────────────────────────────


def compute_file_hash(file_path: str) -> str:
    """Full-file SHA-256."""
    return hashlib.sha256(Path(file_path).read_bytes()).hexdigest()


def capture_file_snapshot(
    file_path: str,
    conn: sqlite3.Connection,
    captured_by: str,
    triggering_proposal_id: Optional[str] = None,
) -> int:
    """Record the file's current state in file_state_snapshots.

    captured_by: 'proposal_draft' | 'edit_apply' | 'manual_resync'
    triggering_proposal_id: optional reference to the proposal that
        triggered this capture.

    Returns the snapshot row id.
    """
    full_hash = compute_file_hash(file_path)
    cur = conn.execute(
        """
        INSERT INTO file_state_snapshots
            (file_path, full_content_hash, captured_by, triggering_proposal_id)
        VALUES (?, ?, ?, ?)
        """,
        (file_path, full_hash, captured_by, triggering_proposal_id),
    )
    return cur.lastrowid


# ─── Applicability check ───────────────────────────────────────────────


def verify_proposal_applicable(
    file_path: str,
    proposal_drafted_against_hash: str,
    proposal_targeted_guids: list[str],
    conn: sqlite3.Connection,
) -> ProposalApplicabilityResult:
    """Check whether a proposal can be applied to the file's current state.

    Two checks:
      1. File-level: does the file's current hash match what the
         proposal was drafted against? If not, the file has moved.
      2. GUID-level: do all the proposal's targeted GUIDs still exist
         in the tracking table (not deleted)? If not, target lines
         have been removed by intervening work.

    Returns a ProposalApplicabilityResult. If applicable=True, the
    proposal can safely apply. If False, the reason field explains
    what's wrong.
    """
    current_hash = compute_file_hash(file_path)
    if current_hash != proposal_drafted_against_hash:
        return ProposalApplicabilityResult(
            applicable=False,
            reason="file_hash_mismatch",
            expected_hash=proposal_drafted_against_hash,
            actual_hash=current_hash,
        )

    if proposal_targeted_guids:
        placeholders = ",".join("?" * len(proposal_targeted_guids))
        rows = conn.execute(
            f"""
            SELECT line_guid FROM line_guid_tracking
            WHERE file_path = ?
              AND line_guid IN ({placeholders})
              AND deleted_at IS NULL
            """,
            [file_path] + proposal_targeted_guids,
        ).fetchall()
        found_guids = {r[0] for r in rows}
        missing = [g for g in proposal_targeted_guids if g not in found_guids]
        if missing:
            return ProposalApplicabilityResult(
                applicable=False,
                reason="guid_missing",
                missing_guids=missing,
            )

    return ProposalApplicabilityResult(applicable=True, reason="ok")


# ─── Post-write invalidation ───────────────────────────────────────────


def invalidate_overlapping_proposals(
    file_path: str,
    applied_proposal_id: str,
    applied_guids: list[str],
    conn: sqlite3.Connection,
    notify_author=None,                       # callable(proposal_id, reason) -> None
) -> list[str]:
    """After an edit lands, mark open proposals targeting overlapping
    GUIDs as invalidated.

    Assumes a `proposals` table with columns:
      - id (TEXT)
      - target_file_path (TEXT)
      - targeted_guids (TEXT, JSON-encoded list)
      - state (TEXT)
      - invalidation_reason (TEXT)
      - author (TEXT)
    Adapt the SQL below if your project's schema differs.

    Returns the list of invalidated proposal IDs.
    """
    import json

    open_props = conn.execute(
        """
        SELECT id, targeted_guids, author
        FROM proposals
        WHERE target_file_path = ? AND state = 'open'
        """,
        (file_path,),
    ).fetchall()

    invalidated = []
    for prop_id, targeted_guids_json, author in open_props:
        if prop_id == applied_proposal_id:
            continue  # don't invalidate self
        targeted = set(json.loads(targeted_guids_json))
        if targeted & set(applied_guids):
            reason = (
                f"invalidated by apply of proposal {applied_proposal_id}; "
                f"overlapping GUIDs: {sorted(targeted & set(applied_guids))}"
            )
            conn.execute(
                """
                UPDATE proposals
                SET state = 'invalidated',
                    invalidation_reason = ?
                WHERE id = ?
                """,
                (reason, prop_id),
            )
            invalidated.append(prop_id)
            if notify_author:
                notify_author(prop_id, reason)

    return invalidated


# ─── High-level apply orchestration ────────────────────────────────────


def apply_edit_with_concurrency_check(
    file_path: str,
    proposal_id: str,
    proposal_drafted_against_hash: str,
    proposal_targeted_guids: list[str],
    new_content: str,
    conn: sqlite3.Connection,
    notify_invalidation_author=None,
) -> dict:
    """Orchestrate the full apply pipeline.

    Returns:
      {
        'status': 'applied' | 'conflicted',
        'reason': '...',
        'invalidated_proposals': [list of proposal IDs that were invalidated]
      }
    """
    check = verify_proposal_applicable(
        file_path,
        proposal_drafted_against_hash,
        proposal_targeted_guids,
        conn,
    )
    if not check.applicable:
        return {
            "status": "conflicted",
            "reason": check.reason,
            "expected_hash": check.expected_hash,
            "actual_hash": check.actual_hash,
            "missing_guids": check.missing_guids,
            "invalidated_proposals": [],
        }

    # Write the new content
    Path(file_path).write_text(new_content)

    # Capture the post-apply snapshot
    capture_file_snapshot(file_path, conn, "edit_apply", proposal_id)

    # Invalidate overlapping proposals
    invalidated = invalidate_overlapping_proposals(
        file_path,
        proposal_id,
        proposal_targeted_guids,
        conn,
        notify_invalidation_author,
    )

    # Note: this helper doesn't re-populate the GUID table from the new
    # content. That requires a diff against the old content to identify
    # inserted/deleted/modified lines; see PrizmForge's full
    # implementation for the diff logic. The simpler version: track only
    # files where edits modify existing GUIDs (no insertion/deletion);
    # the richer version handles all cases.

    return {
        "status": "applied",
        "reason": "ok",
        "invalidated_proposals": invalidated,
    }


# ─── Notes ──────────────────────────────────────────────────────────────
#
# WHAT'S DELIBERATELY OUT OF SCOPE
#
# 1. Diff-based GUID-table updates on apply. When an edit inserts or
#    deletes lines (not just modifies existing ones), the GUID table
#    needs new rows for inserted lines and deleted_at writes for removed
#    lines. This requires a proper text diff against the prior content.
#    PrizmForge implements this fully; the adapted version here covers
#    the simpler modify-existing-lines case and leaves the diff path as
#    a follow-on implementation.
#
# 2. Semantic merge. Two non-overlapping edits to the same file can both
#    apply via this pipeline; whether the combination produces a working
#    program is downstream of edit safety. Tests in CI are the
#    structural mitigation.
#
# 3. Binary files and non-line-structured formats. assign_line_guids
#    assumes splitlines() produces meaningful units. For binary blobs
#    or whitespace-significant formats, additional considerations apply.
#
# WHAT'S OPTIONAL
#
# 1. Post-write invalidation. The apply-time concurrency check catches
#    conflicts at the moment of application; post-write invalidation
#    surfaces them earlier (when the conflicting edit lands) so other
#    proposals' authors react before re-spending cycles on now-stale
#    proposals. Useful in higher-throughput systems; optional in
#    single-author or low-throughput contexts.
#
# 2. Notification hook (notify_author). When a proposal is invalidated,
#    its author may want to know immediately. Wire this to your
#    project's notification path (a queue, an email, a MultiAgent
#    message, etc.) — or leave it as a no-op if synchronous notification
#    isn't needed.
