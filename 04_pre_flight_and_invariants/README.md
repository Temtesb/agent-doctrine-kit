# 04 — Pre-flight + invariants

## The concept

> Two enforcers operating at different points in the change lifecycle. The **design-time pre-flight** is five questions the agent answers before any non-trivial change; it catches violations before they enter the code. The **architecture invariant tests** are structural CI assertions; they catch violations before they ship. Together they're independent layers covering different failure modes.

**Derives from:** Foundations [F2](../01_foundations/F2_logic_holds.md) (the test surface and the principles can't contradict the doctrine at the file-system level) and [E2](../01_foundations/E2_convergence_is_triangulation.md) (multi-layered enforcement is structural triangulation; one layer is one perspective, two are two).

## Why this matters for agent-governed systems

A single-layer governance system has one failure mode: when that layer's coverage misses, the bug ships. If your system governs solely by reviewer-at-merge-time, a clever proposal can social-engineer the reviewer; an off-distribution proposal can pass review by being unprecedented; a reviewer can have a bad day.

The pre-flight + invariant pair gives you two independent layers:

- **The pre-flight catches design-time violations.** Before the agent writes the first line of code, it answers questions that surface doctrine violations *in the design* — not just in the implementation. A change that can't articulate which foundation it derives from is suspect at the design stage; you don't need to write the code to know that.

- **The invariant tests catch structural violations at CI time.** Even if the design passes the pre-flight, the implementation might drift. The invariant tests fail CI on any structural pattern that violates doctrine — `UPDATE` without audit, computed value without `_as_of`, AI output written directly to a business column, etc.

Both layers are essential. Pre-flight without invariants relies on the agent's discipline; invariants without pre-flight catches violations late (after the code is written and the rework is expensive).

## What's in this directory

| File | Purpose |
|---|---|
| [doctrine/five_questions.md](doctrine/five_questions.md) | The five questions the agent answers before any non-trivial change. Goes in your governance doc as the pre-flight section. |
| [enforcer/_known_allowed_ratchet_template.py](enforcer/_known_allowed_ratchet_template.py) | The ratchet pattern as a working template, with detailed comments on how to adapt it to a new invariant. |

Multiple invariant tests live in [02_audit_as_shape/](../02_audit_as_shape/) and other concept directories. This directory is the **pattern documentation** — the meta-pattern that all invariant tests follow — rather than a list of invariants. The list grows project-by-project as accepted lesson candidates produce new invariant tests through the loop closure in [05_lessons_loop/](../05_lessons_loop/).

## How to adopt

1. **Copy the five questions** ([doctrine/five_questions.md](doctrine/five_questions.md)) into your governance doc. Place it as a section the agent reads at session start. The questions are framed as actions the agent takes; the doctrine entry explains what each question catches.

2. **Adopt the ratchet pattern for your first invariant.** Pick the highest-value invariant for your project (usually [02_audit_as_shape/](../02_audit_as_shape/)'s `TestUpdateRequiresFactCorrection`). Copy the test file. Adapt to your project. Run it. Add legitimate exceptions to `_KNOWN_ALLOWED` with inline justifications. Commit the baseline.

3. **Add invariants incrementally.** New invariants enter the test file via the lesson-loop closure: when a lesson candidate is accepted, [05_lessons_loop/](../05_lessons_loop/)'s stub generator produces a draft invariant test. The user reviews and completes the stub; the test enters CI; the loop closes.

4. **Wire the pre-flight into your agent's session-start protocol.** When the agent starts a session and the work isn't trivial, it answers the five questions before writing code. The answers go in a session log, commit message, or PR description. The point isn't paperwork; it's that *the act of answering* catches violations.

5. **The pre-flight is a principle; the invariant tests are enforcers.** Per the meta-stance [prefer enforcers over principles](../00_meta_stances/prefer_enforcers_over_principles.md), prioritize moving each pre-flight question into a structural enforcer where possible. Question 2 ("what's the audit trail?") has an enforcer ([02_audit_as_shape/](../02_audit_as_shape/) test). Question 3 ("what pattern does this resemble?") has an enforcer (the pattern library + the lesson loop). Other questions remain principles until enforcers are invented.

## The ratchet pattern explained

The `_KNOWN_ALLOWED` ratchet is the structural answer to *"how do I add a strict invariant when current code already has many legitimate or deferred violations?"*

Three properties:

1. **Baseline current state.** Run the test. Every current violation gets an entry in `_KNOWN_ALLOWED` with an inline justification — either LEGITIMATE (the violation is actually correct under doctrine; the test's pattern is too broad) or DEFERRED (the violation is real and tracked for future cleanup).

2. **Block additions.** New code that violates the invariant fails CI immediately. Adding to `_KNOWN_ALLOWED` requires a code review explaining why the exception is justified — exactly the right friction for a regression.

3. **Ratchet down on fixes.** Removing an entry from `_KNOWN_ALLOWED` is the structural form of "we fixed it." The baseline can only shrink, never grow. Over time, the allow-list approaches empty or stabilizes at only LEGITIMATE entries.

This pattern is what makes invariant tests adoptable without forcing a big-bang cleanup before the test can ship. Without the ratchet, you'd have to fix every existing violation before adding the test — which is rarely feasible — and the test gets deferred indefinitely.

## Cross-references

- [00_meta_stances/prefer_enforcers_over_principles.md](../00_meta_stances/prefer_enforcers_over_principles.md) — the meta-stance that anchors the "invariants are stronger than principles" argument.
- [02_audit_as_shape/enforcer/test_update_requires_fact_correction.py](../02_audit_as_shape/enforcer/test_update_requires_fact_correction.py) — the worked example using the ratchet pattern.
- [05_lessons_loop/](../05_lessons_loop/) — the loop closure where accepted lesson candidates generate new invariant test stubs.
- [06_patterns_and_dissonance/](../06_patterns_and_dissonance/) — the project's pattern library is what the third pre-flight question consults.
- [10_followups_patterns/](../10_followups_patterns/) — three more enforcers ready to lift, all using the ratchet pattern.
