# Doctrine excerpt — the two-layer System Reviewer

Place this in your governance doc as the section governing periodic system-wide review.

---

## The System Reviewer — two layers

**Derives from:** Foundations [E2](../../01_foundations/E2_convergence_is_triangulation.md) (the system's belief that it is consistent with its own doctrine is exactly the kind of belief that cannot be self-validated; two-layer triangulation is the structural form) and [E1](../../01_foundations/E1_corpus_is_hypothesis.md) (the reviewer's findings are evidence that the project's working hypotheses are still working; absence of findings is informative but not conclusive).

The System Reviewer is the periodic-audit role, distinct from any per-proposal reviewer. The per-proposal reviewer evaluates one change at a time and approves/rejects based on whether the change is locally good. The System Reviewer evaluates the whole system periodically and asks *"does the big picture still hang together?"*

Both roles are needed. Neither substitutes for the other.

### Layer 1 — Deterministic Self-Audit

Fast, runs in CI, catches mechanical mistakes:

- **Migration completeness.** Are migration files sequential with no gaps? Does the highest migration number match the declared schema version? Does the fresh-install path (running all migrations from empty) produce the same schema as the upgrade path (running only new migrations from current)?

- **Contract coverage.** What percentage of tables have fact ownership declarations? What percentage of stored computed values have refresh contracts? What percentage of business events declare their atomicity scope? (Reports coverage; doesn't fail on low coverage — that's Layer 2's judgment.)

- **Module health.** Are any files over the soft limit (500 lines)? The hard limit (800 lines)? Does every module have a corresponding test file? Are there modules that lack docstrings or category tags?

- **Doc-code alignment.** Do governance docs (CLAUDE.md, BUSINESS.md) reference files that still exist? Do declared module responsibilities match what the files actually contain? Are there file moves or renames that broke cross-references?

- **Registry consistency.** Does every registered handler have a test? Does every declared fact owner resolve to an existing function? Does every business event's handler exist?

- **Dependency graph.** Are there circular imports? Are there modules that import from more than N other project modules (excessive coupling)? Are there modules that are never imported anywhere (dead code candidate)?

**Output:** a structured report with pass/fail per check and specific remediation guidance. Failures in CI block the merge; warnings (low coverage, soft-limit violations) surface in the daily digest.

### Layer 2 — AI Architectural Review

Requires judgment. Runs on-demand, on a schedule, or as a pre-push hook (Layer 2 advisory; Layer 1 blocking on pre-push).

The reviewer collects:

- The governance docs (CLAUDE.md, BUSINESS.md, project foundations, etc.)
- The module map (file names, line counts, declared responsibilities, last-modified dates)
- The fact ownership registry, computed value contracts, business event declarations
- The dependency graph
- Recent git history (what changed since last review)
- Layer 1 self-audit results

Then asks the AI to evaluate:

1. **Architectural coherence.** Are modules still single-domain? Are any modules accumulating responsibilities outside their declared scope? Are subsystems coupling in unintended ways?

2. **Contract compliance.** Are there data concepts that appear in multiple places but aren't in the fact ownership registry? Are there business events whose transaction boundaries look incomplete?

3. **Documentation drift.** Does the governance documentation still match reality? Are there decisions that were made in code but never documented?

4. **Fatal flaws.** Step back from the details — does the big picture still make sense? Are there architectural risks that are invisible when looking at individual modules?

5. **Coverage guidance.** Where should contracts be added next? Which modules are most likely to harbor undeclared complexity?

**Output:** a short report (under 500 words) with specific findings and recommendations. Not a checkbox list — a narrative assessment. Findings route to the user's decision queue; the user decides what to act on.

### Triggering

- `./manage.py review` — on-demand
- Scheduled via cron or CI — weekly or per-milestone
- Git pre-push hook (optional) — runs Layer 1 (fast), blocks push on failures, logs Layer 2 results as advisory

### Why two layers, not one

Layer 1 catches what mechanical analysis can find. Layer 2 catches what mechanical analysis cannot. They're independent in two senses:

1. **Different evidence shapes.** Layer 1 produces deterministic pass/fail signals; Layer 2 produces narrative judgments. A mechanical check that the AI re-evaluates is redundant; the value comes from the AI evaluating things mechanical checks can't.

2. **Different failure modes.** Layer 1 fails on patterns it was written to detect; Layer 2 catches novel patterns that emerged after the deterministic checks were written. Layer 2 is the structural answer to *"what if the wrong thing isn't in any of our checks yet?"*

The two-layer pair is the operational form of E2 — triangulation across genuinely independent dimensions. A single layer is one perspective; two layers from genuinely different angles is triangulation.

### AI-dependency for Layer 2

Per [11_ai_dependency_tracking/](../../11_ai_dependency_tracking/), Layer 2 is AI-dependent. Document the dependency:

- **Depends on:** the model's ability to reason about architectural coherence from a module map + governance docs, without over-claiming patterns that aren't there.
- **Validated against:** specify the model versions Layer 2 was tested against.
- **Falsification:** if cross-model agreement on Layer 2 findings drops below a calibration threshold, Layer 2 outputs are suspect and need re-validation.
- **Fallback:** route findings to user with explicit "Layer 2 model-validation pending" tag; don't auto-act.

Cross-model corroboration is the structural mitigation: running Layer 2 through two independent models and surfacing only findings both agree on is the strongest evidence form per E2. Adds cost; worthwhile when Layer 2 findings drive significant action.
