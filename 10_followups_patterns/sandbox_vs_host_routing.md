# Sandbox vs. host-resident write routing (conditional)

## Conditional framing

> **This is conditional doctrine** — see [09_elevation_protocol/doctrine/conditional_doctrine.md](../09_elevation_protocol/doctrine/conditional_doctrine.md) for the meta-concept. The rule below applies only when its activating condition holds; otherwise it's informational, not enforced.

**Applies when:** Multiple agent runtimes operate concurrently against shared host-resident state (a SQLite DB on the host filesystem, a git working tree, an HTTP-served `index.html`, etc.), AND at least one of the runtimes is sandboxed in a way that prevents reliable writes to that shared state.

**Doesn't apply when:** A single agent runtime is operating, OR multiple runtimes operate with independent state (their own DBs, their own working trees), OR all runtimes have equivalent write capability to the shared state.

**Detection mechanism:**
- Check whether the project's deployment has multiple concurrent runtimes (e.g., a launchd plist running a background loop AND a foreground interactive session AND a separate browser-sandboxed agent).
- Check whether any of those runtimes is sandboxed (cross-mount filesystem boundaries, container isolation, browser-sandbox security model).
- If both are true, the rule activates. If either is false, the rule informs rather than enforces.

**What changes when the condition activates:** Durable-state writes route through a designated host-resident write-agent. Sandboxed runtimes buffer writes as turnover documents (structured handoffs) and the host-resident agent applies them in its process context. Read operations stay distributed.

**What changes when the condition deactivates:** A single-runtime configuration doesn't need the buffer-and-handoff coordination; agents write directly via the helper. The routing rule becomes inactive; existing buffered handoffs should be drained before deactivation completes; the configuration change should be recorded (per [01_foundations/F1_time_has_direction.md](../01_foundations/F1_time_has_direction.md), state-transitions are events).

---

## Why this pattern exists

When multiple agent runtimes share host-resident state but have asymmetric write capability, naive direct-write attempts from the sandboxed runtimes produce silent or noisy failures that cascade. Specifically:

- **Silent failures** — a write attempt that the runtime believes succeeded but didn't actually persist. The runtime moves on; downstream reads see stale state; the system enters inconsistent state that's hard to diagnose.

- **Noisy failures** — a write attempt that fails with an error the sandboxed runtime can't recover from (the sandbox boundary returns ambiguous error semantics). The runtime stops mid-operation; partial state remains.

The structural answer: don't attempt direct writes from sandboxed runtimes. Buffer writes as turnover documents (structured handoffs with verbatim commands the host-resident agent can run) and let the host-resident agent apply them. The host-resident agent has unambiguous write capability; the sandboxed runtime preserves its work via the buffer; the round-trip is the cost of coordination.

---

## What "durable-state writes" covers

When the rule activates, the following are covered:

- **SQLite DB writes** to any host-mounted DB (project domain DBs, MultiAgent's `messages.db`, future on-host DBs)
- **Git operations** — commit, branch, merge, tag, push, pull, revert, anything that touches `.git/`. The git index lock (`.git/index.lock`) is itself a write-coordination artifact (see [git_lock_coordination.md](git_lock_coordination.md))
- **File mutations that need atomic coordination with a running service** — for example, editing `index.html` while an HTTP server is serving it; the server should be the single writer of files it actively reads
- **Schema migrations** — anything that modifies the structure of a host-resident DB, not just rows
- **Environment changes** — package installs, virtualenv modifications, launchd plist changes, anything that affects host runtime configuration

What does NOT route through the host-resident write-agent even when the rule activates:

- **Read operations** — any runtime can read files, query DBs, run diagnostic probes. Read access doesn't have the same coordination requirement.
- **Markdown turnover documents and design memos** — these are coordination artifacts, not durable-state writes. They land in markdown files that don't change git history until someone commits them.
- **Conversation, analysis, recommendation, review** — all the work that's about thinking, not about changing durable state.

---

## Seed evidence

Two distinct sightings in different projects under the same activating condition:

1. **MultiAgent's D-020 incident** (2026-05-12) — Cowork-browser-sandboxed runtime attempted direct writes to `~/MultiAgent/messages.db` (a host-mounted SQLite file). Writes returned ambiguous success but didn't persist. Cascade required manual reconciliation. The routing rule emerged from this incident and is documented in the MultiAgent bootstrap skill.

2. **TradeDesk and Skeleton repos** (2026-05-11) — git index lock orphans from background-process git operations interacting with user-driven foreground commits. The git-specific instance is documented separately in [git_lock_coordination.md](git_lock_coordination.md); the underlying coordination pattern (host-resident agent gates writes when sandboxed runtimes are present) generalizes.

Both sightings share the activating condition. Both produced incidents that wouldn't have happened in single-runtime configurations.

---

## When NOT to enforce this

The rule is overhead when:

- A project has only one agent runtime (no coordination needed)
- Multiple runtimes each operate against independent DBs / working trees (no shared state to coordinate)
- All runtimes have equivalent write capability (no asymmetry to manage)
- A project is in early exploration phase where the multi-runtime configuration hasn't been decided yet (premature enforcement guesses at conditions that don't hold)

In those configurations, the rule is informational. It's worth knowing the rule exists for the day the configuration changes, but it shouldn't be implemented as coordination machinery before it's needed.

---

## Composition with other coordination patterns

This pattern composes with siblings:

- [git_lock_coordination.md](git_lock_coordination.md) — the git-specific instance of write coordination. Under the same activating condition (multiple agents touching git), the git-quiesce wrapper is the structural mechanism.
- [reflective_freshness_audit.md](reflective_freshness_audit.md) — the per-edit-substrate-check pattern. When multiple agents are modifying shared state, the freshness audit catches stale assumptions before they cause corruption.

When the activating condition holds, all three patterns tend to be relevant; they cover different aspects of the same underlying coordination concern.

---

## Elevation status

This pattern is **filed as conditional stack-layer doctrine** rather than universal. The four-criteria elevation gate ([09_elevation_protocol/doctrine/four_criteria.md](../09_elevation_protocol/doctrine/four_criteria.md)) is partially met:

- ✓ Generative force — multiple operational rules derive (buffer-and-handoff, host-resident gate, read-write asymmetry)
- ✓ Reduction-resistance — derives from F1+F3 but adds the structural coordination layer those foundations don't directly imply
- ✓ Falsifiability — would be falsified by a system where sandboxed-runtime writes to shared host-resident state work reliably (current sandbox technologies don't provide this)
- ⚠ Independent triangulation — two sightings (MultiAgent D-020 + TradeDesk/Skeleton git locks); same author/AI; same broad stack. Genuinely-independent cross-project evidence is the gap.

The conditional framing means the rule earns its place without claiming universality. A future independent sighting in a project with different stack/authorship would advance the elevation evidence; until then, the conditional file documents the pattern without overstating its reach.
