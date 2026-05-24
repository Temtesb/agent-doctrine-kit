# Reflective-layer freshness audit

## The pattern

**The principle:** *"Artifacts of truth exist; nothing forces downstream readers to consult them at the moment of use. The fix at every layer is a structural enforcer at the consumer's decision moment — not another principle entry."*

A reconciliation pass runs before any consumer acts on a reflective surface (briefing, ledger, status field, proposal review). For each open observation entry whose claim references substrate (a manifest clause, a commit SHA, a doctrine section, a code call site, a config key), the pass resolves the reference against current substrate and writes a `superseded_by` field if the reference's current state falsifies the claim. Cheap, idempotent, runs before any consumer acts. The reconciliation output is the projection; the substrate is ground truth.

**Anchored to:** Foundation [F2](../01_foundations/F2_logic_holds.md) — non-contradiction applied at the reflective-layer boundary: an observation surface paraphrasing or summarizing substrate facts must not present a framing that contradicts the substrate. Also [E1](../01_foundations/E1_corpus_is_hypothesis.md) — every reflective claim is a hypothesis about substrate state that must be falsifiable by re-reading the substrate; a reflective surface with no reconciliation contract is a hypothesis with no error-correction path.

## Why this is the most relevant for agent-governed systems

The principle is general — it applies anywhere a reflective surface (a summary, a status field, a proposal, a ledger entry, a doctrine excerpt) carries claims that reference substrate state.

For agent-governed systems specifically, the highest-leverage application is the **per-proposal reviewer**.

The reviewer reads each proposal in isolation. The proposal's content was drafted at some moment in the past; the reviewer evaluates it at the present moment. Between draft and review, the substrate may have changed: a referenced fact owner was renamed, a referenced invariant test was added, a related proposal was rolled back, the contract the proposal cites was modified. The reviewer has no structural mechanism that surfaces these changes — and so may approve a proposal whose claims have been falsified by recent system state. The artifacts of truth (current state of the substrate) exist but nothing forced the reviewer to consult them.

Applied to a per-proposal reviewer: before the reviewer evaluates, a reconciliation pass checks whether anything in the proposal's stated assumptions has been falsified. The reviewer sees the freshness state alongside the proposal content.

## Seed evidence

In one project, the user's morning briefing surface was assembled from data substrate (ledger entries, code state, recent commits) via an aggregation script that ran nightly. The briefing's claims about the system's state (open ledger items, recent commits, integrity check status) were assembled at the moment the script ran — and the user read the briefing the next morning.

In one observed case, an open ledger item said *"the X subsystem is blocked on Y not yet shipping."* By the time the user read the briefing, Y had shipped (a commit from the early morning). The briefing's claim was stale. The user followed the briefing's recommendation, which assumed Y wasn't yet available — and produced redundant work because the recommended path was no longer the right one.

The framing surfaced a deeper pattern: any reflective surface that assembles claims about substrate state and presents them to a consumer at a later moment is subject to staleness. The fix isn't to make the assembly more frequent (a more-frequent stale claim is still stale); it's to wire a *reconciliation pass at the consumer's decision moment* that resolves the claim against current substrate before the consumer acts.

## The fix shape

Four sibling components:

### 1. Reconciliation pass

A scheduled sweep that runs as part of every reflective-update cycle (briefing refresh, ledger update, status-field render). For each open observation entry whose claim references substrate, the pass:

- Resolves the reference against current substrate (`git rev-parse`, `grep -r`, query the database, check the file's modification time, etc.)
- If the reference's current state falsifies the claim, write a `superseded_by` field on the observation entry with a pointer to the falsifying evidence
- If the claim still holds, no change

Cheap, idempotent, runs before any consumer acts on the entries. The reconciliation output is the *projection*; the substrate is ground truth.

### 2. Decision-surface enrichment

When an observation entry is rendered to a decision-maker (a user reviewing a proposal, a user reading the briefing, an agent consuming a contract), the surface displays the entry's claim *alongside* the current state of every artifact the claim references. Contradictions are visible to the decision-maker before approval, not after.

For a proposal reviewer specifically: the proposal's content is rendered alongside the reconciliation results. If the proposal cites a contract that has changed since the proposal was drafted, the reviewer sees the change inline ("this contract has been modified since the proposal was drafted; check whether the proposal's reasoning still holds").

### 3. Cross-source consistency invariant

A `self_audit`-domain check (analog to the existing System Reviewer Layer 1 patterns) that fires when an open ledger entry's blocking claim does not resolve against current substrate. Surfaces in the daily digest, not as a blocker — the human decides what to reconcile, the framework just makes the drift visible.

### 4. Substrate-change watchdog

A complementary mechanism that watches the substrate for changes that *might* affect open observations, without waiting for the next render cycle. When a commit lands, a config changes, or a fact owner is renamed, the watchdog notes the affected observation surfaces and flags them for re-reconciliation on next render.

## Implementation sketch

```python
# foundation/reflective_freshness.py

from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Optional


@dataclass
class SubstrateReference:
    """A claim's reference to substrate state."""
    reference_type: str       # 'file_exists' | 'commit_sha' | 'config_value' | etc.
    reference_value: str      # the specific thing being referenced
    resolver: Callable        # function(value) → current substrate state


@dataclass
class ReconciliationResult:
    """Output of one reconciliation pass for one entry."""
    entry_id: str
    references_checked: list[SubstrateReference]
    falsifying_references: list[tuple[SubstrateReference, str]]  # (ref, falsification_reason)
    superseded_by: Optional[str] = None


def reconcile_entry(entry: dict, references: list[SubstrateReference]) -> ReconciliationResult:
    """Run the reconciliation pass for one observation entry."""
    falsifying = []
    for ref in references:
        current_state = ref.resolver(ref.reference_value)
        # Project-specific logic for "does current_state falsify the claim?"
        # Examples:
        # - file_exists: claim "file X blocks deployment"; if file X now exists, claim falsified
        # - commit_sha: claim "blocked on commit Y not yet landing"; if Y is now in main, claim falsified
        # - config_value: claim "feature flag Z is off"; if Z is now on, claim falsified
        if _claim_falsified(entry, ref, current_state):
            falsifying.append((ref, _explain_falsification(entry, ref, current_state)))
    return ReconciliationResult(
        entry_id=entry["id"],
        references_checked=references,
        falsifying_references=falsifying,
        superseded_by=_format_superseded(falsifying) if falsifying else None,
    )


def render_with_freshness(entry: dict, references: list[SubstrateReference]) -> str:
    """Render an observation entry alongside its reconciliation result."""
    result = reconcile_entry(entry, references)
    text = entry["claim"]
    if result.falsifying_references:
        text += "\n\n⚠ Substrate check: claim may be stale\n"
        for ref, reason in result.falsifying_references:
            text += f"  - {ref.reference_type}: {reason}\n"
    return text
```

## Why this belongs at the stack layer

Any project bootstrapped from a stack that grows a reflective surface (briefing, ledger, status field, proposal review, summary table) will have the same staleness shape. The bug class is fully determined by *"reflective surface assembled at moment A consumed at moment B with substrate changes between"* — not by what the project does.

Filing at the stack layer means every project that adopts the stack inherits the reconciliation discipline.

## Adopt this in your project

1. Identify your project's reflective surfaces. Common ones: nightly briefings, ledger renderings, status fields that aggregate substrate state, per-proposal review interfaces.

2. For each surface, identify the substrate references the claims rely on. File paths, commit SHAs, config values, contract definitions, etc.

3. Implement the reconciliation pass and the decision-surface enrichment. Start with one surface (the per-proposal reviewer is highest-leverage for agent-governed systems).

4. Wire the cross-source consistency invariant into your System Reviewer Layer 1.

5. Optional: add the substrate-change watchdog for surfaces with high-velocity substrate.

## Elevation status

**Currently staged.** Elevation criteria:

- ✓ Generative force — explains rules about reflective-surface staleness, substrate-as-ground-truth, reconciliation-as-projection
- ✓ Reduction-resistance — derives from F2 + E1 but not from existing stack-layer rules; the meta-principle "artifacts of truth exist; nothing forces consultation" is a generative reformulation that catches a wide bug class
- ✓ Falsifiability — would be falsified by a system where reflective surfaces don't drift from substrate (no such system has been observed; substrate change is the default)
- ⚠ Independent triangulation — one project sighting in deep detail; needs at least one more independent sighting before formal promotion

This is the pattern most likely to benefit any agent-governed system, including PrizmForge-shape projects. If you're building such a system and you adopt this pattern, your project is the second sighting — and the pattern is one step closer to formal elevation.
