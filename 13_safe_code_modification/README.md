# 13 — Safe code modification

## The concept

> Three coupled primitives for applying code edits safely under concurrent modification. **Line-GUID editing** gives each line a stable identifier so edits don't rely on volatile line numbers. **Content-hash optimistic concurrency** verifies a file hasn't changed since a proposal was drafted, rejecting stale proposals at apply time rather than corrupting state. **Post-write invalidation** proactively flags proposals whose target lines have shifted, so consumers see staleness before attempting application.

**Derives from:** Foundations [F1](../01_foundations/F1_time_has_direction.md) (the file's state at proposal-draft time and apply time are two distinct temporal facts; the system must be able to query the difference) and [F2](../01_foundations/F2_logic_holds.md) (the line-GUID is single-source-of-truth for line identity, distinct from the line's volatile position; the proposal's assumptions about file state must still hold at apply time or the assumption is non-contradictory with reality).

**Ingested from PrizmForge** (https://github.com/seakintruth/PrizmForge) — see [12_ingestion_protocol/examples/prizmforge_ingestion.md](../12_ingestion_protocol/examples/prizmforge_ingestion.md) for the full ingestion record. The primitives originated there; this subsystem adapts them into the kit's idiom with proper foundation-anchoring and ratchet-pattern enforcers.

## Why this matters for agent-governed systems

Agent-modified codebases hit two failure modes that single-author codebases rarely encounter at the same intensity:

**Failure mode 1 — line-number drift.** An agent drafts an edit targeting "lines 50-55 of foo.py." Between draft time and apply time, an earlier edit inserts 10 lines above. The edit now applies to the wrong place — silently corrupting code that looked fine in the proposal review. Single-author workflows tend to draft-and-apply quickly; agent workflows often have longer gaps where the file state diverges.

**Failure mode 2 — concurrent overwrite.** Two agents draft edits to the same file. Both pass review. The second to apply overwrites the first's work silently. No conflict surfaces because both edits looked locally correct against the file state they each read.

Single-author git workflows mitigate these through tight feedback loops and explicit merge conflicts. Agent workflows benefit from structural mitigation built into the edit pipeline.

The three primitives in this subsystem address both failure modes:

- **Line-GUIDs** prevent line-number drift by giving each line a stable identity that survives surrounding insertions/deletions.
- **Content-hash optimistic concurrency** catches concurrent overwrites by verifying the file hasn't shifted since the proposal was drafted.
- **Post-write invalidation** proactively flags proposals whose target lines have moved, surfacing staleness before the user (or another agent) tries to apply them.

## What's in this directory

| File | Purpose |
|---|---|
| [schema/line_guid_tracking.sql](schema/line_guid_tracking.sql) | The DDL for tracking line-GUIDs and their current positions + content hashes per file. |
| [doctrine/safe_editing_principles.md](doctrine/safe_editing_principles.md) | The principles around line identity stability, optimistic concurrency, and proposal invalidation; with the decision-trigger questions that fire at edit-draft and edit-apply time. |
| [code/safe_edit_helpers.py](code/safe_edit_helpers.py) | Working Python implementations of the three primitives: GUID assignment on file-tracking-init, content-hash comparison at apply time, post-write invalidation of overlapping proposals. |

## How to adopt

1. **Copy the schema** into your migrations directory. The `line_guid_tracking` table is independent of your project's domain schema; it sits alongside as edit-pipeline infrastructure.

2. **Copy the doctrine** into your governance doc. Place it under the section governing how agents apply code edits. The decision-trigger questions fire at two points: when drafting an edit (record the file's content hash + the line-GUIDs targeted) and when applying an edit (verify both still match before writing).

3. **Copy the helpers** into your edit toolchain. Adapt the file-tracking initialization to your project's structure; the GUID-assignment algorithm is deterministic (SHA-1 of original line content + offset, seeded with a tracking-table version field) so existing files can be one-time backfilled.

4. **Wire the optimistic concurrency check into every edit path.** This is the load-bearing integration step. Every code path that applies an edit must:
   - Read the current file state + GUID table row
   - Compare against the hash the proposal was drafted against
   - Reject as `conflicted` on mismatch; apply otherwise
   - Update the GUID table row with the new content hash + any new line GUIDs (for inserted lines)

5. **Optional — wire post-write invalidation.** When a file's GUID table row changes, scan open proposals targeting overlapping GUIDs and mark them invalidated. This is a proactive complement to the apply-time check; it lets reviewers see staleness before they spend cycles reviewing a now-conflicted proposal.

## Tensions to name explicitly

1. **Line-GUID assignment is deterministic but the algorithm is versioned.** If a project changes the GUID-assignment algorithm later, existing GUIDs need to remain valid. The schema includes a version field on the tracking table per F1 — schema evolution is itself a fact subject to F1.

2. **The primitives assume line-structured text files.** Binary files, whitespace-significant formats, and binary blobs in text files don't get line-GUIDs naturally. The kit's adaptation matches PrizmForge's scope on this; extending to other file shapes is future work.

3. **Conflict resolution is reject-as-conflicted.** No automatic merge attempt. This is conservative per the [hypothesis posture](../00_meta_stances/hypothesis_posture.md) — automatic conflict resolution requires confidence the kit hasn't earned. Rejected proposals surface to the user (or to the proposing agent) for re-drafting against current state.

4. **The primitives don't address semantic merge.** Two non-overlapping edits to different parts of the same file can both succeed individually; whether the combination produces a coherent result is a domain-level question the primitives don't reason about. Out-of-scope here; downstream tests are the structural mitigation.

5. **AI-dependency status.** Line-GUID assignment is deterministic (no AI dependency). Content-hash concurrency is deterministic. Post-write invalidation is deterministic. None of these primitives have AI-behavior dependencies, so they're free to land at the stack layer without [11_ai_dependency_tracking/](../11_ai_dependency_tracking/) notes. The AI dependency would enter only if a project adds a "semantic-merge attempt" feature on top of conflict-detection.

## Cross-references

- [12_ingestion_protocol/examples/prizmforge_ingestion.md](../12_ingestion_protocol/examples/prizmforge_ingestion.md) — the full ingestion record covering this subsystem's origin in PrizmForge.
- [02_audit_as_shape/](../02_audit_as_shape/) — the row-grain audit complement. This subsystem provides line-grain edit safety; the audit-as-shape subsystem provides row-grain mutation safety. Together they cover both granularities.
- [03_classifier_and_audit_lane/](../03_classifier_and_audit_lane/) — per-edit gating is a finer-grained sibling to per-finding classification. A project that wants both could route edits through the classifier (is this a mechanical edit doctrine names, or a judgment-requiring edit?) and use this subsystem's primitives for the apply-time safety.
- [01_foundations/F1_time_has_direction.md](../01_foundations/F1_time_has_direction.md) and [F2_logic_holds.md](../01_foundations/F2_logic_holds.md) — the foundations this subsystem implements.
