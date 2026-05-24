# 07 — The two-layer System Reviewer

## The concept

> A reviewer that audits *the whole system*, distinct from any per-proposal reviewer. Layer 1 is fast deterministic CI checks: migration completeness, contract coverage, module health, doc-code alignment. Layer 2 is judgment-requiring AI architectural review: does the big picture still hang together; what's drifting; what's the next thing to add.

**Derives from:** Foundation [E2](../01_foundations/E2_convergence_is_triangulation.md) (the system's belief that it is consistent with its own doctrine is exactly the kind of belief that cannot be self-validated; two-layer triangulation is the structural form). Also [E1](../01_foundations/E1_corpus_is_hypothesis.md) (the reviewer's findings are evidence that the project's working hypotheses are still working; absence of findings is informative but not conclusive).

## Why this matters for agent-governed systems

In a system where agents propose changes and a per-proposal reviewer evaluates each change, there's still a failure mode the per-proposal reviewer cannot catch: **slow accumulation of architectural drift across many individually-approved changes**.

Each proposal might be locally fine. The reviewer approves it. The next proposal is also locally fine; approved. After fifty proposals, no individual change was bad, but the codebase has drifted — modules are accumulating responsibilities outside their declared scope; contracts that were declared at session 3 no longer match reality; a subsystem that was supposed to be the audit trail has become a junk drawer.

The System Reviewer is the second layer that catches this drift. It runs periodically (daily Layer 1, weekly/on-demand Layer 2) and asks *"does the big picture still hang together?"* — a question no per-proposal reviewer is positioned to ask.

For agent-governed systems specifically, this matters more than for human-only systems. Agents propose more changes per unit time than humans; the accumulation rate is higher; the per-proposal review can keep up but doesn't have the lookback span to notice multi-proposal drift. The System Reviewer's distinct cadence and distinct scope is what closes this gap.

## What's in this directory

| File | Purpose |
|---|---|
| [doctrine/two_layers.md](doctrine/two_layers.md) | The two-layer design — what Layer 1 (deterministic) checks; what Layer 2 (AI architectural review) evaluates; how they compose. |
| [code/layer1_self_audit_signature.py](code/layer1_self_audit_signature.py) | The interface for Layer 1 — function signatures for the deterministic checks, with worked examples. |

Layer 2 is described in the doctrine but not implemented as code here — the implementation is project-specific (depends on which AI client your project uses, what doctrine you have to feed it, what module map your code exposes).

## How to adopt

1. **Copy the doctrine** ([doctrine/two_layers.md](doctrine/two_layers.md)) into your governance doc. Adapt the example check categories to your project's structure.

2. **Implement Layer 1 incrementally.** Start with two or three of the highest-value checks from the signature file:
   - Migration completeness (file count vs. declared schema version)
   - Contract coverage (% of tables with fact_owners declarations)
   - Module health (file line counts vs. soft/hard limits)
   - Doc-code alignment (governance doc references files that still exist)

   Wire them into CI. Each check returns a structured `CheckResult` with pass/fail + remediation guidance.

3. **Build Layer 2 when Layer 1 has enough coverage.** Layer 2 is an AI call that consumes the governance docs, the module map, recent git history, and Layer 1's results. It produces a narrative report (under 500 words) with architectural findings and recommendations.

4. **Set the cadence.**
   - Layer 1: every CI run (fast)
   - Layer 2: weekly or per-milestone, plus on-demand via `./manage.py review` (or your equivalent)
   - Pre-push hook (optional): Layer 1 only, blocks push on failures; Layer 2 logged as advisory

5. **Wire Layer 2 findings to the lesson loop.** When Layer 2 surfaces a pattern that recurs across multiple proposals, it's a candidate for a `lesson_candidate` entry — the same loop closure from [05_lessons_loop/](../05_lessons_loop/) handles it.

## Layer 1 vs. Layer 2 — different scope, different cadence

**Layer 1 (deterministic):**

- Fast (runs in CI, sub-second to seconds)
- Mechanical (regex, AST walking, SQL queries)
- Binary results (pass/fail with specific remediation)
- Catches mechanical drift that automated checks can detect
- Examples: missing migration, file over hard limit, contract references a function that no longer exists

**Layer 2 (judgment):**

- Slow (AI call, costs tokens, runs occasionally)
- Conceptual (modules accumulating responsibilities; subsystems coupling unintentionally; doc-code semantic drift)
- Narrative results (a short report, not a checkbox list)
- Catches conceptual drift that requires judgment from a perspective that doesn't already share the project's framing
- Examples: a handler module is now doing three things its docstring doesn't mention; a fact owner declared at session 3 is actually computed in two places now; the integrity check coverage has plateaued at the same domains for months

The two layers are independent. Either can find what the other misses. Layer 1 catches what mechanical analysis can find; Layer 2 catches what mechanical analysis cannot. Both are needed.

## Tensions to name explicitly

1. **Layer 2 is AI-dependent.** Per [11_ai_dependency_tracking/](../11_ai_dependency_tracking/), Layer 2's outputs depend on the model it uses. Different models produce different architectural readings of the same module map. Cross-model corroboration (running the same Layer 2 review through two models and surfacing only consistent findings) is the strongest evidence form per E2, but adds cost.

2. **Layer 1 vs. invariant tests overlap.** Both are deterministic CI checks. The distinction is *scope*: invariant tests ([04_pre_flight_and_invariants/](../04_pre_flight_and_invariants/)) check *patterns within code* (this function violates this rule); Layer 1 checks *patterns across the codebase* (this contract has zero coverage; this module exceeds size limit). The overlap is intentional — Layer 1 is the meta-level check that's useful when invariant-level checks miss the bigger picture.

3. **Layer 2 reports can be noisy.** An AI architectural review surfaces things that aren't problems alongside things that are. The user's role is to triage; the System Reviewer's role is to surface, not to decide. Don't auto-act on Layer 2 findings; route them to the user's queue with the AI-drafted summary attached.

## Cross-references

- [04_pre_flight_and_invariants/](../04_pre_flight_and_invariants/) — invariant tests are the pattern-level CI checks; Layer 1 is the system-level CI checks.
- [05_lessons_loop/](../05_lessons_loop/) — Layer 2 findings can feed the lesson loop when they identify recurring shapes.
- [08_data_contracts/](../08_data_contracts/) — Layer 1's "contract coverage" check measures what % of tables have fact_owners declarations; the contracts themselves live in this concept directory.
- [11_ai_dependency_tracking/](../11_ai_dependency_tracking/) — Layer 2 is AI-dependent and needs an AI-dependency note.
