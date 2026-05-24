# Patterns are local sightings; enforcers are the home

## The principle

> When the same bug shape recurs across projects, the canonical fix lives at the stack layer as an enforcer. The project-side equivalents (a `PATTERNS.md` file recording recurring bug shapes seen in that codebase) are the *local-sighting* records — they trace where the shape was observed and serve as evidence for elevation criteria. A pattern entry without a corresponding stack-level enforcer is a project-trapped lesson; an enforcer without project-side pattern entries has no audit trail for when and where the shape recurred. Both layers carry their own work, and they cite each other.

**Derives from:** Foundation E2 (local convergence on a pattern is evidence, not proof; the pattern entry is the data, the enforcer is the reusable mechanism) and Foundation E3 (the layered architecture is what makes elevation possible).

## The two layers carry different work

**Project-side pattern entries** (a `PATTERNS.md` file at your repo root):

- Record what was *observed* in this specific codebase
- Carry the *seed evidence* — the concrete instance, the date, the session log reference
- Cite the governing principle (a stack-layer or universal-layer rule)
- Cite the stack-layer enforcer that prevents recurrence
- Are append-only; entries that turn out to be wrong get `**Status: SUPERSEDED**` and a pointer

**Stack-layer enforcers** (invariant tests, schema constraints, lint rules):

- Encode the *fix* — the structural mechanism that prevents the bug shape from recurring
- Inherit into any project that adopts the stack layer
- Are general — they don't depend on the specific project that first surfaced the pattern
- Document the *seed evidence* — which project-layer sightings justified the enforcer's existence

The cross-references are bidirectional. The pattern entry says *"this is why the enforcer exists."* The enforcer says *"these are the sightings that justified me."*

## Why this matters for agent-governed systems

Agent-driven code modification scales the rate at which patterns are discovered. A single human discovering a bug shape might see it three times before naming it; an agent system processing dozens of repos may see the same shape across many of them in a week.

If every sighting is fixed *only at the project layer*, the same lesson gets re-learned in every project the agents touch. The fix is local; the prevention is local; the next agent encounters the same trap in the next repo and learns it again. Lesson velocity ≈ zero.

If sightings flow upward through the elevation protocol, the canonical fix lands at the stack layer, where every project that adopts the stack inherits it for free. Lesson velocity scales with the size of the project portfolio.

The discipline is: when an agent or reviewer discovers a recurring shape, the question is not just *"how do we fix this here?"* but *"is this a project-specific case or a stack-layer pattern? If the latter, the enforcer's home is up a layer."*

## Concrete shape — a sighting that became an enforcer

**Seed evidence (project layer):** In one project, the shelf-scan upload form had eleven concrete instances of three sibling shapes in a single bug batch — eight HTML/JS ID mismatches where `getElementById('foo')` referenced an ID that didn't exist in any template, two unrouted endpoint references where `api('foo_endpoint')` didn't match any handler in the server's routing table, and one missing `onclick` attribute. Eight of the eleven would never have produced any server-side exception in any layer.

**Project-layer pattern entry:** Recorded in that project's `PATTERNS.md` as a P-numbered entry with the bug shape, fix shape, governing principle (F2 — non-contradiction applied at the file-boundary layer), the seed evidence above, and a pointer to the stack-layer enforcer.

**Stack-layer enforcer (the home):** Three sibling invariant tests in the stack's `foundation/contracts/` directory:

1. JS-IDs-resolve-in-HTML
2. JS-API-endpoints-resolve-in-server
3. HTML-handlers-resolve-in-JS

All use the `_KNOWN_ALLOWED` ratchet pattern (baseline current state, fail forward on regressions, ratchet down as fixes land). Any project bootstrapped from the stack inherits these tests. The next project that hits one of the eleven sub-shapes catches it at CI rather than at runtime.

**Bidirectional citation:** The stack-layer enforcer documents the project-layer pattern entry as seed evidence. The project-layer entry names the stack-layer test file as the canonical home for the fix.

## How to adopt this stance

1. **Establish your project's `PATTERNS.md`** (see [06_patterns_and_dissonance/](../06_patterns_and_dissonance/) for the template). It's a project-level append-only library of recurring bug shapes seen in *this* codebase.

2. **Distinguish at recording time** which layer a pattern belongs at. The criteria:
   - **Project layer only:** specific to your domain, your business rules, your data
   - **Stack layer:** any project of your stack shape (Python+SQLite+HTTP+JS, etc.) would hit the same bug
   - **Universal layer:** any project of any shape would hit it (rare)

3. **Wire the elevation protocol** (see [09_elevation_protocol/](../09_elevation_protocol/)). For patterns that look stack-layer or universal, the protocol describes when they earn promotion based on cross-project evidence.

4. **Cross-reference religiously.** Every project-layer pattern entry names its stack-layer enforcer (or `[none yet]` if it hasn't been promoted). Every stack-layer enforcer documents its seed-evidence project-layer entries. The cross-references are how the layers cohere.

## Cross-references

- [prefer_enforcers_over_principles.md](prefer_enforcers_over_principles.md) — the parent principle this companion principle extends.
- [three_layer_architecture.md](three_layer_architecture.md) — the structural model that makes "the home is at the right layer" meaningful.
- [06_patterns_and_dissonance/](../06_patterns_and_dissonance/) — the project-layer `PATTERNS.md` template.
- [09_elevation_protocol/](../09_elevation_protocol/) — the criteria for moving a sighting up to a stack-layer enforcer.
