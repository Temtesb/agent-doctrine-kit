# The three-layer architecture

## The structural model

Doctrine isn't monolithic. It lives at three layers with different scopes and responsibilities:

- **Universal layer** — foundational physical/logical and epistemic invariants that apply to any project of any shape. See [01_foundations/](../01_foundations/) for the six foundations.
- **Stack layer** — patterns and enforcers specific to a technology stack (e.g., Python+SQLite, Rust+Postgres, TypeScript+Prisma). What stays true across every project of that stack shape; what an enforcer at this layer prevents in every project that adopts it.
- **Project layer** — rules and doctrine specific to one codebase. Business logic, naming conventions, project-purpose foundations, domain-specific invariants.

Each layer derives from the layer above. A stack-layer rule cites which universal foundation it implements. A project-layer rule cites which stack-layer pattern or universal foundation it specializes.

## The promotion principle

> Promote lessons to the right layer, not just the nearest one. When you fix a bug, the post-mortem question is: *"where does this lesson belong?"* Often the answer is all three layers — a project-specific rule, a generic pattern at the stack, AND a universal skill or foundation. A lesson trapped at the project layer that should have promoted to the stack or universal layer is wasted evidence and weakens future cross-project triangulation.

**Derives from:** Foundation E3 (the foundational layer must be aggressively small). Most lessons are operational; foundations are bedrock; layer-confusion weakens the corpus by allowing operational rules to masquerade as foundations (over-elevation) or by trapping reusable patterns at the project layer (under-elevation).

## Why this matters for agent-governed systems

Two reasons.

**Without layering, every pattern recurs.** An agent system that operates across multiple projects (whether multi-repo by design, or multi-session within one repo) will encounter the same patterns repeatedly. If every pattern is recorded at the project layer, each project re-discovers them. If patterns flow upward through the elevation protocol to the stack layer, the next project inherits them for free.

**Without layering, doctrine bloats.** Every project's CLAUDE.md (or equivalent) accretes rules over time. Without explicit scope, those rules pile up: domain-specific rules sit next to stack-shape rules sit next to universal claims. The reading agent can't distinguish *"this is a deep universal truth"* from *"this is a one-project convention."* The doctrine becomes a flat list, which is the original problem the layering is meant to solve.

Per the smallness discipline (Foundation E3): the foundational layer earns its tininess by promoting only what survives the elevation protocol's adversarial checks. Everything else stays at the stack or project layer. The proportion of insights that elevate to universal foundations should be small over time. If most session insights elevate, the gate is too low.

## What lives where

### Universal layer

**Contents:** F1-F3 (physical/logical foundations), E1-E3 (epistemic foundations), and any future foundations that survive elevation. The elevation protocol itself, the lessons archive, AI-dependency tracking discipline.

**Examples of universal-layer rules:**

- "Time has direction" (F1) → no hard deletes, lifecycle transitions are events with timestamps
- "Mathematics and logic hold" (F2) → single source of truth, atomicity across tables
- "The corpus is a hypothesis, not an authority" (E1) → every rule has a falsification condition and anchor history

**What does NOT belong at the universal layer:**

- Anything stack-specific ("use parameterized SQL" is F2 applied to SQL injection; it's a stack-layer rule)
- Anything project-specific ("auction items must have a purchase_price by month-end" is project doctrine)
- AI-behavior-dependent rules (per AI-dependency tracking, those cap at the stack or project layer)

### Stack layer

**Contents:** Patterns and enforcers specific to a technology stack. Auto-discovered migration system; connection factory abstracting the backend; handler registry; data contract templates; integrity check framework; structured logging; AI client with retry and cost tracking; the System Reviewer's Layer 1 deterministic checks; static-coupling invariants; background-process git-lock coordination; reflective-layer freshness audit; and so on.

**Examples of stack-layer rules:**

- "Every UPDATE on a meaningful business column writes to an audit table" (F1 applied to SQLite mutation patterns)
- "JS handlers in HTML must resolve to a top-level JS function definition" (F2 applied to cross-file coupling in HTML+JS+Python projects)
- "Background processes touching git must use the git-quiesce wrapper" (F1+F3 applied to lock coordination)

**What does NOT belong at the stack layer:**

- Anything universal (F1, F2 themselves are universal; the stack-layer rule is the *application* to the specific stack)
- Anything project-specific (the meaningful_business_columns list is project-defined; the rule that they require audits is stack-shape)

### Project layer

**Contents:** Business logic, project-purpose foundations, domain-specific rules, the project's `PATTERNS.md` of local sightings, the project's specific data contracts (which tables, which fact owners, which business events).

**Examples of project-layer rules:**

- "Auction items have these specific meaningful columns: purchase_price, sale_price, condition_grade, ..." (the list is project-specific; the rule that they require audits is stack-layer)
- "The system's named output goal is three listings per day" (purpose foundation specific to this project)
- "P-014 — Cross-file static coupling fails silently and invisibly" (a project-layer sighting that cites the stack-layer enforcer as its canonical home)

## How to adopt this stance

1. **Audit your existing doctrine.** Walk through it and ask, per rule: *which layer does this belong at?* Most rules will be project-layer. Some will be stack-layer disguised as project-layer (the same rule would apply to any project of your stack shape). A few may be universal-layer disguised as either (the rule is just an application of a deeper foundation).

2. **Re-locate rules that are at the wrong layer.** Stack-layer rules trapped at the project layer are the most common error — they slow down the next project of the same stack shape because the lesson hasn't been promoted. Move them up.

3. **For new rules, ask the layer question at recording time.** *"Is this specific to this project, this stack, or universal?"* The answer determines where the rule lives.

4. **Wire the elevation protocol** ([09_elevation_protocol/](../09_elevation_protocol/)) to formalize the promotion path. The protocol's criteria (multi-project triangulation, anti-collinearity, falsifiability) prevent over-elevation and create a structured path for under-elevation.

5. **Cross-reference between layers.** Every project-layer rule that derives from a stack-layer pattern names that pattern. Every stack-layer pattern that derives from a universal foundation names that foundation. The cross-references are what let the reading agent verify the derivation rather than defer to the rule.

## A fourth layer for multi-repo tools

If your project is a *meta-tool* that injects into third-party repos (e.g., a code-modification agent that operates on external codebases), there's an additional layer to consider:

- Universal foundations
- Your meta-tool's stack layer
- Your meta-tool's own project layer
- The target repo's project layer (the doctrine you inject into the repos you modify)

The doctrine you inject into a target repo is a separate question from the doctrine you hold about your meta-tool itself. The two layers can share or differ. Multi-repo tools that don't distinguish these layers tend to either over-inject (forcing every target repo to adopt the meta-tool's idiosyncratic conventions) or under-inject (failing to enforce stack-layer rules that *every* target repo would benefit from).

## Cross-references

- [01_foundations/](../01_foundations/) — the universal-layer foundations.
- [09_elevation_protocol/](../09_elevation_protocol/) — the operational protocol for moving rules between layers based on evidence.
- [10_followups_patterns/](../10_followups_patterns/) — three concrete examples of stack-layer enforcers, each with project-layer seed evidence and bidirectional cross-references.
- [hypothesis_posture.md](hypothesis_posture.md) — the paired stance; layering becomes meaningful only when each layer is held as hypothesis rather than authority.
- [patterns_local_enforcers_home.md](patterns_local_enforcers_home.md) — the companion principle about where enforcers live and how project-side sightings flow up.
