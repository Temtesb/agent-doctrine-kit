"""Architecture invariant test — UPDATE on meaningful business column requires audit row.

Derives from Foundation F1 (time has direction) applied to data mutation.
Mechanically enforces the decision-trigger principle: any function that
runs an UPDATE on a column in MEANINGFUL_BUSINESS_COLUMNS must also
write to one of the recognized AUDIT_TABLES in the same function body.

Pattern: the `_KNOWN_ALLOWED` ratchet.
- Baseline current state by running the test and adding existing
  violations to the allow-list with inline justification.
- New code that violates the invariant fails CI immediately.
- Removing entries (fixing violations) ratchets the baseline down.

Categories used in justifications:
- LEGITIMATE — the row itself or a sibling write IS the audit; fixing
  this would be wrong (e.g., status-transition writes where the column
  write itself is the lifecycle event).
- DEFERRED — real violation, tracked as ratchet-down work. Allow-listed
  to baseline current state; should drop off as fixes land.

Adapt to your project:
1. Set MEANINGFUL_BUSINESS_COLUMNS to your project's column list.
2. Set AUDIT_TABLES to your project's audit-table list.
3. Set _EXCLUDED_FILENAMES to your schema-authority files (migrations,
   schema DDL, seed data).
4. _KNOWN_ALLOWED starts empty; baseline by running, add legitimate
   exceptions with justification, ratchet down over time.
"""

import ast
import re
import sys
import unittest
from pathlib import Path

# Adapt: the root of your handler/business-logic Python files.
# Usually the repo root; adjust if your code lives in a subdirectory.
ROOT = Path(__file__).resolve().parent.parent  # ADAPT


# Files that are unequivocally NOT subject to handler-level invariants.
# Schema authorities, migrations, the migration runner, seed data, and
# tests themselves are excluded.
_EXCLUDED_FILENAMES = {
    # Adapt to your project's schema-authority files
    "models.py",
    "migrations.py",
    "migration_runner.py",
    "seed_data.py",
}


# Columns whose value is a meaningful business fact — overwriting one
# without recording its prior value is the F1 violation.
#
# Deliberately EXCLUDED: voided_at, closed_at, cancelled_at, ended_at.
# These are pure NULL→timestamp transitions; the column transition itself
# IS the audit. Overwriting one of these to a different timestamp is a
# separate (rarer) violation that this scan won't catch and would need
# its own check.
MEANINGFUL_BUSINESS_COLUMNS = {  # ADAPT
    # Core lifecycle / state
    "current_stage", "status", "decision",
    # Money
    "sale_price", "purchase_price", "buyers_premium", "cost_basis",
    "platform_fees", "shipping_cost", "final_hammer_price",
    # Identity / classification
    "title", "description", "condition_grade", "condition_notes",
    "category_id", "size_class", "material",
    # FK rewrites (re-pointing parentage)
    "auction_item_id", "inventory_id", "signature_id",
}


# Audit / event tables that satisfy the "I left a trail" requirement.
AUDIT_TABLES = {  # ADAPT
    "fact_corrections",
    "pipeline_events",
    "lifecycle_events",
    "ai_identifications",
    "match_suggestion_outcomes",
    "lesson_candidates",
}


_UPDATE_RE = re.compile(
    r"UPDATE\s+(\w+)\s+SET\s+(.*?)(?:WHERE|\"\"\"|\Z)",
    re.IGNORECASE | re.DOTALL,
)
_AUDIT_INSERT_RE = re.compile(
    r"INSERT\s+(?:OR\s+\w+\s+)?INTO\s+(" +
    "|".join(re.escape(t) for t in AUDIT_TABLES) +
    r")\b",
    re.IGNORECASE,
)


def _handler_files() -> list[Path]:
    """Python files at repo root subject to handler-level invariants.

    Excludes schema authorities, migrations, seed data, and the test
    directory itself.
    """
    return [
        p for p in sorted(ROOT.glob("*.py"))
        if p.name not in _EXCLUDED_FILENAMES
    ]


def _function_sources(file_path: Path):
    """Yield (function_name, function_source) tuples for every top-level
    FunctionDef and AsyncFunctionDef in the file. Methods inside classes
    are also yielded (qualified as Class.method)."""
    src = file_path.read_text()
    try:
        tree = ast.parse(src)
    except SyntaxError:
        return
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            seg = ast.get_source_segment(src, node)
            if seg:
                yield (node.name, seg)


def _find_meaningful_updates(file_path: Path):
    """Yield (function_name, columns_set) for every function that UPDATEs
    at least one MEANINGFUL_BUSINESS_COLUMNS column without pairing it
    with an audit-table INSERT in the same function body."""
    for fname, fsrc in _function_sources(file_path):
        meaningful_cols = set()
        for m in _UPDATE_RE.finditer(fsrc):
            set_clause = m.group(2)
            for col_m in re.finditer(r"(\w+)\s*=", set_clause):
                col = col_m.group(1).lower()
                if col in MEANINGFUL_BUSINESS_COLUMNS:
                    meaningful_cols.add(col)
        if not meaningful_cols:
            continue
        has_audit = bool(_AUDIT_INSERT_RE.search(fsrc))
        if not has_audit:
            yield (fname, meaningful_cols)


class TestUpdateRequiresFactCorrection(unittest.TestCase):
    """Functions that UPDATE meaningful business columns must also
    leave an audit trail."""

    # Allow-list: function names that legitimately UPDATE meaningful
    # columns without writing to an audit table. Each entry must carry
    # an inline justification. To remove an entry, fix the function so
    # it writes an audit row, then drop the entry.
    #
    # Format: (filename, function_name) → reason
    _KNOWN_ALLOWED = {  # BASELINE — populated when first adopted
        # Example LEGITIMATE entry:
        # ("lifecycle_handlers.py", "api_decide_pending_review"):
        #     "LEGITIMATE — decided_at + decided_by + decision_notes "
        #     "ARE the audit (lifecycle-transition pattern, F1). The "
        #     "column writes themselves are the event.",
        #
        # Example DEFERRED entry:
        # ("legacy_import_handler.py", "bulk_update_categories"):
        #     "DEFERRED — pre-audit bulk import, tracked in TODO.md "
        #     "as P-007. Fix: route through corrections_handlers.",
    }

    def test_no_unaudited_updates(self):
        violations = []
        for file_path in _handler_files():
            for fname, cols in _find_meaningful_updates(file_path):
                if (file_path.name, fname) in self._KNOWN_ALLOWED:
                    continue
                violations.append(
                    f"  {file_path.name}:{fname} UPDATEs {sorted(cols)}"
                )
        if violations:
            msg = (
                "Functions that UPDATE meaningful business columns must "
                "also INSERT into an audit table (fact_corrections or "
                "equivalent) in the same function body.\n"
                "\nViolations:\n" + "\n".join(violations) +
                "\n\nSee CLAUDE.md §audit-as-shape decision trigger. To "
                "fix: wrap the UPDATE in a transaction with a "
                "fact_corrections INSERT recording prior_value, new_value, "
                "reason, confidence. If the UPDATE legitimately doesn't "
                "need audit (the column write IS the lifecycle event), "
                "add to _KNOWN_ALLOWED with a LEGITIMATE justification."
            )
            self.fail(msg)


if __name__ == "__main__":
    unittest.main()
