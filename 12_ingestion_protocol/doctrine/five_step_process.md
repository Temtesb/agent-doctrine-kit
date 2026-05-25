# Doctrine excerpt — the five-step ingestion process

Place this in your governance doc as the procedure for incorporating external artifacts into the kit.

---

## The ingestion process

**Derives from:** Foundations [F1](../../01_foundations/F1_time_has_direction.md) (ingestion is a historical event with provenance), [E2](../../01_foundations/E2_convergence_is_triangulation.md) (an external artifact is an independent source whose convergence with internal patterns is evidence — but only if its independence is honored at ingestion), and the meta-stance [patterns are local sightings; enforcers are the home](../../00_meta_stances/patterns_local_enforcers_home.md) (external work is one more source of sightings; the kit is one more home for the enforcers).

### Step 1 — Source analysis

Read the external artifact. Inventory what's actually in it — primitives, principles, design choices, the problems it's responding to, the assumptions it makes.

The output of this step is a *map* of the source, not a value judgment. You're not yet deciding what to take; you're understanding what's there.

Common shape:

- **Primitives** — concrete mechanisms (data structures, algorithms, schemas, interfaces) the source defines.
- **Principles** — rules or invariants the source explicitly or implicitly relies on.
- **Anti-patterns** — failure modes the source is reacting to (worth noting because those failure modes likely apply to other projects too).
- **Assumptions** — what the source takes as given (its target stack, its assumed deployment shape, its assumed user model).

Done well, Step 1 produces a document that someone unfamiliar with the source could read and understand what the source is fundamentally about — independent of whether it gets ingested.

### Step 2 — Principle extraction

For each primitive identified in Step 1, ask: *"which foundation does this derive from?"*

The answer is almost always one of F1, F2, F3, E1, E2, or E3. The primitive is an instance of an underlying foundational concern; the source happened to articulate this particular instance.

Three outcomes per primitive:

- **Derivation found.** The primitive maps cleanly to an existing foundation. Record the derivation and move on to Step 3.
- **Derivation requires new framing.** The primitive maps to an existing foundation but requires articulating a derivation that the kit hasn't named before. Record the new derivation and surface it as a candidate addition to that foundation's "Implies" list.
- **Derivation not found.** The primitive doesn't derive from any existing foundation. This is rare. Most likely outcome: you haven't seen the derivation yet; revisit later. Less likely: the primitive surfaces a candidate new foundation, which routes through the elevation protocol's normal gate ([09_elevation_protocol/](../../09_elevation_protocol/)).

Per [E3](../../01_foundations/E3_foundations_aggressively_small.md), the default disposition is *"this is a derivation we hadn't articulated."* Most candidates resolve there. Resist the urge to elevate every novel-looking primitive to foundational status.

### Step 3 — Subsystem fit assessment

For each primitive that survived Step 2, ask: *"does an existing subsystem cover this concern, or does this need a new subsystem?"*

Three outcomes per primitive:

- **Existing subsystem covers it.** The primitive extends a subsystem that already exists. The ingestion's output for this primitive is an addition to that subsystem's files.
- **Existing subsystem partially covers it.** The primitive sits at the boundary between two subsystems, or extends one in a way that changes its shape. The ingestion's output is a subsystem-level revision; the change may require updating cross-references.
- **No subsystem covers it.** The primitive needs a new subsystem. This is significant — adding a subsystem is a structural decision that shapes how future ingestions and projects fit into the kit. New subsystems should be proposed with their own derivation chain to foundations, just as the existing ones are.

A primitive that fails Step 3 (no subsystem fits AND no new subsystem is justified) is the honest "this doesn't fit" outcome. Record the analysis; don't force the import.

### Step 4 — Adaptation

For each primitive that has a target subsystem, re-implement it in the kit's idiom.

Adaptation is not translation. The source's idioms, dependencies, naming conventions, and authorial choices get *reinterpreted* into the kit's:

- Filename and directory conventions (numbered subsystems, README-plus-detail-files structure)
- Code conventions (Python+SQLite stack, dataclasses, type hints, ratchet patterns)
- Documentation conventions ("Derives from:" headers, falsification conditions, anchor histories)
- Cross-reference style (relative paths to other subsystems)

The adapted primitive almost never looks identical to its source. The structural form changes; the underlying concept stays.

Adaptation often surfaces gaps the original source didn't address. For example, an external paper might describe a primitive without addressing how it interacts with concurrency, or how its outputs get audited, or how it degrades under model upgrade. The adaptation step is where those gaps get noticed — and may need to be filled by the kit's own discipline (audit-as-shape-of-data, AI-dependency tracking, etc.).

When adaptation surfaces a gap the source didn't address: *that's an interesting finding*. Record it. The gap may indicate the source was incomplete on a dimension the kit takes seriously.

### Step 5 — Provenance recording

Document the ingestion as a historical event. The record makes the kit's evolution auditable.

The provenance record (see [../templates/ingestion_record_template.md](../templates/ingestion_record_template.md)) captures:

- **Source identity** — URL, version, accessed date, license (if applicable)
- **Inventory from Step 1** — what was in the source (the map produced in Step 1)
- **Per-primitive analysis from Steps 2-4** — derivation, subsystem fit, adaptation notes
- **What got ingested** — which primitives landed in the kit and where
- **What didn't get ingested** — primitives that failed Step 2, Step 3, or were judged not valuable enough to adapt
- **Ingestion-time gaps surfaced** — issues in the source the adaptation revealed
- **Attribution** — explicit acknowledgment that the source was external and where credit is due

The record lives in the kit (or the consuming project) as a permanent artifact. Future readers asking *"where did this primitive come from?"* should be able to trace it back to its source.

Provenance recording is the F1 application to ingestion itself. An undocumented ingestion is a primitive that appeared in the kit with no traceable origin — which is the same epistemic shape as a status field that got overwritten with no audit row. The kit's own evolution must obey the same temporal discipline it imposes on project data.

## What ingestion is NOT

- **Not silent absorption.** A primitive that gets re-implemented in the kit without provenance recording is theft, not ingestion. Even when the adaptation is so thorough that no source code remains, the intellectual debt stands.

- **Not pure import.** A primitive that gets dropped into the kit without going through Steps 2-4 isn't ingested; it's grafted. Grafted code competes with the kit's structural commitments and creates compositional friction.

- **Not zero-cost.** The five steps take time. The benefit is structural integrity + auditable evolution. The cost is the bookkeeping. For substantial ingestions, the benefit dominates. For tiny adoptions (a one-line idiom from elsewhere), inline attribution in the code may be enough; full protocol overhead would exceed the value.

- **Not a value judgment on the source.** Choosing not to ingest a particular primitive doesn't mean the primitive is bad. It often means the primitive doesn't fit *this* kit's purpose; it might fit perfectly elsewhere. The ingestion protocol is a fit assessment, not a quality judgment.

## When to invoke the protocol

- A new external artifact (paper, project, library, conversation) contains primitives that look valuable for the kit
- An existing kit subsystem feels underdeveloped relative to external work on the same concern
- A consuming project is hitting a problem the kit doesn't address, and external work has formal patterns for it
- A retrospective on what's in the kit reveals primitives whose origin isn't documented (back-fill the provenance record by treating the historical absorption as an ingestion-after-the-fact)

## Cross-references

- [../README.md](../README.md) — the concept overview.
- [../templates/ingestion_record_template.md](../templates/ingestion_record_template.md) — the per-ingestion record template.
- [../examples/prizmforge_ingestion.md](../examples/prizmforge_ingestion.md) — the worked first case.
- [../../09_elevation_protocol/](../../09_elevation_protocol/) — the sibling protocol for internally-surfaced patterns.
- [../../01_foundations/E3_foundations_aggressively_small.md](../../01_foundations/E3_foundations_aggressively_small.md) — Step 2's default disposition derives from E3's smallness discipline.
