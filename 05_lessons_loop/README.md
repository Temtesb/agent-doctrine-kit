# 05 — Lessons loop

## The concept

> A closed loop from detection through prevention: integrity checks detect repeated violation patterns → a `lesson_candidates` row is written → AI drafts a suggested invariant and doctrine update → user accepts/rejects → if accepted, a stub generator emits a draft invariant test and a pattern library entry → user completes both → CI now prevents the next instance of the bug shape. The loop closes without a human running it manually.

**Derives from:** Foundations [F1](../01_foundations/F1_time_has_direction.md) (every step in the loop is an event with a timestamp; the loop's history is preserved) and [E1](../01_foundations/E1_corpus_is_hypothesis.md) (AI drafts are hypotheses; the user's accept/reject is the verification surface).

## Why this matters for agent-governed systems

Without the lessons loop, prevention infrastructure stays flat. Each bug gets fixed once; the next instance of the same bug shape arrives in another part of the codebase (or another session) and gets fixed again, by hand, with no learning. The human is the loop — translating raw violations into principles, principles into tests, tests into prevented bugs.

With the lessons loop, prevention compounds. Detection → candidate → user-accept → invariant test → CI catches the next instance. The agent does the mechanical work (detecting the recurrence, drafting the suggestion, generating the stub); the user does the user-shaped work (deciding whether the pattern is real and what to call it). This is the structural form of the *division-of-labor pillar* — the human does what only the human can do, the agent does what the agent is genuinely faster at.

For agent-governed systems specifically, the loop is what prevents the same bug shape from being re-discovered in every project the agents touch. When the loop is wired at the stack layer (per [09_elevation_protocol/](../09_elevation_protocol/)), a lesson accepted in one project becomes a CI test in every project that adopts the stack — including ones the original lesson never touched.

## What's in this directory

| File | Purpose |
|---|---|
| [schema/lesson_candidates.sql](schema/lesson_candidates.sql) | The append-only candidate table. Each row records a detected pattern with the AI-drafted suggestions and the user's eventual decision. |
| [doctrine/loop_closure.md](doctrine/loop_closure.md) | The principle explaining how the loop closes — detection → candidate → decision → stub → test → prevention. |
| [code/stub_generator_signature.py](code/stub_generator_signature.py) | The interface the stub generator implements. When a candidate is accepted, this is the API that produces the draft invariant test and pattern library entry. |

## How to adopt

1. **Copy the schema** ([schema/lesson_candidates.sql](schema/lesson_candidates.sql)) into your migrations directory. The schema is project-agnostic.

2. **Copy the doctrine** ([doctrine/loop_closure.md](doctrine/loop_closure.md)) into your governance doc. Adapt the doctrine pointers and the lesson-detection mechanism references to your project.

3. **Wire the detection layer.** Your integrity check framework (per [10_followups_patterns/](../10_followups_patterns/) or your existing checks) needs to detect *repeated* violations — e.g., the same check firing N times within a rolling window. When it does, write a `lesson_candidates` row.

4. **Wire the AI drafter.** When a `lesson_candidates` row is created, run an AI call to draft `suggested_invariant` and `suggested_doctrine_update`. Failure-tolerant: on AI failure (rate limit, parse error, no key), leave the fields NULL. The user can write the suggestion manually if needed. The candidate row's existence is the load-bearing thing; the AI drafts are convenience.

5. **Wire the user decision surface.** Whatever decision queue your project uses (a UI tab, a markdown ledger, a Slack channel), surface pending `lesson_candidates` rows for user accept/reject/edit. The user's decision writes `decided_at + decided_by + decision_notes + status`.

6. **Wire the stub generator** (see [code/stub_generator_signature.py](code/stub_generator_signature.py) for the interface). On `accepted` decisions, the generator produces a draft invariant test file and a draft pattern library entry. The user reviews and commits both.

7. **Loop closure verification.** When the generator produces a stub, set `invariant_test_path` and `pattern_library_entry` on the candidate row. These act as the cross-references — the candidate points at its artifacts, the artifacts point back at the candidate as their source.

## The candidate-lifecycle pattern

A `lesson_candidates` row is structurally similar to other agent-output-as-hypothesis patterns (see [02_audit_as_shape/](../02_audit_as_shape/) decision-trigger for the parent shape):

- The AI's `suggested_invariant` and `suggested_doctrine_update` are the *AI's hypothesis*
- The user's accept/reject is the *verification surface*
- The user's decision writes a lifecycle transition with `decided_at + decided_by`
- Accepted candidates become artifacts (invariant test + pattern entry); rejected candidates stay in the table as a record of the pattern *and* the reason for rejection

This avoids the AI-output-as-fact failure mode where AI drafts get adopted without user verification. The candidate row IS the AI's hypothesis; the artifact (the actual invariant test) is what lands in CI only after the user has reviewed and accepted.

## Cross-references

- [02_audit_as_shape/](../02_audit_as_shape/) — the parent pattern (AI output routes through audit/candidate tables before promotion).
- [03_classifier_and_audit_lane/](../03_classifier_and_audit_lane/) — `lesson_candidate` is one of the four finding source types the classifier handles. Most lesson candidates route to user (because criterion 1 requires doctrine to already name the answer; if the candidate is *about* extending doctrine, that's a user-required taxonomy decision).
- [04_pre_flight_and_invariants/](../04_pre_flight_and_invariants/) — the generator's output is a new invariant test file using the ratchet pattern.
- [06_patterns_and_dissonance/](../06_patterns_and_dissonance/) — the generator's other output is a new entry in the pattern library.
- [07_system_reviewer/](../07_system_reviewer/) — the System Reviewer's Layer 1 can detect that no new lesson_candidates have been created in N days (a signal that detection might be silent rather than that nothing's drifting).
