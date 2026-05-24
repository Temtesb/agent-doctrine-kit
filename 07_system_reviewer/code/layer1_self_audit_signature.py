"""System Reviewer Layer 1 — interface signatures for deterministic checks.

Implements the Layer 1 checks described in ../doctrine/two_layers.md.
Each check is a pure function returning a CheckResult; the runner
collects results and produces a structured report.

This file is the INTERFACE. Each check function is a sketch — the
actual implementation depends on your project's schema, contract
format, module conventions, and CI integration.

Layer 2 (AI architectural review) is not implemented in this file. It
is a project-specific AI call that consumes the same data + Layer 1's
output. See ../doctrine/two_layers.md for the Layer 2 design.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, Optional


@dataclass
class CheckResult:
    """Result of one Layer 1 check."""
    check_name: str
    passed: bool
    message: str                    # Human-readable summary
    remediation: Optional[str] = None  # How to fix (when passed=False)
    metric_value: Optional[float] = None  # e.g., coverage percentage
    details: list[str] = field(default_factory=list)  # Per-violation details


@dataclass
class ReviewReport:
    """Aggregate result of a Layer 1 audit pass."""
    timestamp: str
    results: list[CheckResult]

    @property
    def passed_count(self) -> int:
        return sum(1 for r in self.results if r.passed)

    @property
    def failed_count(self) -> int:
        return sum(1 for r in self.results if not r.passed)

    @property
    def overall_passed(self) -> bool:
        return self.failed_count == 0


# ─── Individual check signatures ─────────────────────────────────────────


def check_migration_completeness(migrations_dir: Path) -> CheckResult:
    """Migration filenames are sequential with no gaps; highest number
    matches the declared schema version.

    Implementation sketch:
    1. List migration files (e.g., NNN_*.py / NNN_*.sql)
    2. Extract the leading number from each
    3. Verify sequential (1, 2, 3, ... no gaps)
    4. Query the schema_versions ledger for the current version
    5. Assert max(file_numbers) == current_version

    Fails on: gap (missing 003 between 002 and 004), out-of-order
    files, schema_versions disagreeing with file count.
    """
    raise NotImplementedError("Adapt to your migration format.")


def check_fresh_install_vs_upgrade(migrations_dir: Path,
                                    schema_dump_fn: Callable) -> CheckResult:
    """Running all migrations on an empty DB produces the same schema
    as running them on a DB that already had earlier ones.

    Implementation sketch:
    1. Spin up two ephemeral DBs.
    2. DB A: run migrations 001 through N in sequence.
    3. DB B: run migrations 001 through N-1, then N.
    4. Dump both schemas (schema_dump_fn).
    5. Assert they're equal.

    Catches the classic failure where a migration was meant to update
    something existing but the fresh-install path treats it as a no-op.
    """
    raise NotImplementedError("Adapt to your DB layer.")


def check_contract_coverage(tables: list[str],
                            fact_owners: dict,
                            computed_values: dict,
                            business_events: dict) -> CheckResult:
    """Reports the percentage of tables with declared fact owners,
    stored computed values with refresh contracts, business events
    with declared atomicity.

    Implementation sketch:
    1. tables_with_owners = set of tables referenced as `storage` in fact_owners
    2. tables_with_computed = set of tables containing any computed_values column
    3. tables_with_events = set of tables in any business_event's tables_touched
    4. Compute coverage metrics
    5. Return CheckResult with metric_value set to the lowest coverage

    Does NOT fail on low coverage — reports it. Layer 2 decides whether
    the coverage shape is concerning. The intent: surface gaps without
    forcing premature completeness.
    """
    raise NotImplementedError("Adapt to your contract format.")


def check_module_size(handler_files: list[Path],
                      soft_limit: int = 500,
                      hard_limit: int = 800) -> CheckResult:
    """File line counts vs. soft and hard limits.

    Implementation sketch:
    1. For each handler file, count non-blank non-comment lines.
    2. Bucket into under-soft, soft-to-hard, over-hard.
    3. Fail on any over-hard. Warn on any soft-to-hard.

    Adapt the line-counting rule to your project's conventions
    (some count docstrings; some don't; some count test files
    separately).
    """
    raise NotImplementedError("Adapt to your module conventions.")


def check_module_has_test(handler_files: list[Path],
                          tests_dir: Path) -> CheckResult:
    """Every module has at least one corresponding test file.

    Implementation sketch:
    1. For each handler file <name>.py, check whether
       tests/test_<name>.py or tests/test_<name>_*.py exists.
    2. Fail with the list of modules lacking tests.

    Adapt the test-file naming convention to your project.
    """
    raise NotImplementedError("Adapt to your test conventions.")


def check_doc_references_resolve(governance_doc_paths: list[Path],
                                  repo_root: Path) -> CheckResult:
    """Files referenced in governance docs still exist; cross-references
    are not broken.

    Implementation sketch:
    1. Parse each governance doc for relative file paths and code links.
    2. For each referenced path, check os.path.exists.
    3. Fail with the list of broken references.

    Catches the case where a refactor renamed files but the governance
    doc wasn't updated.
    """
    raise NotImplementedError("Adapt to your doc and link conventions.")


def check_registered_handler_has_test(handler_registry: dict,
                                      tests_dir: Path) -> CheckResult:
    """Every registered handler has at least one test.

    Implementation sketch:
    1. For each handler name in the registry, grep tests_dir for the name.
    2. Fail with the list of unhandled handlers.
    """
    raise NotImplementedError("Adapt to your registry and test format.")


def check_fact_owner_functions_exist(fact_owners: dict,
                                     module_loader: Callable) -> CheckResult:
    """Every fact_owners entry's `source` function exists and is callable.

    Implementation sketch:
    1. For each fact_owners entry, parse `source` as module.function.
    2. Attempt to import the module and resolve the function.
    3. Fail with the list of broken references.

    Catches the case where a fact owner was declared but the function
    was renamed or removed.
    """
    raise NotImplementedError("Adapt to your import mechanism.")


def check_dependency_graph(handler_files: list[Path],
                            max_imports_per_module: int = 8) -> CheckResult:
    """No circular imports; no modules with excessive coupling.

    Implementation sketch:
    1. Parse each handler file's imports.
    2. Build a directed graph of project-internal imports.
    3. Detect cycles (Tarjan's strongly-connected components).
    4. Detect over-coupled modules (out-degree > max_imports_per_module).
    5. Fail with violations.
    """
    raise NotImplementedError("Adapt to your import scanner.")


# ─── Runner ──────────────────────────────────────────────────────────────


# The set of Layer 1 checks. Add/remove based on what's relevant to
# your project. Each entry is (check_name, callable, kwargs).
LAYER_1_CHECKS = [
    # ("migration_completeness", check_migration_completeness, {"migrations_dir": ...}),
    # ("fresh_install_vs_upgrade", check_fresh_install_vs_upgrade, {...}),
    # ("contract_coverage", check_contract_coverage, {...}),
    # ("module_size", check_module_size, {...}),
    # ("module_has_test", check_module_has_test, {...}),
    # ("doc_references_resolve", check_doc_references_resolve, {...}),
    # ("registered_handler_has_test", check_registered_handler_has_test, {...}),
    # ("fact_owner_functions_exist", check_fact_owner_functions_exist, {...}),
    # ("dependency_graph", check_dependency_graph, {...}),
]


def run_layer_1() -> ReviewReport:
    """Run all Layer 1 checks; return aggregate report."""
    from datetime import datetime
    results = []
    for name, fn, kwargs in LAYER_1_CHECKS:
        try:
            result = fn(**kwargs)
            results.append(result)
        except Exception as e:
            # A check that raises is itself a problem worth surfacing,
            # but it shouldn't crash the runner.
            results.append(CheckResult(
                check_name=name,
                passed=False,
                message=f"Check raised exception: {type(e).__name__}: {e}",
                remediation=f"Fix the {name} check implementation.",
            ))
    return ReviewReport(
        timestamp=datetime.now().isoformat(),
        results=results,
    )


# ─── CLI sketch ──────────────────────────────────────────────────────────
#
# if __name__ == "__main__":
#     report = run_layer_1()
#     print(f"Layer 1 audit at {report.timestamp}")
#     print(f"Passed: {report.passed_count}, Failed: {report.failed_count}")
#     for r in report.results:
#         status = "✓" if r.passed else "✗"
#         print(f"  {status} {r.check_name}: {r.message}")
#         if r.remediation and not r.passed:
#             print(f"    Remediation: {r.remediation}")
#     sys.exit(0 if report.overall_passed else 1)
