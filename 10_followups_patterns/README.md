# 10 — Stack-layer FOLLOWUPS patterns

## The concept

Concrete stack-layer enforcers that are staged for promotion (per [09_elevation_protocol/](../09_elevation_protocol/)) and ready to lift. Most are universal within their layer; one is **conditional** (see [09_elevation_protocol/doctrine/conditional_doctrine.md](../09_elevation_protocol/doctrine/conditional_doctrine.md)) — applies only under named conditions and is informational otherwise. Each pattern has project-layer seed evidence, a fix shape, and an implementation sketch.

These are presented as **worked examples** — concrete instances of how stack-layer enforcers look when you adopt the patterns in this kit. If you're building a Python+SQLite project, these are immediately applicable when their conditions hold; if you're on a different stack, the *shape* of how the enforcer is structured may transplant even if the specifics don't.

## What's in this directory

| File | Pattern | Universal/Conditional | Why it matters |
|---|---|---|---|
| [static_coupling_invariants.md](static_coupling_invariants.md) | CI tests that catch when cross-file references don't resolve (HTML ↔ JS ↔ server, JSON ↔ Python, etc.) | Universal (for projects with the relevant coupling shape) | A class of bugs that produces zero server-side exception; agents may not notice them because no error fires |
| [git_lock_coordination.md](git_lock_coordination.md) | Wrapper for background processes touching git, with explicit acquire/release and orphan-lock watchdog | Universal (for projects with background processes touching git) | Multi-agent systems where multiple processes touch git concurrently will eventually orphan `.git/index.lock` |
| [reflective_freshness_audit.md](reflective_freshness_audit.md) | Reconciliation pass that runs before consumers act on reflective surfaces; surfaces claims that have been falsified by substrate changes | Universal | *"Artifacts of truth exist; nothing forces downstream readers to consult them at the moment of use"* — directly applicable to per-proposal reviewers |
| [sandbox_vs_host_routing.md](sandbox_vs_host_routing.md) | Buffer-and-handoff routing rule when sandboxed agents share host-resident state with host-resident agents | **Conditional** — applies when multi-runtime sharing host state | First conditional-doctrine instance in the kit; informs rather than enforces in single-runtime configurations |

## Why these three specifically

Each of the three has the same shape:

- **Real seed evidence** — at least one concrete instance where the pattern surfaced in a project, with the specific bug and its impact
- **Fully-determined-by-stack** — the bug class is fully determined by the stack choice (Python+SQLite+HTTP+JS, or process+git, or AI-consuming-reflective-surface), not by what the project does
- **Stack-layer enforcer ready** — the fix shape is implementable as a stack-layer enforcer that any project of that stack shape can inherit
- **Currently staged, not yet elevated** — they meet criteria 1, 2, and 3 of the [elevation protocol](../09_elevation_protocol/), and have project-layer evidence (criterion 4) but not yet enough cross-project independence to formally promote

By including them here, the kit makes them adoptable as project-layer patterns immediately, while their elevation status is tracked separately. Adopting one in your project counts as additional seed evidence — and as the same pattern surfaces in more independent projects, it earns formal stack-layer status.

## How to use these patterns

Each file is self-contained. For each pattern:

1. **Read the file.** It describes the bug class, the fix shape, the seed evidence, and the implementation sketch.

2. **Decide whether the pattern applies to your project.** Some patterns (static coupling invariants) apply only to projects with the relevant coupling shape; others (git-lock coordination) apply to most projects with background processes.

3. **Implement the fix shape.** The files give enough detail to implement directly. The implementations are not yet packaged as drop-in libraries because the integration points are project-specific.

4. **Record adoption in your project's PATTERNS.md.** Each adoption adds to the cross-project evidence supporting elevation. Cite the relevant file from this directory as the canonical source of the pattern.

5. **If you find a fourth pattern of this kind**, file a promotion proposal (see [09_elevation_protocol/templates/promotion_proposal_template.md](../09_elevation_protocol/templates/promotion_proposal_template.md)) so the pattern can be staged here.

## The "reflective freshness audit" is the gem

Of the three, the [reflective_freshness_audit.md](reflective_freshness_audit.md) pattern is the deepest. The principle it instantiates:

> Artifacts of truth exist; nothing forces downstream readers to consult them at the moment of use. The fix at every layer is a structural enforcer at the consumer's decision moment — not another principle entry.

This is directly applicable to **any per-proposal reviewer in an agent-governed system**. The reviewer reads each proposal in isolation. The system state at the time of review (current contracts, current invariants, current rejection patterns, recent rolled-back resolutions) is the *substrate* the reviewer's claims must reconcile against. Without a reconciliation pass, the reviewer can approve a proposal whose claims have been falsified by recent system state — the artifacts of truth exist but nothing forced the reviewer to consult them.

If you adopt only one pattern from this directory, this is the one with the highest leverage for agent-governed systems specifically.

## Cross-references

- [09_elevation_protocol/](../09_elevation_protocol/) — the protocol these patterns are staged under.
- [00_meta_stances/patterns_local_enforcers_home.md](../00_meta_stances/patterns_local_enforcers_home.md) — the meta-stance about how project sightings become stack enforcers.
- [04_pre_flight_and_invariants/](../04_pre_flight_and_invariants/) — the ratchet pattern most of these enforcers use.
