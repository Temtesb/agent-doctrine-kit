# Doctrine excerpt — the four-criteria elevation gate

Place this in your governance doc as the protocol governing how patterns climb layers.

---

## The elevation protocol

**Derives from:** Foundations [E2](../../01_foundations/E2_convergence_is_triangulation.md) (independent triangulation is the strongest evidence; shared-source bias undermines convergence) and [E3](../../01_foundations/E3_foundations_aggressively_small.md) (the foundational layer must be aggressively small).

A pattern earns promotion from one layer to the next when it passes all four criteria below. The gate is high by design — most candidates resolve to *"this is a derivation we hadn't articulated"* rather than a new foundation or a new stack-layer rule.

### The four criteria

**1. Generative force.** The candidate explains multiple operational rules, not just one.

A candidate that produces only one derived rule is usually *that derived rule*, mis-classified at a higher layer than it belongs. A genuine foundation produces a cascade — when you articulate it, multiple existing rules become explicable as instances. F1 (time has direction) is the canonical example: once articulated, it explains no-hard-deletes, lifecycle-events, cached-aggregate-as_of, schema-migration-ledger, and audit-as-shape-of-data — five operational rules that previously stood alone.

To satisfy criterion 1, the candidate must name at least three operational rules it makes explicable.

**2. Reduction-resistance.** The candidate doesn't already derive from existing foundations.

The default disposition is *"this is a derivation we hadn't articulated."* Most candidates resolve there. Before promoting a candidate, try to derive it from each existing foundation. If you can, the candidate is a derivation; record it at the appropriate layer with the derivation chain documented.

Reduction-resistance means: the candidate explains something the existing foundations *cannot* explain. The test is rigorous — for each existing foundation, write down "this candidate derives from F<n> because..." If every attempt fails, criterion 2 is satisfied.

**3. Falsifiability.** The candidate declares what would prove it wrong.

A foundation without a falsification condition is suspect. The condition makes the foundation testable — *"this holds unless we observe X"* tells readers what would *change my mind* and earns the foundation its bedrock status by exposing the conditions of its possible failure.

F1 has the condition *"demonstrated retrocausality"* — not observed in any domain we operate in, so F1 stands. E2 has the condition *"a demonstrated procedure that produces provably true conclusions through convergence alone"* — Gödel's incompleteness and the problem of induction tell us no such procedure exists, so E2 stands.

A candidate that can't be falsified by any imaginable observation isn't a foundation; it's tautology or taste.

**4. Independent triangulation.** N≥2 genuinely-independent projects surface the same pattern.

Independence is the criterion that's hardest to satisfy in practice. From [E2](../../01_foundations/E2_convergence_is_triangulation.md):

> If all projects share an author, an LLM, a stack, and a domain shape, *"three projects converge"* is mostly evidence that the author is consistent, not that the conclusion is true.

For elevation purposes, *"genuinely independent"* requires meaningful variation in at least one of:

- **Stack** — Python+SQLite vs Rust+Postgres vs TypeScript+Prisma. Cross-stack convergence rules out stack-specific framing.
- **Domain** — financial vs medical vs gaming vs developer-tools. Cross-domain convergence rules out domain-specific framing.
- **Authorship** — different authors or AI models. Cross-authorship convergence rules out shared-perspective bias.

The bar isn't perfect independence (which is rare); the bar is *honest acknowledgment of the evidence's actual evidential weight*. Three same-author same-AI same-stack sightings count for less than two genuinely-independent sightings.

When filing a promotion proposal, declare which dimensions of independence the evidence covers. A candidate with strong cross-stack evidence but weak cross-authorship evidence may still warrant promotion, but the promotion proposal should be honest about the gap.

### What happens to candidates that fail one criterion

A candidate that passes three of four stays at its current layer with the candidate's analysis recorded. The protocol explicitly tracks "almost-promotions" because:

- The candidate may earn promotion later when new evidence accumulates (the fourth criterion was the missing one; a future project supplies the missing evidence).
- The analysis itself is useful — it surfaces the candidate's structure and the reasons it didn't yet promote.

Re-evaluation happens when triggered by:

- A new independent project surfacing the same pattern (advances criterion 4)
- A new operational rule becoming explicable as an instance of the candidate (advances criterion 1)
- A successful demotion of an unrelated foundation, freeing conceptual space for the candidate to be revisited

### Demotion

Demotion is structurally necessary — without it, the foundational layer can only grow. From [E3](../../01_foundations/E3_foundations_aggressively_small.md):

> Without a path from "foundation" back to "operational rule" or "domain-specific pattern," the foundational layer can only grow.

A foundation gets demoted when cross-project evidence shows that:

- The bug shape doesn't actually recur outside its original domain (criterion 4 failure on retrospection)
- The fix shape doesn't generalize across stacks (the foundation was stack-specific, not universal)
- The principle was a derivation all along (criterion 2 failure surfaces in hindsight)

Demotion preserves the original elevation history per F1. The foundation's entry isn't deleted; a `DEMOTED` line is added with the demotion rationale and a pointer to where the rule now lives. Anchors are never reused.

### What this protocol does NOT do

- **It does not auto-promote.** Promotion always requires user decision. The protocol surfaces candidates and provides the criteria; the user is the decision-maker.
- **It does not eliminate judgment.** The criteria are gates, not algorithms. Two readers in good faith can disagree about whether a candidate meets criterion 1 (generative force). The protocol provides structure for the disagreement, not a way around it.
- **It does not promise universal coverage.** Some patterns will never have N≥2 independent sightings because they're rare. Those patterns stay at the project layer indefinitely; the protocol's gate isn't biased against rare-but-real patterns, just unable to certify them at higher layers without the evidence.

### Cross-references

- [../templates/promotion_proposal_template.md](../templates/promotion_proposal_template.md) — the structured document for filing a promotion proposal.
- [../../10_followups_patterns/](../../10_followups_patterns/) — three patterns currently staged for promotion, with their seed evidence and criteria analysis.
- [../../11_ai_dependency_tracking/](../../11_ai_dependency_tracking/) — AI-dependent rules cap at the stack or project layer per this protocol; they cannot promote to universal even if they meet the other three criteria.
