# Dissonance ledger entry template

Copy this template into your project's dissonance ledger (`PLANS/dissonance_ledger.md`, `dissonance_log.md`, or whatever your project uses). The ledger is the infrastructure for the tension-holding pillar.

---

## File header (one-time setup)

```markdown
# <Project name> — Dissonance Ledger

This file is the record of competing valid concerns the system has perceived but hasn't yet resolved. Per the tension-holding principle:

> Encountering competing valid concerns — between two doctrines, between doctrine and deadline, between two foundations — is itself a sign that the system has the resolution to perceive multiple concerns at once. A simpler system has fewer tensions because it perceives less. Holding the tension is the work; collapsing it via expedience is the failure.

Open dissonances are signal of system reach, not technical debt. Entries are append-only with stable `D00N` anchors. Resolutions are recorded inline as updates to existing entries (the original framing is preserved per F1; the resolution adds context, never overwrites).

Status values per entry:
- **open** — actively held; no resolution direction chosen
- **resolved** — user has made a choice; resolution recorded inline; entry stays for reference
- **rephrased** — the original framing was wrong or shifted; pointer to the rephrased entry
- **archived** — no longer load-bearing (the tension dissolved because circumstances changed); rationale recorded

## Entry format

Each entry has:

- **Stable `D00N` anchor** (never reused; never removed)
- **Title** (one line, names the tension)
- **The two (or more) concerns in tension** — each cited to its principle, with the case where they pull in opposite directions
- **Status** (open/resolved/rephrased/archived)
- **Holding rationale** (when status=open) — why we're holding rather than collapsing
- **Resolution** (when status=resolved) — the decision, the rationale, the date, who decided
- **Cross-references** — which patterns, lesson candidates, or other ledger entries this relates to

## Index

- [D001 — Title (status)](#d001--title)
- [D002 — Title (status)](#d002--title)
- ...

---
```

---

## Single entry template (open)

```markdown
## D00N — Title naming the tension

**Status:** open
**Detected:** YYYY-MM-DD
**Detected by:** <agent name | session log | conversation record>

### The tension

**Concern A:** <principle X, anchored to its source> says <implication>.

**Concern B:** <principle Y, anchored to its source> says <implication that conflicts with A>.

In the case of <concrete situation>, A and B pull in opposite directions. Following A produces <outcome that violates B>; following B produces <outcome that violates A>.

### Holding rationale

We are holding this tension because:

- <Reason 1 — e.g., neither principle is currently load-bearing enough to override the other; the user hasn't directed which to prioritize>
- <Reason 2 — e.g., the tension surfaces a possible gap in doctrine that may need a new clause to resolve cleanly; collapsing prematurely would obscure the gap>
- <Reason 3 — e.g., the situations where this arises are rare enough that ad-hoc per-instance handling is cheaper than systemic resolution right now>

### Cross-references

- Related patterns: <P00N entries that touch this tension>
- Related lesson candidates: <#N>
- Related ledger entries: <D00N if the tension shares structure with others>

---
```

---

## Single entry template (resolved)

```markdown
## D00N — Title naming the tension

**Status:** resolved
**Detected:** YYYY-MM-DD
**Resolved:** YYYY-MM-DD
**Resolved by:** <user identifier>

### The tension (preserved from original entry)

<As above; not modified after resolution>

### Resolution

**Decision:** <one sentence stating the chosen direction>

**Rationale:** <2-3 sentences explaining why this direction over the alternative — what evidence or principle tipped the choice>

**What changes:** <concrete operational changes — doctrine update, new pattern entry, code change, process adjustment>

**What stays:** <the other principle still applies in its non-conflicting cases; this resolution doesn't override it everywhere, only in the specific situation named>

### Cross-references

- Related patterns: <P00N entries created or updated as a result of this resolution>
- Doctrine updates: <CLAUDE.md sections modified>
- Code changes: <commit SHAs or PR numbers>

---
```

---

## Worked example (open)

```markdown
## D013 — Doctrine vs. expedience: file-size limit applied to one prose-heavy section

**Status:** open
**Detected:** 2026-05-08
**Detected by:** session log 2026-05-08

### The tension

**Concern A:** The 800-line hard limit on file size (§2.1) says that any file above the limit must be split. The rule exists to prevent monolith handlers from accumulating.

**Concern B:** The doctrine file `CLAUDE.md §1` contains explanatory prose about the project's pillars that has grown organically as new pillars are added. Splitting the file across multiple files would fragment the conceptual frame that newcomers (human and AI) read at session start — the cohesion of §1 IS the value.

In the case of CLAUDE.md crossing the 800-line limit, A and B pull in opposite directions. Following A (splitting CLAUDE.md) produces fragmentation that defeats the purpose of session-start orientation. Following B (keeping CLAUDE.md whole) produces an unenforced exception to the size limit.

### Holding rationale

We are holding this tension because:

- The size limit was originally framed for handler files (where the failure mode is monolith accumulation of business logic). Applying it uniformly to doctrine files conflates two different concerns.
- A resolution would either narrow the size-limit rule's scope (good doctrine work, but not urgent) or find a way to split CLAUDE.md without losing cohesion (no obvious mechanism yet).
- The pre-flight question 5 explicitly asks "is there a tension between doctrine and what's expedient right now?" — the right answer here is to name the tension rather than silently violate either rule.

### Cross-references

- Related patterns: P010 — silent collapse of doctrine-vs-expedience tension (the meta-pattern this entry instantiates)

---
```

---

## Why this matters for agent-governed systems

Without a dissonance ledger, the only places unresolved tensions can live are:

- **The agent's working memory** — lost at session end. The next agent re-discovers the same tension.
- **The user's head** — lossy and slow to retrieve. The user re-explains the tension every time it surfaces.
- **Silent collapse** — the agent picks one side without naming the tension; the loser's perspective is lost; trust erodes when the unnoticed-loser turns out to have mattered.

The ledger makes tensions:

- **Durable** — survives sessions
- **Surfaceable** — agents can read it; the user can review pending entries
- **Aggregatable** — recurring tensions across entries are evidence for new doctrine clauses or foundation revisions
- **Honest** — naming the tension is what the tension-holding pillar requires

The dissonance ledger is what makes the tension-holding pillar structural rather than aspirational. Without it, the pillar is a principle; with it, the pillar has a home.
