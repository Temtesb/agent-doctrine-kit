# Doctrine excerpt — the lessons loop closure

Place this in your governance doc as the section describing how detection-to-prevention compounds.

---

## The lessons loop — detection through prevention

**Derives from:** Foundations [F1](../../01_foundations/F1_time_has_direction.md) (every step is an event, history is preserved), [E1](../../01_foundations/E1_corpus_is_hypothesis.md) (AI drafts are hypotheses; user accept/reject is the verification surface), and the *prefer enforcers over principles* meta-stance ([00_meta_stances/prefer_enforcers_over_principles.md](../../00_meta_stances/prefer_enforcers_over_principles.md)).

The loop:

```
detection (integrity check fires repeatedly within window)
  → lesson_candidate row written (with AI-drafted suggestion)
    → user accepts / rejects / suppresses
      → if accepted: stub generator runs
        → invariant test stub + pattern library entry generated
          → user completes both
            → CI now catches next instance
              → pattern entry surfaces it for the next §pre-flight question 3
```

The loop closes without a human running it manually. Detection and prevention infrastructure compound automatically.

### Why the loop exists

Without the loop, prevention stays flat. The same bug shape gets fixed each time it surfaces, by hand, with no accumulation. The human is the loop — translating raw integrity violations into doctrine, doctrine into tests, tests into prevented bugs. That work is structurally agent-shaped (mechanical detection, pattern matching, draft generation), and forcing the human to do it is a failure of the *division-of-labor pillar*.

With the loop, the agent does the mechanical work and the user does the user-shaped work (deciding whether the pattern is real and what to call it). Each accepted candidate adds one more invariant test to CI, one more entry to the pattern library, and one more pre-flight reference for future changes. Prevention compounds.

### The dual trigger

The detector fires on **either** condition over a rolling window (default 30 days):

- **Distinct checks ≥ 3** — at least three different integrity checks have violated the same governing principle. The "many different checks all finding the same shape" signal is strong evidence of a recurring pattern.
- **Total violations ≥ 100** — a single check has fired 100+ times under the same principle. The "one check, many cases" signal catches patterns where the violation has a high-volume single-shape rather than diverse expressions.

A distinct-only trigger would miss the high-volume single-shape case (a single check firing thousands of times can be one principle's recurring violation, not noise). A volume-only trigger would miss the diverse-expression case (three different checks each firing 5 times reveals the principle is being violated in multiple ways). Both trigger paths catch a different shape; using both is the structural answer.

### The AI drafter — failure-tolerant

When a `lesson_candidates` row is created, an AI call drafts `suggested_invariant` and `suggested_doctrine_update`. The prompt includes the governing principle, the distinct check IDs, and a sample of the violations.

**Failure-tolerant by design.** On any AI failure (rate limit, parse error, malformed response, no API key), the fields remain NULL and candidate creation is never blocked. The user can still accept the candidate and write the suggestion manually.

Per [E1](../../01_foundations/E1_corpus_is_hypothesis.md): the AI's drafts are hypotheses, not authority. The user's accept/reject is the verification surface. Even when the drafts are populated, the user's decision is what makes them load-bearing.

### The decision surface

`pending` candidates surface in the user's decision queue (a UI tab, a markdown ledger, whatever your project uses). The user reads the principle, the snapshot of violations, the AI-drafted suggestion, and decides:

- **Accept** — pattern is real; suggestion is roughly right; route to stub generator
- **Reject** — pattern isn't real OR isn't worth enforcing; record reason; close candidate
- **Suppress** — real pattern but the failure mode is acceptable in this project's context; close candidate with explicit suppression rationale
- **Duplicate** — pattern overlaps with an earlier candidate; reference that one; close

Each decision writes `decided_at + decided_by + decision_notes + status`. The status transition is the audit (per F1, the column writes themselves are the event — no separate fact_corrections row needed; this is the exception the [02_audit_as_shape/](../../02_audit_as_shape/) enforcer's `_KNOWN_ALLOWED` set allows).

### The stub generator

On `accepted` candidates, a generator runs (manually triggered or scheduled). For each accepted-but-not-yet-generated candidate it produces two artifacts:

- A draft invariant test file (e.g., `tests/test_arch_invariants_candidate_N.py`) using the ratchet pattern from [04_pre_flight_and_invariants/enforcer/_known_allowed_ratchet_template.py](../../04_pre_flight_and_invariants/enforcer/_known_allowed_ratchet_template.py). The candidate's `suggested_invariant` text is the seed for the test's docstring and detection logic.
- An entry in the project's `PATTERNS.md` with a stable `P00N` anchor, the governing principle, the bug shape, the fix shape, and a cross-reference to the invariant test file.

The candidate row is updated atomically with `invariant_test_path` and `pattern_library_entry`, so the generator stays idempotent — running it again won't regenerate the same candidate's stub.

**The user reviews both artifacts and commits them.** The generator produces drafts; the user is the final reviewer (the draft might capture the pattern imperfectly; the user has the domain knowledge to refine). This is the second verification surface — the first was at candidate-accept, the second is at artifact-commit.

### What's still NOT in the loop

The loop closes the *recurrence detection → prevention* cycle. It doesn't close:

- **Novelty detection.** A single instance of a new bug shape doesn't trigger a candidate — the dual trigger requires recurrence. Single-instance bugs still get fixed individually, and the dual trigger picks them up only if they recur.
- **Cross-project elevation.** A pattern accepted at the project layer doesn't automatically promote to the stack or universal layer. The elevation protocol ([09_elevation_protocol/](../../09_elevation_protocol/)) is the separate mechanism that handles that — it requires cross-project evidence (multiple independent projects surfacing the same shape).
- **Doctrine revision.** An accepted candidate may suggest a doctrine update (`suggested_doctrine_update` field). The user can incorporate the suggestion into the governance doc, but the loop doesn't auto-edit doctrine. Doctrine changes are user-required per [03_classifier_and_audit_lane/](../../03_classifier_and_audit_lane/) doctrine.

These deliberate non-closures preserve the user's judgment on the decisions that need it.
