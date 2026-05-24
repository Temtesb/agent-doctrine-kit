# Notes on PrizmForge from someone working a related problem in a different domain

You asked for thoughts; this is the long-form take. Peer-to-peer — I'm not advocating that you adopt any of this.

Some context on what I'm working from: my project (TradeDesk — single-user resale operations, runs autonomous Claude agents on schedules) is the *project-layer instance* of a three-layer architecture I've been building. The **stack layer** is a Python+SQLite skeleton that codifies cross-project patterns and enforcers. The **universal layer** is a small set of physical/logical and epistemic invariants (the "Cornerstones") that any project of any shape can derive from. PrizmForge sits at a structurally interesting position — it's Python+SQLite (so the stack layer transplants directly) AND it operates on third-party repos (so it has a deeper question to answer about what doctrine layer it injects into the repos it modifies).

I'll be explicit about which layer each concept lives at, because the layer determines where it should land in your architecture and how it composes with the rest.

Real schema and code throughout so you can see the shape concretely. Take what's useful; discard the rest.

---

## The thesis in one sentence

PrizmForge has built the **causal** layer of safe autonomous modification (this change is well-formed, doesn't conflict, passes review). The concepts below are the **temporal** and **epistemic** layers on top — what makes the system learn over time, retrospect on its own changes, accumulate trust about what kinds of changes go well, and recognize when the gap between principle and enforcement needs structural closure.

The layers compose. You will eventually need them under operational pressure (the reviewer-as-uniform-gate problem hits every system that gates uniformly; the principle-vs-enforcer gap accumulates silently). The question is whether you build them ad hoc when they hurt, or transplant a worked-out version.

---

## The meta-principle: prefer enforcers over principles

This is the single most important framing. Quoted from my stack-layer doctrine:

> **Prefer enforcers over principles.** A principle in a doc says "you're supposed to remember this." An enforcer is code that fails at write, build, or run time if violated. Schema constraint, decorator, pre-commit hook, contract test, lint rule, runtime assertion, integrity check. Every lesson that lands should be evaluated for enforcer potential. Principles are the fallback for things that genuinely cannot be enforced (judgment, taste, social context). This derives from Foundation E2 — convergence on a documented principle is necessary but not sufficient evidence that the principle is honored at runtime; an enforcer is the structural mechanism that closes the gap between belief and verification.

This is a *stance*, not a feature. It reframes how every other concept below should be received: not as *"adopt this rule"* but as *"build the enforcer that makes the rule self-honoring."*

PrizmForge's Reviewer agent is currently the primary enforcement mechanism — but a Reviewer is itself a *principle-shaped enforcer*: it depends on the Reviewer remembering and consistently applying the criteria. The deeper move is to push as much enforcement as possible into structural mechanisms that cannot be forgotten or socially engineered: schema constraints that reject bad rows, pre-commit hooks that reject bad commits, CI tests that reject bad PRs, decorators that fail at registration time, integrity checks that surface drift in the data shape.

The companion principle:

> **Patterns are local sightings; enforcers are the home.** When the same bug shape recurs across projects, the canonical fix lives at the stack layer as an enforcer. The project-side equivalents (a `PATTERNS.md` file recording recurring bug shapes seen in that codebase) are the *local-sighting* records — they trace where the shape was observed and serve as evidence for elevation criteria. A pattern entry without a corresponding stack-level enforcer is a project-trapped lesson; an enforcer without project-side pattern entries has no audit trail for when and where the shape recurred. Both layers carry their own work, and they cite each other.

For PrizmForge specifically, this framing matters because you're building a *multi-repo* tool. As your agents operate across third-party repos, you'll find the same bug shapes recurring in different codebases — and the temptation will be to fix each one at the project layer (the repo being modified). The deeper move is to recognize the recurring shape and build the enforcer once, at the layer where it belongs. Without this discipline, the same lesson gets re-learned in every repo.

### The paired meta-principle: the hypothesis posture

"Prefer enforcers over principles" addresses the gap between what doctrine claims and what runtime honors. There's a second gap worth naming explicitly — between how doctrine is *written* and how AI agents *read* it. Quoting from my universal-layer doctrine (Foundation E1, the corpus-is-a-hypothesis foundation):

> Every rule in the corpus is the current best understanding, anchored to a stated reason, subject to revision when something deeper is discovered, when the rule's falsification condition is demonstrated, or when cross-project evidence reveals it was domain-specific. The corpus is not a list of true things; it is the set of working hypotheses under which the system currently operates.
>
> The hypothesis posture changes how the corpus reads. Newcomers (human or AI) read it as something to challenge from a position of derived foundations, not as gospel.
>
> **AI-dependency note:** This foundation matters more under AI authorship than under human-only authorship. An AI consuming an authority-shaped doc may follow it more rigidly than a human would; the hypothesis posture is the structural hedge against that.

For PrizmForge this is not stylistic. Your architecture is *AI-consuming-doctrine all the way down* — proposing agents read the rules, the Reviewer reads the rules, future agents reading historical proposals read the rules embedded in them. An authority-shaped doctrine will produce rigid compliance with stale rules; a hypothesis-shaped doctrine produces critical engagement and visible revision when the rules drift from reality.

Concretely, this changes how doctrine entries are written:

- Every rule declares **what would prove it wrong** (a falsification condition), so the reading agent can pressure-test the rule against current state rather than just defer to it.
- Every rule declares its **anchor history** — when it was added, why, what triggered any subsequent re-anchoring — so the reading agent can see the rule as a temporal artifact rather than an eternal one.
- Every rule with AI-behavior dependencies declares them (see §10), so when models change the dependent rules get flagged for review.

The two meta-principles compose: *prefer enforcers over principles* prevents principles from going unenforced; *the hypothesis posture* prevents principles from being followed when they've gone stale. Together they're how doctrine is held in a system where the readers are AI agents who don't have a human's natural skepticism toward authority text.

---

## The three-layer architecture

Doctrine isn't monolithic. It lives at three layers with different scopes and responsibilities:

**Universal layer** — foundational invariants that apply to any project of any shape:

- **F1** — Time has direction. (History is asymmetric; append-only is the default; lifecycle transitions are events not labels; audit is the shape of the data.)
- **F2** — Mathematics and logic hold. (Non-contradiction; single source of truth; atomicity across tables for one logical event.)
- **F3** — Information has asymmetric durability. (Once leaked, it cannot be unleaked; durable records outlive their creators; lock state outlasts the process that held it.)
- **E1** — The corpus is a hypothesis, not an authority. (Every claim needs falsifiability; AI output is hypothesis not fact; absence of complaint is not evidence of correctness.)
- **E2** — Convergence is evidence of triangulation, not proof of truth. (Multiple aligned sources is weaker than triangulation from independent ones; consensus among similar reasoners is not the same as independent verification.)
- **E3** — The foundational layer must be aggressively small. (Most lessons are operational; foundations are bedrock; layer-confusion weakens the corpus.)

**Stack layer** — patterns and enforcers specific to a technology stack. My stack layer is Python+SQLite; it owns things like *"auto-discovered migration system"* (derived from F1), *"connection factory abstracting the backend"* (F2), *"every UPDATE on meaningful columns writes to an audit table"* (F1 applied to data-mutation patterns), *"static-coupling invariants for HTML↔JS↔server"* (F2 at the file-boundary layer). **PrizmForge is also Python+SQLite, so much of this layer would transplant directly.**

**Project layer** — rules and doctrine specific to one codebase. TradeDesk's CLAUDE.md is its project layer; it owns things like *"a $100 net-profit floor at the FLOOR comp scenario"* and *"three-listings-per-day is the output goal."* PrizmForge's project layer would own things like *"line GUIDs are the editing primitive"* and *"every proposal declares its agent of origin."*

The promotion principle:

> Promote lessons to the right layer, not just the nearest one. When you fix a bug, the post-mortem question is: *"where does this lesson belong?"* Often the answer is all three layers — a project-specific rule, a generic pattern at the stack, AND a universal skill or foundation. This derives from Foundation E3 — the foundational layer is small, and most lessons are operational; but a lesson trapped at the project layer that should have promoted to the stack or universal layer is wasted evidence and weakens future cross-project triangulation.

For PrizmForge: as your agents find recurring patterns in third-party repos, the question is whether each pattern is project-specific to that repo (project layer), generally applicable to repos of that shape (stack layer), or universal to all code (universal layer). Without the layering, every pattern gets recorded at the same depth and the corpus loses the ability to distinguish *"this one project does X"* from *"every project of this shape does X."*

Multi-project tools especially need this discipline. Without it, lessons learned in repo A get re-discovered in repo B because there's no mechanism to elevate them between project-instances.

Each concept below is anchored to which layer(s) it operates at.

---

## 1. Foundations as a doctrinal layer the system actually consults
### (Universal layer)

**What I notice is missing:** PrizmForge has architecture but no *consulted* universal layer — nothing the system references to decide whether a *kind* of change is even legitimate before evaluating the specific change.

**The pattern:** A small enumerated set of foundational invariants. Every rule cites which foundation it derives from. The "Derives from:" anchor is structural — it means a rule that no longer honors its anchor is a regression, not a feature.

**Example chain (excerpt from my stack-layer doctrine):**

> **Historical facts are immutable; current state is a projection.** Every meaningful business fact in this domain has a temporal dimension. The schema must record when each fact became true, when it stopped being true, and what replaced it. Current state — *"is this auction open?"*, *"what's the priority score?"*, *"what's the net profit?"* — is a query against that history, not a column that gets overwritten.

That single principle (derived from **F1** — time has direction) generates a cascade of concrete rules: no hard deletes, lifecycle transitions are events with timestamps not labels, cached aggregates carry an as-of timestamp, corrections are events not overwrites. Each can be cited; each can be tested; each fails CI when violated.

**Why it would help PrizmForge:** Your Reviewer currently decides *"is this change OK"* with no enumerated framework. Foundations give it a checklist that's also queryable from the classifier in §3 below. Without foundations, *"doctrine names the answer"* (criterion 1 of the classifier) is always false and everything routes to manual review.

The transplantable concept isn't a specific list of foundations — it's *that there is one, written down, with derivation anchors, that the system mechanically references*.

### What a foundation actually looks like — F1 as worked example

Listing F1-F3 and E1-E3 as headlines (the way I did at the top of this writeup) is shorthand. The actual structure of each foundation in my universal-layer doctrine has six fields. F1 fully expanded:

> **F1. Time has direction**
>
> - **Statement**: Past events cannot be unmade. Causality flows from earlier to later. What was true at a given moment remains true about that moment forever, even after the world changes.
>
> - **Type**: Physical/Logical.
>
> - **Falsification condition**: Demonstrated retrocausality — an effect that preceded its cause in the same reference frame. Not observed in any domain we operate in.
>
> - **Implies**:
>   - Historical facts are immutable. Records of what happened do not get DELETEd.
>   - Lifecycle transitions are events with timestamps. Status columns are projections of the latest event, not the source of truth.
>   - Audit is the shape of the data, not a feature added on top. The schema must answer "what was true at time T" from its own structure.
>   - Cached aggregates carry an `as_of` timestamp so consumers can decide whether to recompute.
>   - Corrections are events. A fact correction records prior value, new value, reason, timestamp; it never silently overwrites.
>   - Schema migrations are append-only and ledger-tracked. The history of schema evolution is itself a fact subject to F1.
>   - The corpus's own evolution is recorded. Anchor histories on every foundation; conversation records for foundational dialogues.
>
> - **Anchor history**:
>   - 2026-04-28: Elevated. Triggered by a session evaluating TradeDesk's data structure that surfaced multiple §5 schema-discipline violations all tracing back to "current state treated as source of truth" thinking. Multiple existing rules became explicable as instances; the elevation gate was satisfied.
>
> - **AI-dependency note**: None. F1 is independent of AI capabilities.

The structure does three things that a one-liner does not:

1. **The falsification condition makes the foundation testable.** "F1 holds unless we observe retrocausality" is sharper than "time has direction"; it tells readers what would *change my mind* and earns the foundation its bedrock status by exposing the conditions of its possible failure. Foundations without falsification conditions are suspect.

2. **The "Implies" list makes derivation visible.** Every operational rule in the stack and project layers traces back to one of these bullets. When a rule's derivation isn't clear, the rule is suspect — it might be free-floating taste rather than a derivation from the foundation it claims.

3. **The anchor history makes the foundation a temporal artifact, not eternal truth.** Per the hypothesis posture above, the foundation was elevated at a specific moment for specific reasons; it can be demoted under cross-project evidence. The history makes that possibility visible to every reader.

For PrizmForge: adopting the six-field structure for your own foundations (if you choose to declare them) means every reading agent sees not just *what* the foundation claims but *what would prove it wrong*, *what derives from it*, and *when and why it was added*. This is the structural difference between a rule that gets followed because it's written down and a rule that gets followed because the reader has independently verified its derivation still holds.

---

## 2. "Audit is the shape of the data"
### (Universal F1 → stack-layer enforcement)

**What I notice is missing:** PrizmForge's proposal lifecycle is `pending → approved/rejected` with status fields. That's *labels*, not *events*. When a proposal gets rejected, you know it's rejected; you don't have a queryable history of *why*, *who reviewed it*, *what evidence*, *what came before*.

**The universal principle (F1):** History must answer *"what was true at time T"*. Status fields that get overwritten erase the answer; append-only event logs preserve it.

**The stack-layer enforcer:** Every meaningful state change writes a row to an audit table in the same transaction. The substrate in my code is `fact_corrections`:

```sql
CREATE TABLE fact_corrections (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    domain TEXT NOT NULL
        CHECK(domain IN ('auction_item', 'inventory_item', 'auction')),
    auction_item_id INTEGER REFERENCES auction_items(id) ON DELETE CASCADE,
    inventory_id INTEGER REFERENCES inventory(id) ON DELETE CASCADE,
    auction_id INTEGER REFERENCES auctions(id) ON DELETE CASCADE,
    fact_name TEXT NOT NULL,
    prior_value TEXT,                    -- JSON-encoded, lossless round-trip
    new_value TEXT NOT NULL,             -- JSON-encoded
    reason TEXT NOT NULL,
    confidence TEXT NOT NULL CHECK(confidence IN ('high', 'medium', 'low')),
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    created_by TEXT
);
```

The corresponding principle in my project layer (CLAUDE.md §1):

> **Corrections are events, not overwrites.** Record prior value, new value, reason, confidence, timestamp; never silently overwrite.
>
> **Decision trigger**: before writing any UPDATE that replaces an existing value in a meaningful business column, pause and ask: *"Am I overwriting a prior value that some future reader might want to know about?"* If yes, write a `fact_corrections` row in the same transaction.

And the structural enforcer that closes the principle/enforcer gap — an architecture invariant test (see §4 for the full pattern):

```python
class TestUpdateRequiresFactCorrection(unittest.TestCase):
    """Functions that UPDATE meaningful business columns must also
    leave an audit trail."""
    # Any function with an UPDATE on MEANINGFUL_BUSINESS_COLUMNS must
    # also INSERT into AUDIT_TABLES in the same function body.
    # Allow-list with inline justification per entry; ratchet pattern.
```

**Why it would help PrizmForge:** Apply the same pattern to your proposal lifecycle. Instead of `proposals.status = 'rejected'`, you'd have `proposal_events(proposal_id, prior_status, new_status, reason, evidence, actor, created_at)`. Now you can answer: *"What kinds of changes get rejected most? By which reviewers? For what reasons? Is there a pattern?"* Today that question has to be reconstructed from logs (if at all); with the event-log shape it's a single query.

This is the substrate everything else below (trust ratchet, retrospection, learning from rollbacks, System Reviewer) sits on. Without it those features are bolted on; with it they're natural readings of the schema.

**Stack-layer note:** Since PrizmForge is Python+SQLite, the `fact_corrections`-style table transplants nearly verbatim. The choice of which columns to recognize as "meaningful business columns" is project-layer; the enforcer pattern is stack-layer.

---

## 3. Classifier + audit lane + trust ratchet, as one coherent system
### (Stack layer)

**What I notice is missing:** PrizmForge's Reviewer is a *uniform gate* — every proposal pays the same review cost regardless of risk or repeatability. This is the failure mode every uniform-gate system eventually hits: review becomes the bottleneck, or the reviewer rubber-stamps to keep up, or both.

**The pattern:** Three coupled stack-layer mechanisms that together implement adaptive routing without abandoning safety.

### 3a. The classifier

A finding is **agent-resolvable** if and only if all four hold (these criteria are stack-layer; the doctrine they consult is project-layer):

1. **Doctrine names the answer.** A clause in the project doctrine unambiguously specifies the fix shape.
2. **A pattern exists to mirror.** The codebase or pattern library contains at least one prior implementation of this fix shape. Greenfield work without precedent does not satisfy this criterion.
3. **Verification is mechanical.** An invariant test, integrity check, or test suite verifies correctness without subjective judgment.
4. **Being wrong is reversible.** Contained in code or schema; `git revert` undoes it; doesn't commit money / publish customer-facing content / delete history / modify security or access controls.

A finding is **user-required** if any of: taxonomy decision, calibration against physical reality, business priority, doctrine change, high-stakes irreversible action.

Default on the boundary: when fewer than four agent-resolvable criteria pass AND no user-required trigger clearly fires, route to user. Conservative bias is preserved at the ambiguous boundary, which is the right place for it.

### 3b. The audit lane (`auto_resolutions`)

```sql
CREATE TABLE auto_resolutions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    resolved_at TEXT NOT NULL DEFAULT (datetime('now')),
    finding_source_type TEXT NOT NULL CHECK(
        finding_source_type IN (
            'dissonance', 'architecture_proposal',
            'integrity_violation', 'lesson_candidate'
        )
    ),
    finding_source_id TEXT NOT NULL,
    change_summary TEXT NOT NULL,
    commit_sha TEXT NOT NULL,
    tests_passed_before INTEGER,
    tests_passed_after INTEGER,
    governing_principle TEXT NOT NULL,
    classifier_criteria_met TEXT NOT NULL,   -- JSON: which criteria fired
    rolled_back_at TEXT,
    rollback_reason TEXT
);
```

Findings classified agent-resolvable that the agent acts on produce one row here. Append-only per F1. The only permitted mutation is `rolled_back_at + rollback_reason`, populated by a post-revert hook when the user reverts the agent's commit.

Surfacing during the bootstrap window: a daily digest appended to a morning briefing under an "Auto-resolved overnight" heading. One line per resolution: source, change summary, commit reference, governing principle. The user scans, doesn't approve item-by-item. Anything that looks wrong gets reverted; the post-revert hook populates `rolled_back_at` and the trust ratchet decays accordingly.

### 3c. The trust ratchet

Trust is keyed on *change shape*, not actor: a fingerprint of `(finding_source_type, governing_principle, change_pattern)`. When accepted ≥ N (initial N=5) and reverts = 0 for that shape, future resolutions of that shape stop appearing in the daily digest. Any revert event decays trust to zero for that shape and re-engages surfacing.

A shape can earn trust, lose it on a regression, and earn it back. The full history is preserved per F1; the ratchet's current state is a projection over that history, not an overwrite.

**Why this would help PrizmForge:** You have `agent_profiles` tracking *per-agent* trust (token efficiency, feedback value). Per-agent trust is too coarse — the same agent making a soft-void cleanup vs. a money-changing edit shouldn't get one number. Per-shape trust lets the system safely accelerate on well-understood change shapes while still gating novel ones, and it survives agent turnover (a new agent can immediately benefit from accumulated trust on well-understood shapes).

The three pieces compose: classifier decides routing → audit lane records outcomes → trust ratchet reads the audit lane to recalibrate routing. Each piece is meaningful alone; together they're a system. **All three are stack-layer mechanisms** — the criteria, the schema, the ratchet algorithm — and would transplant directly to PrizmForge's Python+SQLite substrate.

---

## 4. Design-time pre-flight + invariant tests + lessons loop
### (Stack + project layers)

**What I notice is missing:** PrizmForge governs by *runtime gate* (the Reviewer reads each proposal). One layer. A clever proposal can social-engineer the Reviewer; a Reviewer can have a bad day; an off-distribution proposal can pass review by being unprecedented.

**The pattern:** Three independent layers — design-time, structural, retrospective. Each is an enforcer for a different failure mode.

### 4a. Design-time pre-flight (project layer)

Before any non-trivial change, the agent must answer five questions in a code comment, commit message, or session log:

1. **What doctrine sections govern this change?** If you can't name at least one, either the change is doctrinal-orthogonal (rare) or you don't yet understand what the change is. Walk back to understanding before continuing.
2. **What's the audit trail?** What event row does this change leave behind? If the answer is "none," that's almost certainly an F1 violation in the making.
3. **What pattern in the project pattern library does this resemble?** If a pattern matches, mirror its fix shape unless you have a specific reason to diverge.
4. **What invariant test prevents the next instance of this kind of bug?** If the answer is "none yet," that's a candidate to add now.
5. **Is there a tension between doctrine and what's expedient right now?** If you're noticing a rule the change would bend on local-view grounds — *"this is just 7 lines, the spirit of the rule allows it"* — that noticing is a red flag, not a green light. Name the tension explicitly to the user before resolving it.

Each non-trivial change records the answers somewhere durable. The point isn't paperwork; it's that the *act of answering* the questions catches violations before they enter the code.

### 4b. Architecture invariant tests (stack layer)

Structural assertions that fail CI if the codebase drifts from doctrine. Example:

```python
class TestUpdateRequiresFactCorrection(unittest.TestCase):
    """Functions that UPDATE meaningful business columns must also
    leave an audit trail."""

    MEANINGFUL_BUSINESS_COLUMNS = {
        "current_stage", "status", "decision",
        "sale_price", "purchase_price", "buyers_premium",
        "title", "description", "condition_grade", "category_id",
        "auction_item_id", "inventory_id", "signature_id",
        # ... full list with inline rationale per entry
    }

    AUDIT_TABLES = {
        "fact_corrections", "pipeline_events",
        "ai_identifications", "photo_sufficiency_evaluations",
        "match_suggestion_outcomes", "reprice_outcomes",
        "lesson_candidates",
        # ...
    }

    # Allow-list: ratchet that bakes in current legitimate exceptions
    # with inline justification per row. Additions are blocked; removals
    # (fixes) ratchet the baseline down.
    _KNOWN_ALLOWED = {
        ("integrity_checks.py", "api_lesson_candidates"):
            "LEGITIMATE — decided_at + decided_by + decision_notes "
            "ARE the audit (lifecycle-transition pattern, F1).",
        # each entry must carry an inline justification
    }

    def test_no_unaudited_updates(self):
        for file_path in handler_files():
            for fname, cols in find_meaningful_updates(file_path):
                if (file_path.name, fname) in self._KNOWN_ALLOWED:
                    continue
                self.fail(
                    f"{file_path.name}:{fname} UPDATEs {cols} "
                    f"without writing to an audit table. "
                    f"See doctrine §1's decision trigger."
                )
```

The `_KNOWN_ALLOWED` ratchet pattern is the key insight: bake in the current state as a baseline, block additions, ratchet the baseline down as fixes land. New code that violates the invariant fails CI immediately; existing violations are tracked and reduced over time without forcing a big-bang cleanup before the test can ship.

The current invariants in my project:

- `TestUpdateRequiresFactCorrection` — every UPDATE on a meaningful column writes to an audit table
- `TestMergeRequiresContentUniqueness` — merge-style operations check content uniqueness before re-pointing FKs
- `TestComputedValueRequiresAsOf` — cached aggregate columns either have an `_as_of` companion or a documented refresh function
- `TestAIOutputRequiresVerification` — AI API callers don't write directly to authoritative business columns; they route through verification surfaces
- `TestHtmlHandlersResolveInJs` — every HTML `onclick=...` references a JS function that actually exists (closes a class of cross-file coupling bugs)

### 4c. The lessons loop closure (project + stack)

`lesson_candidates` rows get created by integrity checks when they detect repeated violation patterns:

```sql
CREATE TABLE lesson_candidates (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    detected_at TEXT NOT NULL DEFAULT (datetime('now')),
    governing_principle TEXT NOT NULL,
    distinct_check_count INTEGER NOT NULL,
    distinct_check_ids TEXT NOT NULL,        -- JSON list
    total_violation_count INTEGER NOT NULL,
    window_days INTEGER NOT NULL,
    -- AI-drafted at creation time, user reviews/edits:
    suggested_invariant TEXT,
    suggested_doctrine_update TEXT,
    status TEXT NOT NULL DEFAULT 'pending'
        CHECK(status IN ('pending','accepted','rejected','suppressed','duplicate')),
    decided_at TEXT,
    decided_by TEXT,
    decision_notes TEXT,
    -- Links to the artifacts generated when accepted:
    invariant_test_path TEXT,
    invariant_test_generated_at TEXT,
    pattern_library_entry TEXT          -- 'P00N' anchor in PATTERNS.md
);
```

When the user accepts a candidate, a stub generator emits a draft invariant test the user reviews and commits, plus a stub entry in the pattern library. The loop:

```
detection (integrity check)
  → candidate row (with AI-drafted suggestion)
    → user accepts/rejects
      → if accepted: invariant test stub + pattern entry generated
        → user completes + commits
          → CI prevents the next instance of this bug shape
            → pattern entry surfaces it for the next §9.0 pre-flight
```

The loop is closed without a human running it manually. Detection and prevention infrastructure compound automatically.

**Why this would help PrizmForge:** Right now if your Reviewer rejects a proposal for a reason that recurs, that knowledge lives in (a) the Reviewer's prompt and (b) maybe a comment on the rejected proposal. The next agent doesn't know. With the invariant tests + pattern library, recurring rejection reasons become structural prevention — the next instance can't even be proposed because CI catches it first. Prevention compounds instead of staying flat.

---

## 5. PATTERNS.md + dissonance ledger — cross-session memory
### (Project layer + elevation to stack layer)

**What I notice is missing:** PrizmForge agents start each session with no memory of what kinds of decisions worked vs. failed in prior sessions (beyond what's in `agent_profiles`). Multi-session memory of *patterns* is a different shape than per-agent stats.

**The pattern:** Two cross-session memory surfaces at the project layer, with an elevation path to the stack layer.

### 5a. PATTERNS.md (the resolved-pattern library)

Append-only project-layer library of recurring bug shapes, fix shapes, governing principles (cited up the stack), and links to invariant tests. Each entry has a stable `P00N` anchor that other docs and tests reference. Example entry:

> **P004 — UPDATE on meaningful business column without audit row**
>
> **Governing principle:** §1 (audit is the shape of the data), F1
>
> **Bug shape:** A function UPDATEs a column tracking a meaningful business fact (price, status, decision, category) without recording the prior value. The history of the fact is silently overwritten.
>
> **Fix shape:** In the same transaction as the UPDATE, INSERT a `fact_corrections` row with prior_value, new_value, reason, confidence.
>
> **Invariant test:** `tests/test_arch_invariants.py:TestUpdateRequiresFactCorrection`
>
> **First seen:** 2026-05-05 (task #50)
>
> **Stack-layer enforcer:** [link to skeleton-level invariant once promoted]

### 5b. Dissonance ledger (the *unresolved* tensions)

Different shape: not "what we figured out" but "what's still in tension." Open dissonances are *signal of system reach*, not technical debt. The tension-holding principle:

> Encountering competing valid concerns — between two doctrines, between doctrine and deadline, between two foundations — is itself a sign that the system has the resolution to perceive multiple concerns at once. A simpler system has fewer tensions because it perceives less. Holding the tension is the work; collapsing it via expedience is the failure. The mature stance when two principles pull in opposite directions is to **name the tension explicitly to the user, execute per doctrine, and pay the cost the right answer demands**.

**Why this would help PrizmForge:** Multi-agent systems generate dissonance constantly — one agent's recommendation contradicts another's; doctrine A and doctrine B both apply but pull in different directions; a proposal solves one problem at the cost of another. Today that dissonance probably gets resolved silently by the Reviewer's judgment call, and the knowledge of *what tension was held and how it was resolved* is lost. A queryable ledger lets the system *learn from its own tensions* — recurring dissonances are signals that doctrine needs an additional clause, or that a new pattern needs naming.

---

## 6. The two-layer System Reviewer
### (Stack layer — distinct from PrizmForge's proposal Reviewer)

**What I notice is missing:** PrizmForge has a Reviewer that reviews *proposals*. What it doesn't have is a Reviewer that reviews *the whole system* — periodically asks *"does the big picture still hang together? Is anything drifting?"*

This is a different reviewer addressing a different failure mode: silent system drift vs. bad individual proposals.

**The pattern:** Two layers.

**Layer 1 — Deterministic Self-Audit.** Fast, runs in CI:

- Migration completeness: are migration files sequential with no gaps? Does the highest migration number match the declared schema version?
- Contract coverage: what percentage of tables have fact ownership declarations? What percentage of stored computed values have refresh contracts?
- Module health: are any files over the soft limit? Hard limit? Does every module have a corresponding test file?
- Doc-code alignment: do governance docs reference files that still exist? Do declared module responsibilities match what the files actually contain?
- Registry consistency: does every registered handler have a test? Does every declared fact owner resolve to an existing function?
- Dependency graph: circular imports? Modules importing from more than N other project modules (excessive coupling)?

Output: a structured report with pass/fail per check and specific remediation guidance.

**Layer 2 — AI Architectural Review.** Requires judgment. Runs on-demand, on schedule, or as a pre-push hook.

The reviewer collects:
- The governance docs
- The module map (file names, line counts, declared responsibilities)
- The fact ownership registry and computed value contracts
- The dependency graph
- Recent git history
- Layer 1 self-audit results

Then asks an AI (separate from the agents doing modification work) to evaluate:

1. **Architectural coherence.** Are modules still single-domain? Any module accumulating responsibilities outside its declared scope? Subsystems coupling in unintended ways?
2. **Contract compliance.** Data concepts appearing in multiple places but not in the fact ownership registry? Business events whose transaction boundaries look incomplete?
3. **Documentation drift.** Does the governance documentation still match reality? Decisions made in code but never documented?
4. **Fatal flaws.** Step back from the details — does the big picture still make sense? Architectural risks invisible when looking at individual modules?
5. **Coverage guidance.** Where should contracts be added next? Which modules are most likely to harbor undeclared complexity?

Output: a short narrative report (under 500 words) with specific findings and recommendations.

**Why this would help PrizmForge:** Your proposal Reviewer is your *change* gate. The System Reviewer is your *state* gate — it catches the drift that no individual proposal would obviously cause but that accumulates over many proposals. The two roles are independent and both needed; one cannot substitute for the other.

**Derived from E2:** the system's belief that it is consistent with its own doctrine is exactly the kind of belief that cannot be self-validated. The two-layer reviewer is structural triangulation: Layer 1 catches mechanical drift; Layer 2 catches conceptual drift that requires judgment from a perspective that doesn't already share the project's framing.

---

## 7. Data Contracts as declarative registries
### (Stack layer)

**What I notice is missing:** PrizmForge's data shape is implicit — defined by code that operates on it, enforced by the Reviewer at proposal time. There's no declarative registry of *"these are the facts the system holds, this is who owns them, this is what depends on them."*

**The pattern:** Four sub-components, all declarative Python files.

### 7a. Fact Ownership Registry

```python
# contracts/fact_owners.py
FACT_OWNERS = {
    "net_profit": {
        "source": "calculations.compute_net_profit",
        "description": "Sale price minus cost basis, expenses, fees, shipping",
        "storage": "sales.net_profit",          # Optional: if stored as cache
        "refresh": "calculations.recompute_sale_profit",  # Required if stored
    },
    "item_status": {
        "source": "inventory.current_stage",
        "description": "Current pipeline stage for an inventory item",
        "valid_values": ["received", "shelf", "cleaning", "photography",
                         "listed", "sold", "shipped"],
    },
}
```

Tests verify that declared sources exist. When someone asks *"where does net_profit come from?"*, the answer is in one place — not scattered across code comments. The System Reviewer compares the registry against actual code paths to find undeclared secondary sources.

### 7b. Computed Value Contracts

```python
COMPUTED_VALUES = {
    "sales.net_profit": {
        "formula": "calculations.compute_net_profit",
        "inputs": ["sales.sale_price", "inventory.cost_basis",
                   "expenses.*", "config.ebay_fee_pct"],
        "refresh_trigger": "calculations.recompute_sale_profit",
        "mutation_paths": [
            "listing_management_handlers.api_record_sale",
            "ebay_rest_api.sync_order",
            "settings_handlers.api_update_fee_settings",
        ],
    },
}
```

Tests verify that every declared mutation path calls the refresh trigger. If `api_record_sale` is modified and stops calling `recompute_sale_profit`, the test fails. If a new function writes to `sales.sale_price` but isn't listed in `mutation_paths`, static analysis flags it.

### 7c. Transaction Boundaries

```python
BUSINESS_EVENTS = {
    "record_sale": {
        "description": "Recording a completed sale",
        "tables_touched": ["sales", "inventory", "ebay_listings",
                           "listings", "pipeline_events"],
        "handler": "listing_management_handlers.api_record_sale",
        "atomicity": "required",
    },
}
```

Tests verify the handler actually touches all declared tables in a single transaction. Partial-state violations are caught structurally.

### 7d. Schema Introspection

Tests that verify the database schema matches structural policies at the DDL level:

- Every FK column has an explicit `ON DELETE CASCADE` or `ON DELETE RESTRICT`.
- Every status/stage column has a `CHECK` constraint.
- No table has columns that duplicate a concept owned by another table (cross-referenced with the Fact Ownership Registry).
- No JSON columns store data that's JOINed on, filtered by, or aggregated across rows.

**Why this would help PrizmForge:** Your proposal Reviewer enforces these properties one proposal at a time. The registries enforce them *declaratively* — they're the source of truth, and tests fail when reality drifts from declaration. The two layers compose: the registries are the contract, the proposal Reviewer ensures new proposals honor the contract, the System Reviewer (§6) checks whether the contract still matches reality, and structural tests fail when any of those gaps open.

Adaptability: contracts start sparse. On day one you might declare three fact owners and one business event. The framework doesn't require completeness — it requires that whatever IS declared is mechanically verified. Coverage grows organically.

---

## 8. The elevation protocol
### (Cross-layer infrastructure)

**What I notice is missing:** PrizmForge has no mechanism for promoting lessons learned in one repo to apply to other repos. Each session starts from scratch (modulo agent_profiles).

**The pattern:** Lessons start at the project layer where they're observed. They earn promotion to the stack layer (and possibly the universal layer) based on evidence — primarily, recurrence across independent projects.

The criteria for promoting a project-layer pattern to the stack layer:

1. **N ≥ 2 independent project instances surface the same pattern.** Independence matters — two instances in two repos of fundamentally different shape count more than two instances in two forks of the same repo.
2. **The bug shape is fully determined by the stack choice, not by what the project does.** A pattern that's specific to "this domain" stays at the project layer. A pattern that any project of that stack shape would hit goes up.
3. **The fix shape transplants without project-specific adaptation.** If the fix needs the project's specific schema, it's not stack-layer yet.
4. **A stack-layer enforcer (test, decorator, schema constraint, lint rule) can implement the fix.** If the fix can only be principled-not-enforced, it stays at the project layer until an enforcer is possible.

For PrizmForge as a multi-repo tool, this protocol is central. As your agents find recurring patterns in third-party repos, the question is *"is this just this repo, or every repo of this shape?"* The answer drives where the prevention infrastructure lives — in the third-party repo's project layer, or in PrizmForge's stack layer that injects into every repo it touches.

A worked example from my own work: cross-file static-coupling failures (HTML `onclick="fn()"` references that don't resolve to any JS function definition). First seen in my project (TradeDesk) as eleven concrete instances across three sibling shapes in one bug batch. The project-layer entry lives in `TradeDesk/PATTERNS.md` P014. The stack-layer elevation (a sibling test pattern that any Python+SQLite+HTML+JS project inherits) lives in the skeleton's `FOLLOWUPS.md` item #9, ready for the next project that bootstraps from the skeleton. Two layers, cross-referenced, both carrying their own work.

---

## 9. Stack-layer patterns from FOLLOWUPS worth direct attention

The skeleton's FOLLOWUPS.md is the staging ground for items destined to be stack-layer enforcers. A few that I think apply directly to PrizmForge:

**Static coupling invariants (FOLLOWUPS #9).** Three sibling tests: JS-IDs-resolve-in-HTML, JS-API-endpoints-resolve-in-server, HTML-handlers-resolve-in-JS. All use the `_KNOWN_ALLOWED` ratchet pattern. Bug class is fully determined by the stack (HTML+JS+Python+SQLite). Catches a class of bugs that produce zero server-side exception, which is the structural fact that motivates filing at the static-invariant level. PrizmForge probably doesn't have a JS frontend yet, but the *pattern* — static cross-boundary coupling enforced at CI — generalizes to any cross-file references your system makes (e.g., between proposal text and the file paths it references; between agent_prompts.json and the agents that consume it).

**Background-process git-lock coordination (FOLLOWUPS #11).** Any project with a background process touching git will eventually orphan a `.git/index.lock`. The skeleton's proposed fix is a `cowork_git_quiesce()` context manager with explicit acquire/release, a watchdog for orphaned locks, and a user-priority sentinel file the user drops when they're about to commit. PrizmForge is a system where multiple agents may touch git concurrently — this is directly applicable, and the fix is small.

**Reflective-layer freshness audit (FOLLOWUPS #12).** This is the gem. The principle:

> Artifacts of truth exist; nothing forces downstream readers to consult them at the moment of use. The fix at every layer is a structural enforcer at the consumer's decision moment — not another principle entry.

For PrizmForge specifically: your Reviewer reads each proposal in isolation. The system state at the time of review (current contracts, current invariants, current rejection patterns, current trust ratchet, recent rolled-back resolutions) is the *substrate* the Reviewer's claims must reconcile against. Without a reconciliation pass, the Reviewer can approve a proposal whose claims have been falsified by recent system state — the artifacts of truth exist but nothing forced the Reviewer to consult them.

The skeleton's proposed mechanism: a reconciliation pass that runs before any consumer acts on a reflective surface (briefing, ledger, status field, proposal review). For each open claim that references substrate, the pass resolves the reference against current substrate and writes a `superseded_by` field if the reference's current state falsifies the claim. Cheap, idempotent, runs before any consumer acts. The reconciliation output is the projection; the substrate is ground truth.

Applied to PrizmForge: before the Reviewer evaluates a proposal, a reconciliation pass would check whether anything in the proposal's stated assumptions has been falsified since it was drafted (substrate changed, a referenced fact owner was renamed, a referenced invariant test was added, a related proposal was rolled back). The Reviewer sees the freshness state alongside the proposal content.

---

## 10. AI-dependency tracking
### (Cross-cutting; universal-layer practice; uniquely critical for PrizmForge)

**What I notice is missing:** PrizmForge is a multi-LLM tool — OpenAI, Gemini, and others by design. Each model has its own behavior surface: how it interprets ambiguous prompts, what it treats as authoritative, what it tends to over-commit to, what subtleties it preserves vs. flattens. Your architecture has principles, doctrine, prompts, and rules — but no mechanism that records *which of these depend on a specific AI's behavior* and therefore need re-validation when models change.

This is not a hypothetical concern. From my universal-layer doctrine on E2 (the convergence-as-triangulation foundation):

> The same Claude instance reasoning across projects is a major shared-source factor. As AI capabilities and defaults change across model versions, the convergence pattern may shift; outputs that converged with one model version may not with another.

When a model upgrade ships and a previously-reliable principle starts producing different outcomes, the failure mode is *quiet correctness loss* — the system keeps running, claims keep getting made, but the principles those claims rely on no longer hold. Without dependency tracking, you find out when something breaks in production rather than when the model changes.

**The pattern:** Every operational rule that depends on AI behavior records an explicit `AI-dependency note` field. The note states:

1. **Which AI behavior the rule depends on.** ("This rule assumes the model preserves the distinction between historical claims and current-state claims when summarizing.")
2. **What model version(s) it was validated against.** ("Validated against Claude Sonnet 4.6 and Claude Opus 4.7; not re-validated for Claude 5.0.")
3. **What would falsify the rule under a new model.** ("If the new model produces outputs where historical claims are flattened into present tense, this rule no longer holds.")
4. **What the fallback is.** ("If the rule fails under a new model, route the affected proposals to user review until the rule is re-derived or replaced.")

The structure is a parallel to the falsification-condition discipline from §1's expanded foundation structure. It applies the same epistemic move (declare what would prove the rule wrong) specifically to AI behavior.

### Why this matters more for PrizmForge than for most projects

Three structural reasons:

**1. Multi-LLM architectures multiply the dependency surface.** A single-model project has one AI behavior to track; PrizmForge has at least two (OpenAI + Gemini per the README), and the rules that work with one model's behavior may not work with another's. Without explicit dependency tracking, the cross-model differences become emergent rather than enumerated.

**2. AI-consuming-doctrine is the entire stack.** Per the hypothesis-posture meta-principle: AI agents read your doctrine, your Reviewer reads your doctrine, future agents read your doctrine as it appears in past proposals. Every read is an opportunity for a model upgrade to silently change how the doctrine is interpreted. The dependency note is the structural safeguard.

**3. Cross-model corroboration is your scaling lever.** If you're already running OpenAI + Gemini in parallel, you have an existing substrate for *independent triangulation* across models — which is the strongest evidence E2 admits. Recording which rules require cross-model agreement vs. which can be validated against one model alone is the structural move that turns the multi-LLM design from a redundancy into an evidentiary advantage.

### What a worked example looks like

Adapted from the proposal classifier in §3 above. The classifier's four agent-resolvable criteria depend on an AI agent making consistent judgments about whether doctrine "unambiguously specifies" a fix shape — that judgment is itself model-dependent.

```markdown
## Classifier criterion 1: Doctrine names the answer

**Rule:** A finding is classified agent-resolvable on criterion 1 if and only if the
project doctrine contains a clause that unambiguously specifies the fix shape for this
class of change.

**Implementation:** The classifying agent reads the relevant doctrine sections and
returns a boolean. If the agent's confidence is below a threshold or the doctrine
sections are ambiguous, the boolean is False and the finding routes to user review.

**AI-dependency note:**
- Depends on: The classifying model preserving the distinction between "doctrine
  describes the fix" vs. "doctrine could be interpreted to suggest the fix." A model
  that over-commits in ambiguous cases will produce more False positives on this
  criterion and more incorrect auto-resolutions.
- Validated against: Claude Sonnet 4.6 and Claude Opus 4.7. Cross-model agreement
  between Claude and GPT-4 on a sample of 50 ambiguous findings: 84%.
- Falsification: If cross-model agreement drops below 70% on a calibration set, the
  criterion is suspect under the new models — route all findings to user review
  until the prompt is re-derived for the new model surface.
- Fallback: Manual review for everything classified agent-resolvable until the
  cross-model agreement is re-validated.
```

This adds 8-10 lines per rule that has AI dependencies. Most operational rules don't have them (mechanical CI tests don't depend on any model behavior). The rules that DO have AI dependencies are exactly the ones that need explicit tracking — and they're a minority. The cost is small; the failure-mode-coverage is large.

### How this composes with the rest

The AI-dependency note is consumed by:

- **The classifier (#3):** A criterion whose validation depends on a model behavior that's currently flagged-for-review routes findings to user automatically until re-validation.
- **The trust ratchet (#3):** Shapes that depend on AI behavior carry an additional invalidation trigger: model change. A model upgrade decays trust on AI-dependent shapes back to zero pending re-validation, even without rollback events.
- **The System Reviewer (#6):** Layer 2 (AI architectural review) explicitly evaluates whether AI-dependency notes are current. A rule with an "AI-validated against Claude 3.5 Sonnet" note in a system now running Claude 4 is a finding the Reviewer surfaces.
- **The elevation protocol (#8):** A rule cannot promote to universal layer if it has AI-dependencies — universal-layer rules must be AI-independent. AI-dependent rules cap at the stack or project layer. This is the structural enforcement of foundation E3 (the foundational layer must be aggressively small) applied to the cross-cutting case of AI behavior.

For PrizmForge: this single discipline closes a gap that no other concept in this writeup addresses. The Reviewer can catch bad individual proposals; the integrity framework can catch drift in data shape; the System Reviewer can catch architectural drift; the trust ratchet can catch rollback patterns. But *silent correctness loss from model upgrade* requires its own mechanism, because no observable in the existing system is changing — the principles are static, the data is unchanged, the proposals look normal, and yet the system is now making decisions on premises that no longer hold.

---

## How this composes

Cherry-picking individual pieces loses the property that they reinforce each other. The layering makes the composition explicit:

**Universal layer (foundations) → consulted by:**
- The classifier (#3), which checks if doctrine names the answer
- The §9.0 pre-flight (#4), which asks which foundations govern the change
- The pattern library (#5), whose entries cite which foundation they implement
- The System Reviewer (#6), which evaluates whether the system still honors its anchors

**Stack layer (skeleton enforcers) → reads from:**
- The fact ownership / computed value / business event registries (#7)
- The audit lane (#3) and trust ratchet (#3)
- The static-coupling and process-coordination invariants (#9)

**Project layer (CLAUDE.md, PATTERNS.md, dissonance ledger) → consulted by:**
- The §9.0 pre-flight (#4), which asks which project patterns the change resembles
- The classifier (#3), which checks if a pattern exists to mirror
- The lessons loop (#4), which generates new project-layer entries from accepted candidates

**Elevation protocol (#8) → moves patterns between layers based on evidence.**

**AI-dependency tracking (#10) → cross-cutting against all of the above.** Every rule at every layer that depends on AI behavior carries an explicit note; model upgrades trigger re-validation; cross-model agreement is the evidentiary anchor for AI-dependent claims. This composes with the trust ratchet (model change decays trust on AI-dependent shapes), the System Reviewer (Layer 2 evaluates whether AI-dependency notes are current), the classifier (criteria with stale validation route findings to user), and the elevation protocol (AI-dependent rules cap at the stack or project layer; only AI-independent rules can promote to universal).

If I had to name one **starting move** that opens the door to the rest: declare the three meta-stances as named architectural pillars in your governance doc, alongside your existing safety pillar — *prefer enforcers over principles* (closes the principle-vs-runtime gap), *the hypothesis posture* (closes the static-doctrine vs. evolving-substrate gap), and *AI-dependency tracking* (closes the silent-model-upgrade gap). Once those are framed as load-bearing, the rest of the structure becomes implied requirements rather than optional additions. Without them, each piece looks like a feature; with them, the absence of any one piece becomes a visible gap.

From my project doctrine:

> **Self-improvement is a central pillar of the architecture, not a feature bolted on.** The codebase's job is not just to do work — it is to detect its own blind spots, route detected violations to the principles they violate, recognize recurring patterns across violations, and update its own preventive infrastructure (architecture invariant tests, doctrine entries, the agent's pattern library) so the same class of bug cannot ship a second time. The integrity framework provides runtime detection; it must be paired with design-time prevention (a §9.0 doctrinal pre-flight + architecture invariants) and cross-session memory (a queryable project-specific pattern library) so the loop closes without a human running it manually.

---

## Tensions worth naming explicitly

In the spirit of #4 question 5, six places where the transplant isn't clean:

1. **The classifier presumes the system has doctrine to consult.** You'd need to define PrizmForge's load-bearing principles before the classifier produces useful routing. Bolting on the classifier without first defining doctrine would route everything to manual review (criterion 1 never satisfied).

2. **The trust ratchet assumes the user reverts when the agent is wrong.** PrizmForge has a Reviewer that catches errors before they merge — that's a different signal than a user revert and may need a different ratchet calibration. "Reviewer-rejected" and "user-reverted-after-merge" are both negative signals but carry different evidence weight.

3. **The single-user vs. multi-agent shift.** TradeDesk is single-user; PrizmForge is multi-agent. Some of these patterns assume a single source of "user judgment." With multiple agents producing findings and a separate Reviewer producing decisions, *"who is the user"* in `decided_by` becomes a richer question — possibly an opportunity (you can track decisions per actor) but not just a copy-paste.

4. **The three-layer architecture has a fourth layer when applied to PrizmForge.** PrizmForge is a *meta-tool* that injects into third-party repos. So the layers become: universal foundations → PrizmForge's stack layer → PrizmForge's own project layer → the third-party repo's project layer. The doctrine you inject into a target repo is a separate question from the doctrine you hold about PrizmForge itself. The skeleton's three-layer model needs an extra mental layer for your case.

5. **Enforcers everywhere is the goal; getting there is gradual.** *"Prefer enforcers over principles"* is the right stance, but you can't enforce everything on day one. Some principles will remain principles until the right enforcer is invented. The discipline is to *evaluate every principle for enforcer potential* on entry — not to delay every principle until its enforcer exists. The ratchet pattern (baseline current state, fail forward on regressions, ratchet down on fixes) is the structural answer to this tension.

6. **AI-dependency tracking imposes a cost the project layer has to bear.** Every AI-dependent rule needs the dependency note (~8-10 lines per rule), every model upgrade triggers a re-validation cycle on those rules, and the cross-model agreement calibration is itself a non-trivial ongoing test surface. The cost is real; the rationale is "the alternative is silent correctness loss, which is worse than visible re-validation work." But: a project that's still proving its architecture works at all will find this discipline a heavy lift. The honest answer is the dependency notes can start sparse and grow — exactly the same maturity-progression shape as the Data Contracts subsystem (#7) or the trust ratchet (#3). Day one might be three AI-dependency notes; mature state might be twenty. The framework doesn't require completeness; it requires that whatever IS declared gets re-validated when models change.

---

## Close

That's the full take. PrizmForge is solving a more general problem than TradeDesk (multi-agent, third-party repos, line-GUID precision) so the pieces wouldn't transplant verbatim — the *shapes* would need adaptation. But the shapes are battle-tested; I've shipped them, hit the failure modes they prevent, watched the loop close, and felt the cost of the missing pieces before they existed.

The deeper move I'm offering isn't any single concept — it's the *layered framing held in a particular posture*. Once doctrine has explicit scope (universal / stack / project), once enforcers are preferred over principles, once doctrine is held as hypothesis rather than authority, once AI-behavior dependencies are tracked rather than assumed, once lessons promote to the right layer based on evidence — the architecture becomes self-maintaining. The integrity framework detects; the classifier routes; the audit lane records; the trust ratchet calibrates; the pattern library memorizes; the invariant tests prevent; the System Reviewer audits; the elevation protocol promotes; the AI-dependency notes flag model changes for re-validation; the foundations anchor. Each piece does one thing; together they're a system that gets better at being itself without constant human intervention, and survives the model upgrades that would otherwise silently erode its premises.

Happy to discuss any of this — by issue reply or whatever channel. No expectation of adoption.
