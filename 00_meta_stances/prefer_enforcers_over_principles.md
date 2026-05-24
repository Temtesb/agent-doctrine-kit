# Prefer enforcers over principles

## The principle

> A principle in a doc says "you're supposed to remember this." An enforcer is code that fails at write, build, or run time if violated. Schema constraint, decorator, pre-commit hook, contract test, lint rule, runtime assertion, integrity check. Every lesson that lands should be evaluated for enforcer potential. Principles are the fallback for things that genuinely cannot be enforced (judgment, taste, social context).

**Derives from:** Foundation E2 (convergence is evidence of triangulation, not proof of truth) — convergence on a documented principle is necessary but not sufficient evidence that the principle is honored at runtime; an enforcer is the structural mechanism that closes the gap between belief and verification.

## Why this matters for agent-governed systems

In a system where AI agents are the primary actors reading and writing code, principles are weaker than they are in a human-only system. A human reading a principle has natural skepticism, situational awareness, and the ability to flag "this rule doesn't fit here." An AI agent following a principle may follow it more rigidly when it fits AND fail to apply it when the situation calls for adaptation. Either way, the principle's correctness is *not the agent's responsibility* — it is the system's job to make principles structural, not memorized.

Concretely:

- A principle that says *"every UPDATE on a meaningful column writes to an audit table"* is a hope.
- An invariant test that fails CI on any function that UPDATEs a meaningful column without a paired INSERT into an audit table is a guarantee.
- The test does what the principle wishes to do. The principle's job is then to explain *why* the test exists, not to enforce the rule on its own.

## The hierarchy of enforcement strength

From strongest to weakest:

1. **Type system / schema constraint** — invalid state cannot exist. A `CHECK(status IN ('open', 'closed', 'voided'))` rejects bad rows at write time.
2. **Pre-commit hook / lint rule** — invalid state cannot enter the codebase. A pre-commit hook that rejects `print(` statements catches them before they reach review.
3. **CI test / contract test** — invalid state cannot ship. An invariant test that fails on `git push` blocks the merge.
4. **Runtime assertion / integrity check** — invalid state is detected and surfaced. Drift gets noticed by the system, not by users.
5. **Decorator / wrapper** — invalid use of an API is rejected at call time. `@handle_errors` ensures every endpoint returns the canonical response shape.
6. **Code review / human reviewer** — invalid state is caught by judgment. Necessary for things tests can't catch; weaker than tests because reviewers are inconsistent.
7. **Principle in a doc** — invalid state is hopefully remembered. The fallback. Used when the gap between principle and enforcer can't yet be closed.

The discipline is: **for every principle you write, ask which level of enforcement it could move to.** Most principles can move up at least one level. Some can move several.

## When principles are the right answer

Genuinely cannot be enforced:

- **Judgment calls** — "the right scope for this PR" can't be encoded. A reviewer's read is irreducible.
- **Taste** — "this naming is clearer than that one" is principle-shaped; the most you can do is establish conventions and rely on review.
- **Social context** — "respect the user's stated preference for terse responses" depends on reading the user, not the code.
- **Cross-cutting concerns the codebase doesn't observe** — "consider the customer experience" applies to choices the system can't see.

Even here, you can sometimes push *part* of the principle into structure: lint the naming convention even if you can't lint the clarity; surface the user's preference in a header that handlers must check; instrument the customer-experience-affecting paths so the data shape exposes the choice.

## How to adopt this stance

1. **Audit existing principles.** Walk your doctrine doc. For each rule, ask: "what enforcer could replace this?" Most will have an answer that's higher-strength than the current principle.

2. **For new principles, write the enforcer first.** When you discover a rule, the default question is *"what test, decorator, or check encodes this?"* not *"where do I document this?"* Documentation comes after the enforcer, citing it.

3. **Track the gap.** Some principles will remain principles for a while because the enforcer isn't yet invented. Track those as candidates — when a recurring failure surfaces, that's evidence the enforcer is now possible (see [05_lessons_loop/](../05_lessons_loop/)).

4. **The ratchet pattern lets you adopt enforcers incrementally.** A new invariant test doesn't need to start at zero violations — it can baseline current state in a `_KNOWN_ALLOWED` set, block additions, and ratchet down on fixes. See [04_pre_flight_and_invariants/enforcer/_known_allowed_ratchet_template.py](../04_pre_flight_and_invariants/enforcer/_known_allowed_ratchet_template.py).

## Cross-references

- [patterns_local_enforcers_home.md](patterns_local_enforcers_home.md) — the companion principle about where enforcers live.
- [hypothesis_posture.md](hypothesis_posture.md) — the paired stance for the other half of the principle/enforcement gap (the doctrine-vs-reality gap).
- [10_followups_patterns/](../10_followups_patterns/) — three worked enforcers ready to lift into a project.
