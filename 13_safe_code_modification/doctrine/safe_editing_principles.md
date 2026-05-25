# Doctrine excerpt — safe code modification principles

Place this in your governance doc as the section governing how agents apply code edits.

---

## Line identity is stable; line position is volatile

**Derives from:** Foundation [F2](../../01_foundations/F2_logic_holds.md) (single source of truth — a line's identity is the fact; the line's position is a property of the file's current state; conflating them means two readers can have different "true" answers about which line is which).

A line's *identity* — what semantic content it represents in the codebase — should not depend on its position in the file. Surrounding insertions, deletions, or moves shift every other line's position; if the system reasons about lines by position, every shift invalidates pending work.

The structural answer: assign each tracked line a stable GUID at first-tracking time. The GUID is the canonical identifier; the line's position is a derived property looked up from the GUID table. Edits reference GUIDs; the system computes the actual line numbers at apply time.

This is F2 applied at the line-of-code grain. The same non-contradiction principle that prevents two columns from storing the same fact prevents two coordinates from claiming to identify the same line.

## Optimistic concurrency over locking

**Derives from:** Foundation [F1](../../01_foundations/F1_time_has_direction.md) (the file's state at proposal-draft time and apply time are two distinct temporal facts) and [F2](../../01_foundations/F2_logic_holds.md) (the proposal's assumptions about file state must still hold at apply time or the assumption is non-contradictory with reality).

When a proposal is drafted against a file, the file's content at that moment is captured as a content hash. When the proposal is applied, the current file's hash is compared. If they match, apply succeeds; if they differ, the file moved between draft and apply, and the proposal is rejected as `conflicted`.

This trades locking (serializing access to the file) for detection (allowing concurrent draft, catching divergence at apply time). The trade favors throughput: most proposals don't actually conflict with concurrent work; locking pessimistically would gate everything. Optimistic concurrency lets non-conflicting work proceed while still preventing silent overwrite.

When a proposal is rejected as conflicted: surface the rejection with the proposal's original hash and the file's current hash so the agent (or user) can decide whether to re-draft, abandon, or attempt a manual merge.

## Decision triggers — fire at edit-draft and edit-apply

**Edit-draft trigger:** before any agent drafts an edit to a tracked file, record (a) the file's current full-content hash AND (b) the GUIDs the edit will target. Both go in `file_state_snapshots` and the proposal record. The agent now has a snapshot of "what I assumed the file looked like."

**Edit-apply trigger:** before any agent applies an edit, re-read the file, compute its current hash, and compare against the proposal's recorded "drafted-against" hash. Mismatch → reject as conflicted; do not apply. Match → apply, update the GUID table with new content hashes + any new lines' GUIDs, capture a new snapshot for downstream proposals.

The two triggers are paired. A proposal drafted without the draft-trigger has nothing to compare against; a proposal applied without the apply-trigger may silently overwrite concurrent work. Both fire structurally in the kit's edit toolchain; the principle exists to explain *why* the toolchain enforces this rather than to enforce the rule on its own.

## Post-write invalidation — proactive complement to apply-time check

When a file's content changes (any apply lands), scan open proposals targeting overlapping GUIDs. Mark those proposals invalidated and surface the invalidation to their authors.

This is a proactive complement to the apply-time check. The apply-time check catches the conflict at the moment of attempted application; post-write invalidation surfaces the conflict the moment the conflicting change lands, so the conflicting proposal's author or reviewer can react before spending cycles on a now-stale proposal.

Implementation: post-apply, query for open proposals where `(target_file_path, any_targeted_line_guid)` intersects the current apply's affected GUIDs. For each match, mark the proposal `state='invalidated'`, record the conflicting apply's commit/proposal SHA in the invalidation reason, and notify the proposal's author.

The invalidation is itself an audit event per [02_audit_as_shape/](../../02_audit_as_shape/) — the state transition writes a row, never silently overwrites.

## What this doctrine does NOT cover

- **Semantic merge.** Two non-overlapping edits to different parts of the same file can both succeed individually; whether the combination produces a coherent program is a domain-level question (does the function still type-check; does the test still pass; does the API contract still hold). Downstream tests are the structural mitigation; this doctrine ensures both edits land cleanly without overwriting each other, but doesn't reason about their combined effect.

- **Binary files and non-line-structured formats.** Line-GUIDs are line-granular. Binary blobs, whitespace-significant formats (Python is line-significant but doesn't quite work the same way), and other non-line-structured content don't get GUIDs naturally. The doctrine matches PrizmForge's scope on this; extending to other file shapes is a future ingestion question.

- **Automatic conflict resolution.** Rejected-as-conflicted proposals surface to the agent or user for re-drafting; the kit does not attempt automatic merge. This is conservative per the [hypothesis posture](../../00_meta_stances/hypothesis_posture.md) — automatic conflict resolution requires confidence the kit hasn't earned. A project that wants automatic conflict resolution can add it as a stack-shape addition; the structural baseline is conservative rejection.

## Cross-references

- [../README.md](../README.md) — the subsystem overview.
- [../schema/line_guid_tracking.sql](../schema/line_guid_tracking.sql) — the DDL for tracking line-GUIDs and file-state snapshots.
- [../code/safe_edit_helpers.py](../code/safe_edit_helpers.py) — the working helpers implementing these triggers.
- [../../02_audit_as_shape/](../../02_audit_as_shape/) — the audit-as-shape sibling for row-grain mutation safety. This subsystem and that one together cover both granularities.
- [../../12_ingestion_protocol/examples/prizmforge_ingestion.md](../../12_ingestion_protocol/examples/prizmforge_ingestion.md) — the full ingestion record covering this subsystem's origin.
