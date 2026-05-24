"""Business Event Boundaries — every business event that touches multiple tables declares them.

Derives from Foundation F2 (atomicity in cross-table updates — multiple
tables representing one logical state must remain consistent;
transactions enforce this).

A business event is any operation that updates multiple tables as part
of one logical change: recording a sale, advancing a pipeline stage,
linking inventory to an auction lot, processing a refund. These events
require atomicity — all writes succeed or none do.

USAGE:
  1. Copy this file to your project as `contracts/business_events.py`.
  2. Replace the example entries with your project's events.
  3. Wire the verification tests (see ../README.md) so the handler is
     verified to actually touch all declared tables in a single
     transaction.

A business event declaration is what makes "partial state" (the row in
sales says sold, the row in inventory still says active) a CI failure
rather than a production bug.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class BusinessEvent:
    """Declaration that one business event touches these tables
    atomically through this handler.

    Fields:
      description: One sentence stating what the event represents.
      tables_touched: List of tables the handler writes to as part of
        the event. Tests verify the handler's body actually writes to
        each (via static SQL analysis or instrumented test runs).
      handler: Fully-qualified function name that implements the event.
        Format: 'module.function'. Tests verify it resolves.
      atomicity: One of 'required' (single transaction enforced) or
        'eventual' (writes happen in sequence with idempotency). Most
        events should be 'required'; 'eventual' is for events that
        span systems where a single transaction isn't possible (e.g.,
        a write to your DB plus a call to an external API).
      compensation: Required when atomicity='eventual'. The function
        that undoes partial writes if the event fails mid-sequence.
    """
    description: str
    tables_touched: list[str]
    handler: str
    atomicity: str = "required"  # 'required' | 'eventual'
    compensation: Optional[str] = None


# ─── The registry ────────────────────────────────────────────────────────


BUSINESS_EVENTS: dict[str, BusinessEvent] = {

    # ─── Example: recording a sale ─────────────────────────────────────
    # All tables update together or none of them do.

    "record_sale": BusinessEvent(
        description="Recording a completed sale",
        tables_touched=[
            "sales",                # INSERT the sale row
            "inventory",            # UPDATE the item's stage to 'sold'
            "ebay_listings",        # UPDATE the listing status to 'completed'
            "listings",             # UPDATE the listing status to 'completed'
            "pipeline_events",      # INSERT the stage-transition event
        ],
        handler="listing_management_handlers.api_record_sale",
        atomicity="required",
    ),

    # ─── Example: advancing a pipeline stage ──────────────────────────

    "advance_stage": BusinessEvent(
        description="Moving an item to the next pipeline stage",
        tables_touched=[
            "inventory",            # UPDATE current_stage
            "pipeline_events",      # INSERT the transition event
        ],
        handler="inventory_pipeline_handlers.api_advance_stage",
        atomicity="required",
    ),

    # ─── Example: linking inventory to an auction lot ─────────────────

    "link_auction_lot": BusinessEvent(
        description="Connecting an inventory row to its source auction lot",
        tables_touched=[
            "inventory",            # UPDATE auction_item_id, purchase_price, etc.
            "fact_corrections",     # INSERT audit row(s) for each copied field
        ],
        handler="acquisition_handlers.api_link_auction_lot",
        atomicity="required",
    ),

    # ─── Example: eventual-consistency event (cross-system) ───────────

    "publish_listing_to_ebay": BusinessEvent(
        description="Pushing a draft listing to eBay's marketplace",
        tables_touched=[
            "listings",             # UPDATE status to 'published'
            "ebay_listings",        # UPSERT the eBay-side state record
            "pipeline_events",      # INSERT the publish event
        ],
        handler="ebay_listing_push.api_publish_listing",
        atomicity="eventual",       # eBay API call + local writes can't share txn
        compensation="ebay_listing_push.rollback_publish_attempt",
    ),

    # ─── Add your project's business events here ──────────────────────
}


# ─── Verification helpers ────────────────────────────────────────────────


def get_event(name: str) -> Optional[BusinessEvent]:
    """Return the BusinessEvent for a name, or None if undeclared."""
    return BUSINESS_EVENTS.get(name)


def list_events_touching(table: str) -> list[str]:
    """Return business event names that touch the given table.

    Useful when refactoring a table — you can see which events depend
    on it.
    """
    return [
        name for name, event in BUSINESS_EVENTS.items()
        if table in event.tables_touched
    ]


def list_eventual_events_without_compensation() -> list[str]:
    """Eventual-consistency events that don't declare a compensation
    function.

    Should always be empty in a healthy project — eventual events
    without compensation are partial-state failures waiting to happen.
    """
    return [
        name for name, event in BUSINESS_EVENTS.items()
        if event.atomicity == "eventual" and not event.compensation
    ]


# ─── Notes ───────────────────────────────────────────────────────────────
#
# THE TESTS THIS REGISTRY ENABLES:
#
# 1. Handler-exists test: every `handler` resolves to a callable.
#    Catches refactors that renamed the handler without updating the
#    contract.
#
# 2. Tables-touched test: each handler's source code (via SQL pattern
#    matching or AST analysis) is verified to contain writes to every
#    declared table. Catches the failure mode where someone refactored
#    the handler to skip one of the writes.
#
# 3. Atomicity test: for events with atomicity='required', verify the
#    handler wraps all writes in a single transaction. Look for
#    BEGIN/COMMIT or `with conn:` patterns, and verify no write
#    happens outside the transaction.
#
# 4. Compensation-exists test: for events with atomicity='eventual',
#    verify the `compensation` function exists.
#
# 5. Coverage test: for each business event registered, verify that
#    the handler isn't bypassed by other writers. If another function
#    UPDATEs `sales` and `inventory` together without going through
#    api_record_sale, that's a partial-state risk worth surfacing.
#
# These tests live at System Reviewer Layer 1.
#
# WHY 'EVENTUAL' EVENTS ARE LAST-RESORT:
#
# Atomicity across multiple writes is what F2 demands. 'eventual' is
# the concession to physics — when one of the writes is to an external
# system (eBay, payment processor, email), a single transaction is
# impossible. The compensation function is the structural mitigation:
# if the event fails partway through, compensation undoes what was
# already written.
#
# The system should have very few 'eventual' events. Most events
# should be 'required'. If you find yourself adding 'eventual' often,
# question whether the multi-system coupling is the right design.
