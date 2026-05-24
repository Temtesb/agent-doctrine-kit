# 06 — Patterns and dissonance

## The concept

Two cross-session memory surfaces at the project layer, with different shapes:

- **`PATTERNS.md`** — the *resolved-pattern library*. Append-only record of recurring bug shapes that have surfaced in this codebase, with their fix shape, governing principle, and the invariant test that prevents recurrence. Used by the §pre-flight question 3 — *"what pattern in the project pattern library does this resemble?"*

- **Dissonance ledger** — the *unresolved-tension log*. Append-only record of competing valid concerns the system has perceived but hasn't yet resolved. Open dissonances are *signal of system reach*, not technical debt. The tension-holding pillar treats holding tension as the work; collapsing it via expedience is the failure.

**Derives from:** Foundations [F1](../01_foundations/F1_time_has_direction.md) (both files are append-only event logs) and [E2](../01_foundations/E2_convergence_is_triangulation.md) (PATTERNS.md is the project-side local-sighting record per the *patterns are local sightings; enforcers are the home* meta-stance).

## Why this matters for agent-governed systems

Agents start each session with no memory of what was learned in prior sessions. Per-agent stats (token efficiency, feedback value) are not memory of *patterns*. Without cross-session memory of patterns, the same bug shape gets re-discovered every session.

The two surfaces have different jobs:

- **PATTERNS.md is for things the system figured out.** *"Here's what we learned; here's what stops it from recurring."* Consulted at design-time (the pre-flight) and at lesson-acceptance time (the stub generator appends entries here).

- **The dissonance ledger is for things the system hasn't figured out.** *"These two doctrines conflict in this case; we're holding the tension rather than collapsing it; here's the rationale."* Surfaces unresolved questions to the user without forcing premature resolution.

Both are append-only. Entries that turn out to be wrong get a SUPERSEDED line pointing to the replacement, never deletion.

For multi-agent systems, both surfaces also feed the elevation protocol ([09_elevation_protocol/](../09_elevation_protocol/)). Recurring patterns in PATTERNS.md across multiple projects are elevation evidence for stack-layer enforcers. Recurring tensions in the dissonance ledger across multiple projects are evidence for new foundations or doctrine clauses.

## What's in this directory

| File | Purpose |
|---|---|
| [templates/patterns_md_entry_template.md](templates/patterns_md_entry_template.md) | The template for a `PATTERNS.md` entry. Drop into your repo's root; replace with actual entries as patterns surface. |
| [templates/dissonance_ledger_entry_template.md](templates/dissonance_ledger_entry_template.md) | The template for a dissonance ledger entry. Lives wherever your project's ledgers live. |

## How to adopt

1. **Create your `PATTERNS.md`** at the repo root. Use the template as the entry format. The file starts with a one-page header explaining the format (anchors are `P00N`, append-only, SUPERSEDED for retractions) and an empty entries list.

2. **Create your dissonance ledger** (or whatever you want to call it — `PLANS/dissonance_ledger.md` is one convention). Same shape: header explaining the format, entries as they surface.

3. **Wire PATTERNS.md into the pre-flight.** The third pre-flight question consults it. Your agents read PATTERNS.md at session start (as a structural cue, like CLAUDE.md or README.md). When a change resembles a known pattern, mirror the fix shape unless you have a specific reason to diverge.

4. **Wire PATTERNS.md into the lesson loop.** The stub generator (see [05_lessons_loop/code/stub_generator_signature.py](../05_lessons_loop/code/stub_generator_signature.py)) appends new entries when lesson candidates are accepted. Each new entry's anchor is the next available `P00N`.

5. **Wire the dissonance ledger into your decision surface.** When the agent encounters a tension between principles (per the fifth pre-flight question), surface it to the user via the ledger. The user decides whether to:
   - Resolve immediately (and the resolution becomes a doctrine clause)
   - Hold the tension explicitly (and the ledger entry documents the rationale for holding)
   - Re-frame the tension (and the ledger entry records the re-frame)

6. **Cross-reference both surfaces with the universal-layer doctrine.** Each PATTERNS.md entry cites a governing principle (a foundation or stack-layer rule). Each dissonance ledger entry names which principles are in tension. The cross-references make the surfaces queryable for higher-layer analysis.

## The tension-holding principle

> Encountering competing valid concerns — between two doctrines, between doctrine and deadline, between two foundations — is itself a sign that the system has the resolution to perceive multiple concerns at once. A simpler system has fewer tensions because it perceives less. Holding the tension is the work; collapsing it via expedience is the failure. The mature stance when two principles pull in opposite directions is to **name the tension explicitly to the user, execute per doctrine, and pay the cost the right answer demands**.

**Falsification condition:** A demonstration that silently collapsing competing concerns produces better outcomes than naming them explicitly. We have no such demonstration; observed cases of silent collapse have produced trust erosion, surprise bugs, and re-discovered patterns.

The principle has structural consequences for the surfaces here: the dissonance ledger is the *infrastructure for the tension-holding pillar*. Without a surface for unresolved tensions, the only places they can live are (a) the agent's working memory (lost at session end) or (b) the user's head (lossy and slow to retrieve). The ledger makes them durable, surfaceable, and aggregatable.

## Cross-references

- [00_meta_stances/patterns_local_enforcers_home.md](../00_meta_stances/patterns_local_enforcers_home.md) — the meta-stance about where patterns and enforcers live.
- [04_pre_flight_and_invariants/](../04_pre_flight_and_invariants/) — the pre-flight's questions 3 (pattern library) and 5 (tension naming) directly consume these surfaces.
- [05_lessons_loop/](../05_lessons_loop/) — accepted lesson candidates produce new PATTERNS.md entries through the stub generator.
- [09_elevation_protocol/](../09_elevation_protocol/) — cross-project pattern recurrence is the elevation criterion that promotes a project-layer sighting to a stack-layer enforcer.
