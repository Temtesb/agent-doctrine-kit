"""Template — the _KNOWN_ALLOWED ratchet pattern for architecture invariants.

This is the meta-pattern that every architecture invariant test in this
kit follows. Copy this file as a starting point when adding a new
invariant, then adapt the pattern detection and the allow-list seed.

The ratchet pattern has three properties:

1. Baseline current state. Run the test on first adoption; every
   existing violation gets an entry in _KNOWN_ALLOWED with an inline
   justification — either LEGITIMATE (the violation is actually correct
   under doctrine; the test's pattern is too broad) or DEFERRED (the
   violation is real and tracked for future cleanup).

2. Block additions. New code that violates the invariant fails CI
   immediately. Adding to _KNOWN_ALLOWED requires a code-review
   explanation, which is the right friction for a regression.

3. Ratchet down on fixes. Removing an entry from _KNOWN_ALLOWED is the
   structural form of "we fixed it." The baseline can only shrink,
   never grow.

Derives from Foundations F2 (the codebase and the doctrine cannot
contradict each other at the file-system level) and E2 (each invariant
test is a structural triangulating probe of doctrine compliance).
"""

import ast
import re
import sys
import unittest
from pathlib import Path

# Adapt: the root of your handler/business-logic Python files.
ROOT = Path(__file__).resolve().parent.parent  # ADAPT


# Files that are unequivocally NOT subject to this invariant.
# Schema authorities, migrations, the migration runner, seed data, and
# tests themselves are usually excluded.
_EXCLUDED_FILENAMES = {  # ADAPT
    "models.py",
    "migrations.py",
    "migration_runner.py",
    "seed_data.py",
}


def _handler_files() -> list[Path]:
    """Python files at repo root subject to this invariant."""
    return [
        p for p in sorted(ROOT.glob("*.py"))
        if p.name not in _EXCLUDED_FILENAMES
    ]


def _function_sources(file_path: Path):
    """Yield (function_name, function_source) tuples for every top-level
    FunctionDef and AsyncFunctionDef in the file."""
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


def _detect_violations(file_path: Path):
    """The pattern-detection function. ADAPT THIS to your invariant.

    Yields (function_name, violation_detail) tuples for every function
    in the file that violates the invariant.

    Example: an invariant that "every function with a `pd.read_csv` call
    must also include a `pd.errors.EmptyDataError` handler" would scan
    each function's source for a pd.read_csv call and check whether the
    same function source contains the error class name.

    Keep this function deterministic and idempotent — running the test
    twice on the same code produces the same violation list.
    """
    # ADAPT: replace this with your invariant's detection logic.
    for fname, fsrc in _function_sources(file_path):
        # Example placeholder pattern:
        if "BAD_PATTERN_PLACEHOLDER" in fsrc:
            yield (fname, "BAD_PATTERN_PLACEHOLDER detected")


class TestInvariantNameHere(unittest.TestCase):
    """ADAPT: one-line statement of the invariant.

    Longer docstring explaining what doctrine the invariant enforces,
    what the bug shape looks like, and what the fix shape is. Include
    a pointer to the doctrine excerpt this invariant derives from.

    Derives from: <doctrine anchor>.
    """

    # Allow-list: function locations that legitimately fail the
    # invariant. Each entry must carry an inline justification.
    #
    # Format: (filename, function_name) → reason
    #
    # Categories used in justifications:
    #   LEGITIMATE — the violation is actually correct under doctrine;
    #     fixing the code would be wrong (e.g., the pattern detection
    #     is over-broad and catches a sibling shape that's OK). Stays
    #     in the allow-list permanently with a clear explanation.
    #
    #   DEFERRED — real violation, tracked as ratchet-down work in
    #     TODO.md or equivalent. Allow-listed to baseline current state;
    #     should drop off as fixes land.
    _KNOWN_ALLOWED = {  # BASELINE — populated on first adoption
        # Example LEGITIMATE entry:
        # ("handlers.py", "api_some_handler"):
        #     "LEGITIMATE — handler explicitly catches the exception "
        #     "via the @handle_errors decorator one level up; the local "
        #     "absence is correct.",
        #
        # Example DEFERRED entry:
        # ("legacy.py", "old_import_path"):
        #     "DEFERRED — pre-invariant code, tracked in TODO.md as "
        #     "P-007. Fix: add the missing error handler.",
    }

    def test_invariant(self):
        violations = []
        for file_path in _handler_files():
            for fname, detail in _detect_violations(file_path):
                if (file_path.name, fname) in self._KNOWN_ALLOWED:
                    continue
                violations.append(f"  {file_path.name}:{fname} — {detail}")
        if violations:
            msg = (
                # ADAPT: human-readable failure message that explains
                # what doctrine was violated and how to fix.
                "Invariant violated.\n\n"
                "Violations:\n" + "\n".join(violations) +
                "\n\nSee <doctrine anchor> for the principle. To fix: "
                "<concrete remediation guidance>. If the violation is "
                "actually correct under doctrine, add to _KNOWN_ALLOWED "
                "with a LEGITIMATE justification."
            )
            self.fail(msg)


if __name__ == "__main__":
    unittest.main()


# ─── Adapting this template ─────────────────────────────────────────────
#
# Step 1: Decide the invariant.
#   What doctrine clause does the invariant enforce? Make sure the
#   doctrine clause exists and is current. If it doesn't exist yet,
#   write the doctrine first.
#
# Step 2: Implement _detect_violations.
#   What pattern, when present in a function, constitutes a violation?
#   Use regex for simple cases (a string is or isn't in the source).
#   Use AST walking for structural cases (function calls a specific
#   thing, function lacks a try/except around a specific call). Aim for
#   false-positive tolerance over false-negative tolerance — it's better
#   to over-detect and require allow-list entries than to under-detect
#   and let violations through.
#
# Step 3: Baseline.
#   Run the test on the current codebase. Every failure either:
#   a) Reveals a real violation. Fix it.
#   b) Reveals a legitimate-but-detected case. Add to _KNOWN_ALLOWED
#      with LEGITIMATE justification.
#   c) Reveals a violation that's too expensive to fix immediately.
#      Add to _KNOWN_ALLOWED with DEFERRED justification, file the
#      fix as TODO.
#
# Step 4: Ship.
#   Commit the test + the baselined _KNOWN_ALLOWED. CI now catches new
#   instances. Over time, DEFERRED entries should drop off.
#
# Step 5: Cross-reference.
#   Add an entry to your project's PATTERNS.md naming this invariant
#   as the enforcer for the bug shape. Update doctrine to reference
#   the invariant test as the structural mechanism backing the rule.
