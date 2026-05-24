"""Stub generator — interface signature.

Implements the loop closure described in ../doctrine/loop_closure.md.
For each accepted lesson_candidate that doesn't yet have generated
artifacts, produces a draft invariant test file and a PATTERNS.md entry.

This file is the INTERFACE — the function signatures and the structural
contract. The actual generation logic (AI-drafted detection, template
expansion, file writing) is implementation-specific and depends on your
project's pattern library format, test framework, and AI client.

Implement the three functions below:
  - find_accepted_pending_candidates
  - generate_artifacts_for_candidate
  - run_generator (orchestrator)

Idempotent by construction: each candidate's invariant_test_path field
is set after generation, so a re-run skips already-generated candidates.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Optional


@dataclass
class LessonCandidate:
    """A candidate row from the lesson_candidates table.

    Mirrors the schema in ../schema/lesson_candidates.sql.
    """
    id: int
    detected_at: str
    governing_principle: str
    distinct_check_count: int
    distinct_check_ids: list[str]  # parsed from the TEXT JSON
    total_violation_count: int
    window_days: int
    suggested_invariant: Optional[str]
    suggested_doctrine_update: Optional[str]
    status: str
    decided_at: Optional[str]
    decided_by: Optional[str]
    decision_notes: Optional[str]
    invariant_test_path: Optional[str]
    invariant_test_generated_at: Optional[str]
    pattern_library_entry: Optional[str]


@dataclass
class GeneratedArtifacts:
    """The artifacts produced for one candidate."""
    test_file_path: Path           # The draft invariant test file
    pattern_anchor: str            # The P00N anchor in PATTERNS.md
    pattern_entry_text: str        # The full text appended to PATTERNS.md


# ─── Interface functions to implement ────────────────────────────────────


def find_accepted_pending_candidates(conn) -> list[LessonCandidate]:
    """Return accepted candidates that don't yet have generated artifacts.

    SQL shape:
        SELECT * FROM lesson_candidates
        WHERE status = 'accepted'
          AND invariant_test_generated_at IS NULL
        ORDER BY decided_at ASC

    The idx_lc_accepted_pending_stub partial index makes this O(N) in
    the count of pending candidates, not the total table size.
    """
    raise NotImplementedError("Adapt to your DB layer.")


def generate_artifacts_for_candidate(
    candidate: LessonCandidate,
    test_dir: Path,
    patterns_md_path: Path,
) -> GeneratedArtifacts:
    """Generate the draft invariant test + PATTERNS.md entry for one candidate.

    The test file's content is derived from:
      - The ratchet template at
        ../../04_pre_flight_and_invariants/enforcer/_known_allowed_ratchet_template.py
      - The candidate's `suggested_invariant` text (seed for the docstring
        and an AI-drafted detection-logic sketch)
      - The candidate's `governing_principle` (used in the test class
        name and the failure message)

    The PATTERNS.md entry follows the project's pattern library format
    (see ../../06_patterns_and_dissonance/templates/patterns_md_entry_template.md).
    Required fields:
      - Stable P00N anchor (next available number; never reuse)
      - Governing principle (from the candidate)
      - Bug shape (derived from the distinct check IDs and a sample of
        violations; AI-drafted)
      - Fix shape (from suggested_invariant; AI-drafted)
      - Invariant test path (the path returned by this function)
      - First seen (the candidate's detected_at date)
      - Source (the candidate's ID as `lesson_candidate #N`)

    Both artifacts are DRAFTS — the user reviews and refines before
    committing. The generator's job is to take the candidate from
    "pending stub generation" to "user has something concrete to react
    to" — not to produce production-ready artifacts unsupervised.

    Returns the GeneratedArtifacts with the file path and the pattern
    entry text. The caller writes both to disk and updates the
    candidate's invariant_test_path + pattern_library_entry fields
    in the same transaction.
    """
    raise NotImplementedError("Adapt to your pattern library + test framework.")


def run_generator(
    conn,
    test_dir: Path,
    patterns_md_path: Path,
    dry_run: bool = False,
) -> list[tuple[LessonCandidate, GeneratedArtifacts]]:
    """Orchestrate the generation pass.

    Args:
      conn: database connection
      test_dir: directory where generated invariant tests land
      patterns_md_path: path to the project's PATTERNS.md
      dry_run: if True, generate artifacts but don't write files or
        update candidates. Useful for previewing what the generator
        would produce.

    For each candidate returned by find_accepted_pending_candidates:
      1. Generate artifacts.
      2. If not dry_run:
         a. Write the test file to disk.
         b. Append the pattern entry to PATTERNS.md.
         c. Update the candidate's invariant_test_path,
            invariant_test_generated_at, and pattern_library_entry
            fields in a single transaction.
      3. Append (candidate, artifacts) to the result list.

    Returns the list of (candidate, artifacts) for inspection by the
    caller. The CLI typically prints a one-line summary per candidate.

    Failure handling: if one candidate's artifact generation raises,
    log the error and continue to the next candidate. One bad
    suggestion shouldn't block the rest of the pass. The candidate
    stays in 'accepted' state with NULL artifact fields; the next run
    retries.
    """
    raise NotImplementedError("Wire to your DB connection and AI drafter.")


# ─── CLI sketch ──────────────────────────────────────────────────────────
#
# if __name__ == "__main__":
#     import argparse
#     parser = argparse.ArgumentParser()
#     parser.add_argument("--dry-run", action="store_true")
#     parser.add_argument("--test-dir", default="tests/")
#     parser.add_argument("--patterns-md", default="PATTERNS.md")
#     args = parser.parse_args()
#
#     with get_db() as conn:
#         results = run_generator(
#             conn,
#             test_dir=Path(args.test_dir),
#             patterns_md_path=Path(args.patterns_md),
#             dry_run=args.dry_run,
#         )
#     for candidate, artifacts in results:
#         action = "would generate" if args.dry_run else "generated"
#         print(f"{action} for candidate #{candidate.id}: "
#               f"{artifacts.pattern_anchor} → {artifacts.test_file_path}")


# ─── Notes on AI integration ─────────────────────────────────────────────
#
# The generator's AI calls are AI-dependent rules per
# ../../11_ai_dependency_tracking/. Specifically:
#
# 1. The suggested-invariant text → detection-logic conversion. The AI
#    reads the suggested_invariant prose and proposes the regex / AST
#    patterns the detection function should match. Model-dependent —
#    different models will produce different patterns for the same
#    suggestion text.
#
# 2. The bug-shape text → PATTERNS.md entry conversion. The AI
#    summarizes the violations into the "Bug shape" paragraph. Also
#    model-dependent.
#
# Document the AI dependency on the generator with a dependency note
# (per 11_ai_dependency_tracking templates). Validate that the
# generator's outputs still meet quality bars after model upgrades.
#
# The user's review of generated drafts is the verification surface
# per E1; AI failures here are caught by the user before commit, not
# silently shipped.
