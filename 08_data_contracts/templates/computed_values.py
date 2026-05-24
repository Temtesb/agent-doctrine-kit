"""Computed Value Contracts — every stored computed value declares its formula, inputs, refresh trigger, and mutation paths.

Derives from Foundation F2 (single source of truth — two implementations
of the same formula will diverge unless kept structurally identical) and
F1 (computed values that don't refresh on input changes are stale, which
is an F1 violation of "history must answer 'what was true at time T'").

USAGE:
  1. Copy this file to your project as `contracts/computed_values.py`.
  2. Replace the example entries with your project's stored computed values.
  3. Wire the verification tests (see ../README.md) so that every
     declared mutation_path is verified to call the refresh_trigger.

A stored computed value WITHOUT a contract is an F1/F2 violation
waiting to surface — the cache will drift when an input changes
through an unrecognized mutation path. The contract makes the
recomputation surface mechanically enforceable.

PRINCIPLE: prefer NOT storing computed values. Compute at query time
unless there's a measured performance problem. Only stored computed
values need contracts.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class ComputedValueContract:
    """Declaration that one stored computed value has these inputs,
    this formula, and these mutation paths that must trigger refresh.

    Fields:
      formula: Fully-qualified function name that computes the value.
        Format: 'module.function'. Tests verify it resolves.
      inputs: List of input columns the formula depends on. Format:
        'table.column'. Wildcards allowed for fan-out:
        'expenses.*' = any column in the expenses table; the formula
        depends on the table's rows, not specific columns.
      refresh_trigger: Function that recomputes the cached value. Format:
        'module.function'. Tests verify it resolves.
      mutation_paths: Every function that writes to any input listed
        above. Tests verify each function calls refresh_trigger.
        Format: list of 'module.function' identifiers.
      as_of_column: Required for all stored computed values per F1.
        The column that records when the cache was last computed.
        Tests verify the column exists in the same table as the
        cached value.
    """
    formula: str
    inputs: list[str]
    refresh_trigger: str
    mutation_paths: list[str]
    as_of_column: str


# ─── The registry ────────────────────────────────────────────────────────


COMPUTED_VALUES: dict[str, ComputedValueContract] = {

    # ─── Example: a cached financial calculation ──────────────────────

    "sales.net_profit": ComputedValueContract(
        formula="calculations.compute_net_profit",
        inputs=[
            "sales.sale_price",
            "inventory.cost_basis",
            "expenses.*",                  # any expense row affects profit
            "config.ebay_fee_pct",         # global setting changes too
            "config.shipping_fee_default",
        ],
        refresh_trigger="calculations.recompute_sale_profit",
        mutation_paths=[
            # Every code path that mutates an input MUST call the trigger.
            # Tests scan these functions to confirm.
            "listing_management_handlers.api_record_sale",
            "ebay_rest_api.sync_order",
            "settings_handlers.api_update_fee_settings",
            "expense_handlers.api_add_expense",
            "expense_handlers.api_edit_expense",
            "expense_handlers.api_void_expense",
        ],
        as_of_column="sales.net_profit_as_of",
    ),

    # ─── Example: a cached aggregate count ────────────────────────────

    "auctions.total_bids": ComputedValueContract(
        formula="bid_aggregations.compute_total_bids",
        inputs=["bids.*"],                 # any bid row affects total
        refresh_trigger="bid_aggregations.recompute_total_bids",
        mutation_paths=[
            "bid_handlers.api_record_bid",
            "bid_handlers.api_void_bid",
            "bid_handlers.api_correct_bid",
        ],
        as_of_column="auctions.total_bids_as_of",
    ),

    # ─── Example: a cached scoring value ──────────────────────────────

    "inventory.priority_score": ComputedValueContract(
        formula="inventory_scoring.compute_priority_score",
        inputs=[
            "inventory.category_id",
            "inventory.estimated_value",
            "inventory.days_in_pipeline",
            "category_modeling.*",         # category model changes affect all
        ],
        refresh_trigger="inventory_scoring.recompute_priority_score",
        mutation_paths=[
            "inventory_crud_handlers.api_update_inventory",
            "inventory_pipeline_handlers.api_advance_stage",
            "category_modeling.api_recalibrate_category",
            # The daily scheduled job that re-scores all inventory:
            "inventory_scoring.daily_recompute_all",
        ],
        as_of_column="inventory.priority_score_as_of",
    ),

    # ─── Add your project's stored computed values here ───────────────
}


# ─── Verification helpers ────────────────────────────────────────────────


def get_contract(stored_path: str) -> Optional[ComputedValueContract]:
    """Return the contract for a stored value path (table.column)."""
    return COMPUTED_VALUES.get(stored_path)


def list_mutation_paths_for_input(input_path: str) -> list[tuple[str, list[str]]]:
    """Return [(stored_path, mutation_paths), ...] for every contract
    whose inputs include the given input_path.

    Useful when a refactor is about to modify a mutation path — you
    can check what computed values depend on the column it writes to.
    """
    results = []
    for stored, contract in COMPUTED_VALUES.items():
        if input_path in contract.inputs or any(
            i.endswith(".*") and input_path.startswith(i[:-2] + ".")
            for i in contract.inputs
        ):
            results.append((stored, contract.mutation_paths))
    return results


def list_stored_values_without_as_of() -> list[str]:
    """All stored computed values that DON'T declare an as_of column.

    This should always be empty in a healthy project — every stored
    computed value needs an as_of per F1. The function exists so the
    test can fail with a clear message if someone adds an entry
    without the as_of field set.
    """
    return [
        path for path, contract in COMPUTED_VALUES.items()
        if not contract.as_of_column
    ]


# ─── Notes ───────────────────────────────────────────────────────────────
#
# WHEN TO STORE vs. WHEN TO COMPUTE AT QUERY TIME:
#
# Default: compute at query time. It's simpler, has no drift risk,
# and database query engines are good at aggregations.
#
# Store the computed value ONLY when:
# 1. The computation is expensive enough to measure in user-visible
#    latency on common queries, AND
# 2. The mutation paths are enumerable and stable, AND
# 3. You're willing to maintain the contract as the codebase evolves.
#
# If any of those is false, compute at query time. The cost of the
# extra query is almost always less than the cost of a drifted cache.
#
# WHEN A CONTRACT DRIFTS:
#
# The most common drift: a new function is added that writes to one
# of the inputs but isn't listed in mutation_paths. The function
# doesn't call refresh_trigger, so the cache becomes stale.
#
# The verification test catches this by scanning ALL handler files
# for writes to declared inputs and asserting every writer is either
# in mutation_paths OR calls refresh_trigger.
#
# WHEN AN INPUT CHANGES SHAPE:
#
# If an input column is renamed, the contract becomes stale silently.
# The verification test should also check that every declared input
# resolves to an existing column. This is the schema-introspection
# check that lives at the System Reviewer's Layer 1.
