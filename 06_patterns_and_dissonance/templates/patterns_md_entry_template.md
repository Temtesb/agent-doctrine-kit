# PATTERNS.md entry template

Copy this template into your project's `PATTERNS.md` at the repo root. The file is the project-layer local-sighting record per the [patterns_local_enforcers_home](../../00_meta_stances/patterns_local_enforcers_home.md) meta-stance.

---

## File header (one-time setup, top of your PATTERNS.md)

```markdown
# <Project name> Project Patterns

This file is the project-layer pattern library — the record of recurring bug shapes that have surfaced in this codebase, their fix shape, the governing principle, and the invariant test that prevents recurrence.

**Read this at session start.** The §pre-flight's third question — *"what pattern in the project pattern library does this resemble?"* — is what this file is consulted for. When you're about to write code that smells like a known pattern, find it here, mirror the fix shape, or pressure-test against the invariant test.

The library grows automatically through the lessons loop (see 05_lessons_loop/). When a `lesson_candidates` row is accepted, the stub generator appends a draft entry here for the user to refine.

## Entry format

Each entry has a stable `P00N` ID anchor so it can be referenced from `lesson_candidates.pattern_library_entry` and from invariant-test docstrings. **Anchors are append-only — never renumbered or removed.** An entry that turns out to be wrong gets a `**Status: SUPERSEDED**` line and a pointer to the entry that replaces it.

Fields per entry:

- **Governing principle** — anchor to a foundation (`F1`, `E2`), stack-layer rule, or project doctrine section (`§5.4`).
- **Bug shape** — what goes wrong, in 1-2 sentences.
- **Fix shape** — what works, in 1-2 sentences.
- **Invariant test** — link to the test that prevents recurrence (or `(none yet)` if hard to detect mechanically).
- **First seen** — date.
- **Source** — session log entry, lesson_candidate ID, or `seed`.

## Index

- [P001 — Short title (§anchor)](#p001--short-title)
- [P002 — Short title (§anchor)](#p002--short-title)
- ...

---
```

---

## Single entry template

```markdown
## P00N — Short descriptive title

**Governing principle:** <foundation anchor or doctrine pointer; e.g., F1, §5.4>

**Bug shape:** <1-2 sentences describing what goes wrong>. <Concrete instance: where it was first observed, what happened, what the impact was>.

**Fix shape:** <1-2 sentences describing what works>. <How to recognize the shape in code review or at design time>.

**Invariant test:** [`tests/<test_file>.py:<TestClassName>`](tests/<test_file>.py)

**First seen:** YYYY-MM-DD

**Source:** <session log path | lesson_candidate #N | seed>

---
```

---

## Worked example

Below is a real entry from a project that adopted this pattern, to anchor the template:

```markdown
## P004 — UPDATE on meaningful business column without audit row

**Governing principle:** §1 (audit is the shape of the data), F1

**Bug shape:** A function UPDATEs a column tracking a meaningful business fact (price, status, decision, category) without recording the prior value. The history of the fact is silently overwritten. Concrete instance: 88 of 89 inventory rows had `category_id` silently overwritten by AI guesses with no audit; the principle had been written but not enforced.

**Fix shape:** In the same transaction as the UPDATE, INSERT a `fact_corrections` row with prior_value, new_value, reason, confidence. The §pre-flight's second question is the structural trigger.

**Invariant test:** [`tests/test_arch_invariants.py:TestUpdateRequiresFactCorrection`](tests/test_arch_invariants.py)

**First seen:** 2026-05-05 (task #50)

**Source:** `seed` — see PLANS/2026-05-05_session_log.md task #50
```

---

## SUPERSEDED entries

When a pattern turns out to be wrong (the bug shape was misidentified, the fix shape was insufficient, the principle was revised), the entry doesn't get deleted. It gets marked SUPERSEDED with a pointer to the replacement:

```markdown
## P003 — (former) Some incorrect pattern title

**Status: SUPERSEDED by P017**

**Why superseded:** The original entry conflated two distinct shapes (X and Y). P017 separates them and provides the correct fix for X; P018 covers Y. The original invariant test was over-broad and had been allow-listed in many places.

(Original entry text preserved below for reference.)

---
```

Anchors are never reused. P003 stays in the file forever as a deprecated entry with a clear pointer to its replacement(s). This honors F1 — the history of pattern revisions is itself a fact the project should be able to query.
