# The hypothesis posture

## The principle

> Every rule in the corpus is the current best understanding, anchored to a stated reason, subject to revision when something deeper is discovered, when the rule's falsification condition is demonstrated, or when cross-project evidence reveals it was domain-specific. The corpus is not a list of true things; it is the set of working hypotheses under which the system currently operates.

**Derives from:** Foundation E1 (the corpus is a hypothesis, not an authority).

## Why this matters more under AI authorship

From the AI-dependency note on E1:

> This foundation matters more under AI authorship than under human-only authorship. An AI consuming an authority-shaped doc may follow it more rigidly than a human would; the hypothesis posture is the structural hedge against that.

A human reading a doctrine that says *"always do X"* has natural skepticism. They notice when the rule doesn't fit. They push back. They ask the doctrine's author *"are you sure?"* before deferring.

An AI agent reading the same doctrine may follow it more literally — especially in ambiguous cases where a human would pause and a model defaults to compliance. If the doctrine is authority-shaped (rules stated without falsification conditions, without anchor history, without acknowledgment of uncertainty), the agent has no structural cue that the rule might be wrong, stale, or misapplied. Rigid compliance with stale rules is the failure mode.

The hypothesis posture is the structural hedge:

- Every rule declares **what would prove it wrong** (a falsification condition), so the reading agent can pressure-test the rule against current state rather than just defer to it
- Every rule declares its **anchor history** — when it was added, why, what triggered any subsequent re-anchoring — so the reading agent can see the rule as a temporal artifact rather than an eternal one
- Every rule with AI-behavior dependencies declares them (see [11_ai_dependency_tracking/](../11_ai_dependency_tracking/)), so when models change the dependent rules get flagged for review

The discipline reshapes how doctrine reads. Instead of *"this is how things are"*, it reads *"this is the current best derivation from the foundation it cites; here's what would change it."* The reading agent receives the rule with the same posture the writing agent (or human) held when they wrote it.

## What changes in how doctrine entries are written

Old shape (authority):

> **Rule:** All UPDATEs on meaningful business columns must write a fact_corrections row in the same transaction.

New shape (hypothesis):

> **Rule:** All UPDATEs on meaningful business columns must write a fact_corrections row in the same transaction.
>
> **Derives from:** Foundation F1 (time has direction) applied to data mutation. History must answer "what was true at time T"; overwriting a meaningful column without recording the prior value erases the answer.
>
> **Falsification condition:** A scheme that preserves prior values *without* a paired audit row — e.g., a temporal database that automatically versions every column. Under such a scheme, the explicit fact_corrections row is redundant. We do not currently operate on such a scheme; if the project adopts one, this rule is candidate for revision.
>
> **Anchor history:** 2026-05-05 — added after a session that surfaced 88-of-89 inventory rows with category_id silently overwritten by AI guesses with no audit. Triggered by recognition that the no-overwrite principle had been articulated but not enforced.

The new shape is longer but it serves three functions the old shape doesn't:

1. **It tells the reading agent how to think about the rule.** The derivation says "this is not arbitrary; here's the foundation it implements." The agent can verify the derivation still holds rather than defer blindly.

2. **It tells the reading agent what would change the rule.** The falsification condition surfaces the conditions of the rule's possible failure. Agents (and humans) confronting an edge case can ask *"are we in the falsification condition?"* and route accordingly.

3. **It tells the reading agent the rule is a temporal artifact.** The anchor history shows when the rule was added and why. A rule added in 2026 may not fit a 2028 system; the history makes the timeline visible.

## How to adopt this stance

1. **Add three fields to every operational rule in your doctrine:** Derives-from, Falsification condition, Anchor history. The structure mirrors the six-field foundation structure (see [01_foundations/](../01_foundations/) for examples).

2. **For existing doctrine, retrofit the fields gradually.** A doctrine doc with 50 rules doesn't need all 50 retrofitted before the discipline takes effect — just the ones that change. New rules ship with the fields; old rules get the fields when they're revised.

3. **Surface the posture in your top-level governance doc.** Newcomers (human or AI) should see "this is a hypothesis-shaped corpus, not authority" before they read a single rule. The framing primes the reading.

4. **Wire AI-dependency tracking** (see [11_ai_dependency_tracking/](../11_ai_dependency_tracking/)). Rules whose correctness depends on a specific AI's behavior get a dedicated note declaring the dependency. Model upgrades trigger re-validation of those rules.

5. **Pair the posture with the elevation protocol** (see [09_elevation_protocol/](../09_elevation_protocol/)). The protocol describes when a rule should be revised, demoted, or promoted based on evidence. The hypothesis posture is the *stance*; the protocol is the *operation*.

## What this stance does NOT mean

- **It does NOT mean every rule is up for debate every day.** Hypothesis-shaped rules are still followed; the structural hedge is for the cases where the rule turns out to be wrong, stale, or misapplied. Agents follow doctrine; the posture changes *how* they follow.

- **It does NOT mean weak rules are okay.** A rule with a vague falsification condition is itself suspect — the hedge is for genuinely-strong rules whose strength must remain visible to the reader.

- **It does NOT mean documentation is optional.** The doctrine is the corpus; the posture is *how* the corpus is held, not whether it exists. Skipping documentation because "everything's a hypothesis anyway" is the wrong reading.

## Cross-references

- [01_foundations/](../01_foundations/) — the universal-layer doctrine, written with the full six-field structure as the worked example of the posture.
- [11_ai_dependency_tracking/](../11_ai_dependency_tracking/) — the cross-cutting discipline that closes the silent-model-upgrade gap.
- [09_elevation_protocol/](../09_elevation_protocol/) — the operational protocol for revising, promoting, or demoting rules based on evidence.
