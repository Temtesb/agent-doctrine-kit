# Promotion proposal template

Copy this template to file a promotion proposal — a structured document evaluating whether a project-layer pattern earns promotion to stack-layer enforcer, or a stack-layer pattern earns promotion to universal foundation.

The proposal lives in:

- `FOLLOWUPS.md` at the stack-layer repo (for project → stack promotions)
- `CANDIDATES/<date>_<short-title>.md` at the universal-layer repo (for stack → universal promotions)

The proposal's structure forces honest evaluation against the four criteria. A proposal that can't fill out the structure is not yet ready.

---

## Template

```markdown
# Promotion proposal: <Title naming the candidate>

**Filed:** YYYY-MM-DD
**Filed by:** <agent name or user identifier>
**Proposed elevation:** <project → stack> | <stack → universal>
**Proposed home:** <where the candidate would live if promoted>

## The candidate

<One-paragraph statement of the candidate in its sharpest form. The
"sticky-note version" — if you had to fit the candidate on a sticky
note, what would it say?>

## Criterion 1 — Generative force

**Claim:** This candidate explains the following operational rules:

1. <Rule 1 — name and brief restatement>
2. <Rule 2 — name and brief restatement>
3. <Rule 3 — name and brief restatement>
(continue as needed)

**Analysis:** <2-3 sentences explaining how each listed rule becomes
explicable as an instance of the candidate. The bar is at least three
rules — fewer than three suggests the candidate IS one of those rules,
mis-classified.>

**Verdict:** PASS | MARGINAL | FAIL

## Criterion 2 — Reduction-resistance

**Attempted derivations from existing foundations:**

- **From F1 (time has direction):** <attempt to derive the candidate
  from F1; if successful, the candidate IS that derivation, not a new
  foundation>
- **From F2 (mathematics and logic hold):** <attempt to derive from F2>
- **From F3 (information has asymmetric durability):** <from F3>
- **From E1 (the corpus is a hypothesis):** <from E1>
- **From E2 (convergence is triangulation):** <from E2>
- **From E3 (foundations aggressively small):** <from E3>

**Analysis:** <If every attempt to derive the candidate from an existing
foundation fails, criterion 2 is satisfied. If any attempt succeeds,
the candidate is a derivation; record it at the appropriate layer with
the derivation chain documented.>

**Verdict:** PASS | MARGINAL | FAIL

## Criterion 3 — Falsifiability

**Falsification condition:** <What would prove this candidate wrong?
The condition must be a positive observable, not the absence of
something. "We have not observed X" is acceptable; "we have not seen
the candidate fail" is not.>

**Analysis:** <Why is the falsification condition meaningful? What
would change if it were observed? A condition that can never be
satisfied isn't a falsification condition — it's tautology dressed
up. A condition that's been observed already would already have
falsified the candidate.>

**Verdict:** PASS | MARGINAL | FAIL

## Criterion 4 — Independent triangulation

**Project sightings:**

1. **Project A:** <project name, brief description, stack, domain,
   author/AI>
   - **Sighting evidence:** <concrete instance — link to the project's
     PATTERNS.md entry, integrity check, or session log>
   - **Independence dimensions:** <which dimensions this sighting
     contributes to — stack, domain, authorship>

2. **Project B:** <as above>

(N≥2 sightings; more strengthens the evidence)

**Anti-collinearity analysis:**

<Honest evaluation of how independent the sightings actually are.
Strong cross-stack but weak cross-authorship is documented; strong
cross-authorship but same-domain is documented. The bar isn't perfect
independence — it's honest acknowledgment of the evidence's actual
evidential weight.>

**Verdict:** PASS | MARGINAL | FAIL

## Overall

**Criteria summary:** <table or list showing pass/marginal/fail per
criterion>

**Recommendation:** <PROMOTE | STAGE | DEFER | DEMOTE>

- **PROMOTE** — all four criteria PASS. The candidate earns its
  proposed home. Implementation steps to follow.
- **STAGE** — three of four criteria PASS, one is MARGINAL. The
  candidate stays at its current layer; the proposal is recorded for
  re-evaluation when new evidence accumulates.
- **DEFER** — fewer than three criteria PASS. The candidate is not
  yet ready for promotion. Specific guidance on what would advance it.
- **DEMOTE** — applies only to existing foundations being re-evaluated.
  Cross-project evidence shows the foundation fails one or more
  criteria in retrospect; demotion is the corrective action.

## Implementation steps (if PROMOTE)

<Concrete steps to land the promoted candidate at its proposed home.
For project → stack promotions, this is usually: write the
stack-layer enforcer (test, decorator, schema constraint), add it to
the skeleton, file the elevation as an entry in the stack-layer
doctrine.>

## Cross-references

- **Sighting records:** <links to project-layer PATTERNS.md entries
  this proposal cites>
- **Related candidates:** <other promotion proposals this one shares
  structure with>
- **Affected rules:** <existing rules that may need to be re-anchored
  if this candidate is promoted>
```

---

## Notes on filling out the proposal

**Be honest about MARGINAL verdicts.** The temptation is to claim PASS on every criterion because the proposal feels right. The discipline is to mark MARGINAL when the evidence is genuinely mixed. The protocol's value comes from the gate being honest, not from passing.

**Cross-criterion patterns matter.** A candidate that's PASS on criteria 1-3 but MARGINAL on criterion 4 is in a different position than a candidate that's PASS on criteria 2-4 but MARGINAL on criterion 1. The first might earn promotion when new evidence accumulates; the second suggests the candidate's generative force was overestimated.

**The protocol explicitly tracks DEFER candidates.** A DEFER proposal isn't a failure — it's a recorded analysis that the candidate has been considered and is not yet ready. Future evidence may change the verdict; the analysis is preserved for that re-evaluation.

**DEMOTE proposals are rare but important.** When an existing foundation turns out to have been over-elevated (one of its criteria fails in retrospect), the DEMOTE proposal is how it returns to the appropriate layer. The original elevation history is preserved per F1; the demotion adds context, never overwrites.
