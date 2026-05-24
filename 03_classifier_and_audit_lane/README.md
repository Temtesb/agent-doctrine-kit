# 03 — Classifier + audit lane + trust ratchet

## The concept

> Three coupled mechanisms that together implement adaptive routing without abandoning safety: a four-criteria classifier decides which findings the agent can resolve under doctrine vs. which need human judgment; an append-only `auto_resolutions` audit lane records every agent-resolved finding with its outcome; a trust ratchet keyed on *change shape* (not actor) decides which shapes have earned reduced surfacing.

**Derives from:** Foundations [F1](../01_foundations/F1_time_has_direction.md) (audit lane append-only), [F2](../01_foundations/F2_logic_holds.md) (single classifier output per finding), [E2](../01_foundations/E2_convergence_is_triangulation.md) (trust ratchet as structural convergence-counting across N independent successful resolutions).

## Why this matters for agent-governed systems

Every uniform-gate system eventually hits the reviewer-bottleneck failure mode: review becomes the rate limiter, OR the reviewer rubber-stamps to keep up, OR both. The classifier-and-ratchet pattern solves this without giving up safety:

- **Trivial mechanical changes that doctrine clearly resolves get routed to the agent lane.** They land with an audit row; the user sees a digest, not item-by-item approvals.
- **Judgment calls — taxonomy, calibration, business priority, irreversible actions — route to user.** No automation pressure on the decisions that genuinely need human input.
- **Trust accumulates by change shape, not by agent.** The same agent making a soft-void cleanup vs. a money-changing edit shouldn't get one trust number. Per-shape trust lets the system safely accelerate on well-understood shapes while still gating novel ones.
- **The audit lane is the substrate.** Every classification decision and every outcome is recorded. The trust ratchet reads the audit lane to recalibrate. Rolled-back resolutions decay trust on that shape.

For agent-governed systems specifically, this addresses a real failure mode that the project's review surface might not anticipate: the *count-based rail* problem. A queue cap on pending reviews fires on every accumulation, including accumulation of mechanical work the user shouldn't have to approve. Routing mechanical work to the audit lane keeps the queue meaningful — it surfaces only what genuinely needs judgment.

## What's in this directory

| File | Purpose |
|---|---|
| [schema/auto_resolutions.sql](schema/auto_resolutions.sql) | The append-only audit lane. Records every agent-resolved finding with its outcome. |
| [doctrine/four_criteria.md](doctrine/four_criteria.md) | The classifier's four-criteria gate, the user-required triggers, and the boundary defaults. |
| [code/classifier_predicates.py](code/classifier_predicates.py) | A worked Python implementation of the classifier predicates over finding text and metadata. |

The trust ratchet is implementation-flexible enough that it lives as algorithm description in the doctrine file rather than as code; once you've adopted the schema and the classifier, the ratchet is a query over `auto_resolutions`.

## How to adopt

1. **Copy the schema** ([schema/auto_resolutions.sql](schema/auto_resolutions.sql)) into your migrations directory. The schema is project-agnostic; you only need to adapt the `finding_source_type` CHECK to your project's finding sources.

2. **Copy the doctrine** ([doctrine/four_criteria.md](doctrine/four_criteria.md)) into your governance doc. The doctrine references "your doctrine" generically; adapt to point at the doctrine sections that actually exist in your project.

3. **Copy the classifier** ([code/classifier_predicates.py](code/classifier_predicates.py)) into your handlers. Adapt:
   - The `_RESOLVABLE_SHAPES` regex set to match the kinds of findings your system produces
   - The `_USER_REQUIRED_TRIGGERS` regex set to match the kinds of findings that should never auto-resolve
   - The `_HIGH_STAKES_PATTERNS` regex set for irreversible-action detection specific to your domain

4. **Wire the audit lane writer.** When the agent acts on an agent-resolvable finding, the action concludes by writing one `auto_resolutions` row with the change summary, commit SHA, tests-passed-before/after, governing principle, and which criteria matched. This is single-step at the agent's commit moment; don't defer it.

5. **Wire the rollback hook.** A `post-revert` git hook (or equivalent) populates `rolled_back_at + rollback_reason` when the user reverts a commit recorded in `auto_resolutions`. This is the single permitted mutation; everything else is append-only.

6. **Build the trust ratchet as a scheduled query.** Daily aggregation over `auto_resolutions` grouped by fingerprint of `(finding_source_type, governing_principle, change_pattern)` produces per-shape accepted/reverted counts. Shapes meeting the trust criteria (accepted ≥ N, reverts = 0) skip the daily digest until a new revert event resets them.

7. **Surface the daily digest.** A small writeup appended to your morning briefing (or equivalent) lists agent-resolved findings from the past 24 hours. One line per resolution: source, change summary, commit reference, governing principle. The user scans, doesn't approve item-by-item. Anything that looks wrong gets reverted; the post-revert hook handles the trust impact.

## Tensions to name explicitly

1. **The classifier presumes the system has doctrine to consult.** Without [01_foundations/](../01_foundations/) and project-layer doctrine, criterion 1 (*"doctrine names the answer"*) is always false and everything routes to manual review. The classifier amplifies whatever doctrine exists; it doesn't create doctrine.

2. **The trust ratchet assumes the user reverts when the agent is wrong.** If your project has another error-catching mechanism (a proposal-time reviewer that catches errors before merge), that's a different signal than user-revert-after-merge — and may need a different ratchet calibration. *"Reviewer-rejected"* and *"user-reverted-after-merge"* are both negative signals but carry different evidence weight.

3. **Bootstrap conservatism.** During the first ~5-10 entries in `auto_resolutions`, no shape will have enough volume to earn the trust ratchet. Default behavior: every resolution appears in the daily digest, no per-shape suppression. The ratchet ships only after enough data accumulates to calibrate against. Building it earlier produces calibration with no signal in it.

## Cross-references

- [02_audit_as_shape/](../02_audit_as_shape/) — `auto_resolutions` is a sibling audit table to `fact_corrections`; both are append-only-per-F1 with the only-permitted-mutation being a lifecycle pair.
- [04_pre_flight_and_invariants/](../04_pre_flight_and_invariants/) — the design-time pre-flight + architecture invariant tests are the upstream filter that catches bad changes before they ever reach the classifier.
- [05_lessons_loop/](../05_lessons_loop/) — `lesson_candidates` is one of the four finding-source types the classifier handles.
- [07_system_reviewer/](../07_system_reviewer/) — the System Reviewer's Layer 2 audits whether the classifier's calibration is still appropriate.
- [11_ai_dependency_tracking/](../11_ai_dependency_tracking/) — the classifier itself is AI-dependent (criterion 1 is an AI judgment); model upgrades decay trust on AI-dependent shapes pending re-validation.
