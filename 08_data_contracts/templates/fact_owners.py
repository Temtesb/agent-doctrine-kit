"""Fact Ownership Registry — every core data concept maps to its single authoritative source.

Derives from Foundation F2 (single source of truth applied to data).
Without explicit ownership, the same concept can live in multiple
places without anyone noticing the duplication. The registry makes
ownership queryable: ask "where does X come from?" and get one answer.

USAGE:
  1. Copy this file to your project as `contracts/fact_owners.py`
     (or wherever your project keeps declarative configuration).
  2. Replace the example entries with your project's concepts.
  3. Wire the verification tests (see ../README.md) so the registry's
     declarations get mechanically verified against reality.

The registry is INCREMENTAL — start sparse, grow as concepts surface
as load-bearing. The framework doesn't require completeness; it
requires that whatever IS declared gets verified.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class FactOwner:
    """Declaration that one concept is owned by one source.

    Fields:
      source: The fully-qualified function name that produces this
        fact. Format: 'module.function' or 'module.Class.method'.
        Tests verify this resolves to a callable.
      description: One-sentence statement of what this fact represents.
      storage: Optional. If the fact is also stored as a cache, the
        column path (table.column). Tests verify the column exists.
      refresh: Required if storage is set. The function that recomputes
        the stored value. Tests verify the refresh function exists.
      valid_values: Optional. For enum-shaped facts, the list of valid
        values. Tests verify the storage column has a CHECK constraint
        with these values.
      audit_table: Optional. The audit/event table that records
        mutations to this fact (see ../../02_audit_as_shape/). When
        set, the architecture invariant test that enforces
        "UPDATE on meaningful column requires audit row" uses this
        to know which audit table is expected for this fact.
    """
    source: str
    description: str
    storage: Optional[str] = None
    refresh: Optional[str] = None
    valid_values: Optional[list] = None
    audit_table: Optional[str] = None


# ─── The registry ────────────────────────────────────────────────────────


FACT_OWNERS: dict[str, FactOwner] = {

    # ─── Example: a computed-and-stored fact ──────────────────────────
    # Replace with your project's concepts.

    "net_profit": FactOwner(
        source="calculations.compute_net_profit",
        description="Sale price minus cost basis, expenses, fees, shipping",
        storage="sales.net_profit",  # cached for query performance
        refresh="calculations.recompute_sale_profit",  # required when storage set
        audit_table="fact_corrections",
    ),

    # ─── Example: a pure-computed fact (no storage) ───────────────────

    "available_to_promise_units": FactOwner(
        source="inventory.compute_available_to_promise",
        description="Inventory units not reserved by a pending order",
        # No storage = computed at query time, no refresh needed
    ),

    # ─── Example: a status/enum fact ──────────────────────────────────

    "item_status": FactOwner(
        source="inventory.current_stage",
        description="Current pipeline stage for an inventory item",
        storage="inventory.current_stage",
        valid_values=[
            "received", "shelf", "cleaning", "photography",
            "listed", "sold", "shipped",
        ],
        audit_table="pipeline_events",  # status transitions go in events table
    ),

    # ─── Example: a derived-from-external-source fact ─────────────────

    "ebay_listing_status": FactOwner(
        source="ebay_rest_api.get_listing_status",
        description="Authoritative listing status from eBay's API",
        storage="ebay_listings.status",  # cached for query performance
        refresh="ebay_rest_api.sync_listing_status",
        valid_values=["active", "ended", "completed", "draft", "deleted"],
        audit_table="fact_corrections",
    ),

    # ─── Add your project's concepts here ─────────────────────────────
}


# ─── Verification helpers ────────────────────────────────────────────────


def get_fact_owner(concept: str) -> Optional[FactOwner]:
    """Return the FactOwner for a concept, or None if undeclared."""
    return FACT_OWNERS.get(concept)


def list_concepts_owned_by(source_module: str) -> list[str]:
    """Return concept names whose source is in the given module.

    Useful for the System Reviewer to ask 'what does this module own?'
    """
    return [
        name for name, owner in FACT_OWNERS.items()
        if owner.source.startswith(source_module + ".")
    ]


def list_concepts_with_storage() -> list[str]:
    """Return concept names that have a stored cache.

    Useful for the System Reviewer to verify every stored cache has
    a refresh trigger (storage without refresh is an F2 violation).
    """
    return [
        name for name, owner in FACT_OWNERS.items()
        if owner.storage is not None
    ]


def list_concepts_without_audit() -> list[str]:
    """Return concept names that don't declare an audit table.

    Useful for the System Reviewer to flag concepts that may need
    audit-table coverage but haven't declared one.
    """
    return [
        name for name, owner in FACT_OWNERS.items()
        if owner.audit_table is None
    ]


# ─── Notes ───────────────────────────────────────────────────────────────
#
# What this registry does NOT do:
#
# 1. It does not enforce that the source function actually produces
#    the fact correctly. That's a unit-test concern, separate from
#    ownership declaration.
#
# 2. It does not enforce that no other module produces the same fact.
#    The System Reviewer's Layer 2 (AI architectural review) catches
#    that by reading the codebase and looking for parallel
#    implementations.
#
# 3. It does not enforce that every project concept appears here. The
#    coverage is incremental; what matters is that what IS declared
#    gets verified.
#
# What this registry DOES do:
#
# 1. Makes ownership queryable: "where does X come from?" → one line.
# 2. Enables mechanical verification: tests confirm declared sources
#    exist and refresh triggers fire on every mutation path.
# 3. Provides the structural answer to the pre-flight's question 1:
#    "what doctrine governs this change?" → "this concept is owned by
#    Y; the change must preserve Y's contract."
# 4. Feeds the System Reviewer's contract-coverage metric: % of tables
#    with declared fact owners.
