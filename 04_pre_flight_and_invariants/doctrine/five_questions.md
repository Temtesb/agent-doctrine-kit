# Doctrine excerpt — the five-question design-time pre-flight

Place this in your governance doc as the section the agent reads before any non-trivial change. *Non-trivial* means: anything that touches schema, data flow, AI output, audit log, money calculation, or lifecycle state. Pure documentation edits, comment-only changes, and trivial typo fixes are exempt; everything else runs the pre-flight.

---

## Design-time doctrinal pre-flight

**Derives from:** Foundations [E1](../../01_foundations/E1_corpus_is_hypothesis.md) (doctrine that isn't consulted at the moment of code-write is decorative) and [F2](../../01_foundations/F2_logic_holds.md) at the process layer (a change made without checking which principles govern it has no defense against contradicting them).

Before starting any non-trivial change — before the first Edit/Write to a non-doc file, before any DDL change, before any new handler — pause and answer the five questions below.

### The five questions

**1. What doctrine sections govern this change?**

Name them explicitly. If you can't name at least one, either the change is genuinely doctrinal-orthogonal (rare) or you don't yet understand what the change is. Walk back to understanding before continuing.

Examples:
- Schema additions invoke universal-layer F1/F2 and the project's data-discipline section.
- New AI-driven writes invoke "AI is hypothesis, not authority" + the candidate-lifecycle pattern.
- Merge-style operations invoke F2 (single source of truth) + any project precedent for photo/data deduplication.

**2. What's the audit trail?**

What event row, fact_corrections row, lifecycle event, or candidate decision-row does this change leave behind? Per [F1](../../01_foundations/F1_time_has_direction.md)'s "audit is the shape of the data" — if the answer is "none," that's almost certainly an F1 violation in the making.

The bar for "no audit needed" is *"this is genuinely transient infrastructure"* (expired tokens, temp upload files), not *"I forgot to design one."*

**3. What pattern in the project pattern library does this resemble?**

The pattern library ([06_patterns_and_dissonance/](../../06_patterns_and_dissonance/) holds the template) records recurring bug shapes that have surfaced in this codebase, with their fix shape, governing principle, and the invariant test that prevents recurrence.

If a pattern matches your change, mirror its fix shape unless you have a specific reason to diverge. If no pattern matches but the change is non-trivial, your work may produce a new entry — accepted lesson candidates from [05_lessons_loop/](../../05_lessons_loop/) auto-generate stubs.

**4. What invariant test prevents the next instance of this kind of bug?**

If the answer is "none yet," that's a candidate to add to your architecture invariants ([../enforcer/_known_allowed_ratchet_template.py](../enforcer/_known_allowed_ratchet_template.py) for the pattern) — either now alongside the change, or via a `lesson_candidates` row that the stub generator turns into a draft test for the user to complete.

The bar to skip writing one is *"the existing invariant tests already prevent this,"* not *"I can't think of one right now."*

**5. Is there a tension between doctrine and what's expedient right now?**

If you're noticing a doctrinal rule that the change would bend or bypass on local-view grounds — *"this is just 7 lines, the spirit of the rule allows it"*, *"this is a special case the doctrine didn't anticipate"*, *"the deadline pressure justifies the shortcut"* — that noticing is a red flag, not a green light.

**Name the tension explicitly to the user before resolving it.** Silent collapse of doctrine-vs-expedience tension is a known trust-erosion shape (see [06_patterns_and_dissonance/](../../06_patterns_and_dissonance/) for the pattern entry template).

The bar to skip naming the tension is *"no doctrine is being bent"* (i.e., the change doesn't conflict with any rule), not *"I can rationalize the bend."*

### Demonstrating compliance

Each non-trivial change records the answers somewhere durable:

- In a code comment at the call site
- In the commit message body
- In the active session log under a `## Pre-flight` heading per change

Inline comments are preferred when the doctrine reference adds clarity at the read site (e.g., a `# Per §5.4: cached value, refreshed by ...` next to a stored computed column). Commit-message references are preferred when the change spans multiple files for one design decision. Session-log entries are the fallback — and an open invitation to migrate the rationale into the more durable surface before the session ends.

### Failure mode this prevents

> Six months from now another agent (or me) writes UPDATE inventory.category_id without realizing the AI-output-as-hypothesis rule made AI output suspect, then the user has to be the loop again.

The pre-flight makes that scenario impossible at the design-time layer. The architecture invariant tests (in `../enforcer/` and across the concept directories) make it impossible at the merge-time layer. Both layers are needed.

### When the pre-flight produces a "no, don't"

Sometimes the pre-flight surfaces that the change shouldn't happen at all — at least not in the shape originally conceived. The doctrine doesn't allow it; or the audit trail would be impossible; or the bend in question is too sharp to honor honestly.

When that happens: **stop and re-design**. The pre-flight is doing its job. The point isn't to find a way to make every change pass the questions; the point is for the questions to catch the changes that need to be re-thought before code is written.

Re-design might mean:
- Splitting the change into two: a doctrinal addition + a separate code change that derives from it.
- Adding doctrine first (which goes through its own review path) so the code change has a foundation to derive from.
- Raising the underlying question to the user as a tension rather than resolving it unilaterally.

The user prefers a halted pre-flight that surfaces a real question over a completed change that bent doctrine silently.
