# AI-dependency note template

Add this note to any operational rule whose correctness depends on a specific AI's behavior. The four fields make the dependency explicit so model upgrades trigger re-validation rather than silently producing different outcomes.

---

## The four fields

```markdown
**AI-dependency note:**

- **Depends on:** <Specific AI behavior the rule's correctness relies on.
  Be concrete — "the model preserves distinction X" is more useful than
  "the model is good at task Y".>

- **Validated against:** <Comma-separated list of model versions the rule
  has been tested with. Include validation method when relevant — e.g.,
  "Claude Sonnet 4.6 (manual review of 50 cases), Claude Opus 4.7
  (automated calibration suite)".>

- **Falsification:** <What observation would prove the rule is no longer
  honored under a new model. Usually a calibration metric — "cross-model
  agreement drops below X% on the calibration set" or "false-positive
  rate on the audit sample exceeds Y%".>

- **Fallback:** <What happens when re-validation is pending. Usually:
  route affected outputs to user review until validation completes.
  Don't auto-act on rules whose validation is uncertain.>
```

---

## Worked example — the classifier's criterion 1

From the four-criteria classifier in [03_classifier_and_audit_lane/](../../03_classifier_and_audit_lane/):

```markdown
## Classifier criterion 1: Doctrine names the answer

**Rule:** A finding is classified agent-resolvable on criterion 1 if and
only if the project doctrine contains a clause that unambiguously
specifies the fix shape for this class of change.

**Implementation:** The classifying agent reads the relevant doctrine
sections and returns a boolean. If the agent's confidence is below a
threshold or the doctrine sections are ambiguous, the boolean is False
and the finding routes to user review.

**AI-dependency note:**

- **Depends on:** The classifying model preserving the distinction
  between "doctrine describes the fix" vs. "doctrine could be
  interpreted to suggest the fix." A model that over-commits in
  ambiguous cases will produce more False positives on this criterion
  and more incorrect auto-resolutions. The model also needs to handle
  multi-section doctrine consultation — finding the relevant clause
  may require synthesizing across several sections.

- **Validated against:** Claude Sonnet 4.6 and Claude Opus 4.7. Manual
  review of 50 ambiguous findings: 84% agreement with user judgment.
  Cross-model agreement (Claude 4.6 vs GPT-4o) on the same set: 78%.

- **Falsification:** If cross-model agreement drops below 70% on the
  calibration set, or if user-overturn rate on classifier decisions
  exceeds 20% in a rolling 30-day window, the criterion is suspect
  under the new models — route all findings to user review until the
  prompt is re-derived for the new model surface.

- **Fallback:** Manual review for everything classified agent-resolvable
  until the cross-model agreement is re-validated. The classifier
  continues to output verdicts (for instrumentation and trust-ratchet
  data) but the downstream auto-act path is suspended.
```

---

## Worked example — a doctrine entry with AI-dependency

For a doctrine clause whose application depends on AI:

```markdown
## Rule: AI-identified items default to suggested category with user confirmation

**Statement:** When the AI identifies an inventory item from photos, the
suggested category is presented to the user for confirmation rather
than auto-applied. The user's confirmation is what makes the category
load-bearing.

**Derives from:** Foundation E1 (AI output is hypothesis, not authority)
applied to inventory categorization.

**Falsification condition:** A demonstrated AI categorization accuracy
above 99% on a held-out test set of items typical for this domain.
Currently observed accuracy is 88-94% depending on category type, so
the rule stands.

**Anchor history:** 2026-05-05 — added after 88 of 89 inventory rows
were silently mis-categorized by an AI free-text categorization path
that bypassed user confirmation.

**AI-dependency note:**

- **Depends on:** The AI's identification accuracy being below the
  trust threshold (currently 99%). Above-threshold accuracy would
  make the user-confirmation step unnecessary overhead.

- **Validated against:** Claude Sonnet 4.6 vision identification on
  500 historical items, 88-94% accuracy by category.

- **Falsification:** Accuracy above 99% on a held-out test set; OR
  user-overturn rate on AI suggestions drops below 1% in a rolling
  90-day window.

- **Fallback:** None needed — the rule is conservative. If a new model
  changes the AI's accuracy, the rule may become unnecessarily strict
  (user confirming things the AI got right) but won't produce incorrect
  outcomes. Periodic re-evaluation against the new model's actual
  accuracy is appropriate; the rule may be relaxed if accuracy clears
  the threshold.
```

---

## What to include vs. exclude

**Include the note when:**

- The rule's output would visibly differ if the model changed
- The rule depends on a specific AI judgment (categorization, classification, semantic understanding, prompt comprehension)
- The rule's correctness is validated empirically against a specific model rather than derivable from first principles

**Skip the note when:**

- The rule is deterministic (a regex, an SQL query, a schema constraint)
- The rule doesn't involve AI at all
- The rule's outcomes don't depend on which model is in use (e.g., "log every AI call" — true regardless of model)

The bar for adding a note is *"this rule's outcome would visibly differ if the model changed."* If you can't articulate the dependency, the rule probably isn't AI-dependent — or your understanding of how it works is incomplete (the second case is itself a finding worth surfacing).

## Cross-model corroboration as validation

For high-stakes AI-dependent rules, the strongest validation form per [E2](../../01_foundations/E2_convergence_is_triangulation.md) is cross-model agreement: run the same input through two independent models and check whether they agree.

When this is feasible in your project's infrastructure (you have multiple LLM endpoints configured), the dependency note's "Validated against" field can include cross-model metrics:

```markdown
**Validated against:**
- Claude Sonnet 4.6: 92% accuracy on calibration set
- GPT-4o: 89% accuracy on calibration set
- Gemini 1.5 Pro: 87% accuracy on calibration set
- Cross-model agreement (all three agree): 81%
```

The cross-model agreement metric is the most evidentiarily-strong validation. A rule with high single-model accuracy but low cross-model agreement is making a model-specific judgment that may not generalize. A rule with both high single-model accuracy AND high cross-model agreement is making a more robust judgment.

## What about rules that are AI-drafted but not AI-dependent?

A rule that was *originally drafted by an AI* but doesn't depend on AI behavior to be true (e.g., a derived rule from F1 that an AI happened to articulate first) is NOT AI-dependent. It doesn't need the note.

The distinction:

- **AI-drafted:** the AI was the agent who first articulated the rule. The rule's truth is independent of the AI.
- **AI-dependent:** the rule's application or correctness relies on AI behavior. The rule wouldn't hold (or would hold differently) under a different model.

Most rules that AIs draft turn out to be AI-drafted but not AI-dependent. The ones that are AI-dependent are usually the ones about AI behavior or about the AI's own outputs (classifiers, output-verification rules, prompt-based detectors).
