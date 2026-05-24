"""Classifier predicates — hand-coded over finding text and metadata.

Implements the four-criteria classifier described in
../doctrine/four_criteria.md. This is the hand-coded baseline; later
versions can replace these predicates with an AI-drafted classifier
(see notes at the end), but the hand-coded version is sufficient for
the bootstrap window and provides a stable test surface.

The classifier produces:
  - requires_user_judgment: bool
  - classifier_criteria_met: dict

The dict is what the trust ratchet aggregates on. Recorded in the
auto_resolutions row when the agent acts on the finding.

Conservative bias on the boundary: when fewer than four agent-resolvable
criteria pass AND no user-required trigger fires, route to user.

Adapt to your project:
1. The regex sets below match common shapes; extend them with patterns
   specific to your project's finding text and severity language.
2. The doctrine pointers (e.g., 'F1', 'P004', '§5.4') are placeholders;
   your project's anchor format will differ.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Optional


# ─── Agent-resolvable criteria ──────────────────────────────────────────

# Criterion 1: "Doctrine names the answer."
# Heuristic: the finding text cites a doctrine anchor that resolves the
# fix shape directly. Examples: "per §5.4", "F1 violation", "P004 fix
# shape applies". Extend with your project's anchor formats.
_DOCTRINE_ANCHOR_RE = re.compile(
    r"(?:§\d+(?:\.\d+)*|F[1-9]\d*|E[1-9]\d*|P\d{3,})",
    re.IGNORECASE,
)


# Criterion 2: "A pattern exists to mirror."
# Heuristic: the finding cites a pattern library entry OR an existing
# code file as the template. Cross-checked against the project's pattern
# library if available.
_PATTERN_CITATION_RE = re.compile(
    r"(?:P\d{3,}|see\s+\w+\.py|pattern\s+library|mirror\s+\w+)",
    re.IGNORECASE,
)


# Criterion 3: "Verification is mechanical."
# Heuristic: the finding's resolution path includes running a test, an
# integrity check, or a contract test. The agent's commit message must
# include "tests pass" or equivalent.
_MECHANICAL_VERIFICATION_RE = re.compile(
    r"(?:test\s+passes?|integrity\s+check|contract\s+test|"
    r"invariant\s+test|ci\s+passes?|tests:\s*\d+/\d+)",
    re.IGNORECASE,
)


# Criterion 4: "Being wrong is reversible."
# Heuristic: NONE of the high-stakes patterns appear. If any appear, the
# finding is irreversible by default and routes to user.
_HIGH_STAKES_PATTERNS = re.compile(
    r"(?:money\s+(?:out|transfer)|customer-facing\s+publish|"
    r"delete\s+historical|drop\s+table|truncate|"
    r"security\s+(?:control|policy|permission)|"
    r"access\s+(?:control|grant|revoke)|"
    r"third-party\s+notification|email\s+(?:send|blast)|"
    r"production\s+secret)",
    re.IGNORECASE,
)


# ─── User-required triggers ─────────────────────────────────────────────

# Any of these patterns forces user routing regardless of the four-criteria
# gate.
_USER_REQUIRED_TRIGGERS = {
    "taxonomy": re.compile(
        r"(?:taxonomy|category\s+should\s+exist|new\s+status\s+value|"
        r"vocabulary|naming\s+convention)",
        re.IGNORECASE,
    ),
    "calibration_vs_reality": re.compile(
        r"(?:matches\s+the\s+actual|physical\s+(?:reality|object)|"
        r"measurement\s+correct|external\s+system\s+output)",
        re.IGNORECASE,
    ),
    "business_priority": re.compile(
        r"(?:target\s+rate|tolerance\s+threshold|strategic|"
        r"priority\s+between|business\s+(?:decision|judgment))",
        re.IGNORECASE,
    ),
    "doctrine_change": re.compile(
        r"(?:doctrine\s+(?:change|update|addition)|"
        r"new\s+(?:foundation|principle)|"
        r"modify\s+CLAUDE\.md|add\s+to\s+governance)",
        re.IGNORECASE,
    ),
    "high_stakes_irreversible": _HIGH_STAKES_PATTERNS,
    "cross_layer_change": re.compile(
        r"(?:cross-layer|stack-layer\s+(?:change|update)|"
        r"universal-layer|elevation\s+(?:to|from))",
        re.IGNORECASE,
    ),
}


# ─── Classifier ─────────────────────────────────────────────────────────


@dataclass
class ClassificationResult:
    """The classifier's output for one finding."""

    requires_user_judgment: bool
    criteria_met: dict
    user_required_triggers: list[str]
    routing_reason: str  # human-readable explanation


def classify_finding(
    finding_text: str,
    governing_principle: Optional[str] = None,
    has_pattern_in_library: bool = False,
) -> ClassificationResult:
    """Classify a finding as agent-resolvable or user-required.

    Arguments:
      finding_text: the finding's full text (description + proposed fix).
        Used for regex matching against the criteria.
      governing_principle: optional explicit anchor (e.g., 'F1', '§5.4',
        'P004'). When provided, satisfies criterion 1 without requiring
        the anchor to appear in finding_text.
      has_pattern_in_library: optional flag set by the caller after
        consulting the project's pattern library. When True, satisfies
        criterion 2 without requiring a citation in finding_text.

    Returns:
      ClassificationResult with the routing decision and the criteria
      record. The criteria record is what gets stored as
      auto_resolutions.classifier_criteria_met (JSON-encoded).
    """
    # Check user-required triggers first — they override the four-criteria gate.
    triggers_fired = []
    for trigger_name, trigger_re in _USER_REQUIRED_TRIGGERS.items():
        if trigger_re.search(finding_text):
            triggers_fired.append(trigger_name)

    # Evaluate the four agent-resolvable criteria.
    doctrine_names_answer = bool(
        governing_principle or _DOCTRINE_ANCHOR_RE.search(finding_text)
    )
    pattern_exists = bool(
        has_pattern_in_library or _PATTERN_CITATION_RE.search(finding_text)
    )
    verification_mechanical = bool(_MECHANICAL_VERIFICATION_RE.search(finding_text))
    reversible = not _HIGH_STAKES_PATTERNS.search(finding_text)

    criteria_met = {
        "doctrine_names_answer": doctrine_names_answer,
        "pattern_exists": pattern_exists,
        "verification_mechanical": verification_mechanical,
        "reversible": reversible,
        "user_required_triggers": triggers_fired,
    }

    # Routing logic.
    if triggers_fired:
        return ClassificationResult(
            requires_user_judgment=True,
            criteria_met=criteria_met,
            user_required_triggers=triggers_fired,
            routing_reason=(
                f"User-required trigger(s): {', '.join(triggers_fired)}"
            ),
        )

    agent_criteria_passed = sum([
        doctrine_names_answer,
        pattern_exists,
        verification_mechanical,
        reversible,
    ])

    if agent_criteria_passed == 4:
        return ClassificationResult(
            requires_user_judgment=False,
            criteria_met=criteria_met,
            user_required_triggers=[],
            routing_reason="All four agent-resolvable criteria satisfied.",
        )

    # Conservative bias on the ambiguous boundary: route to user.
    missing = [
        name for name, value in [
            ("doctrine_names_answer", doctrine_names_answer),
            ("pattern_exists", pattern_exists),
            ("verification_mechanical", verification_mechanical),
            ("reversible", reversible),
        ] if not value
    ]
    return ClassificationResult(
        requires_user_judgment=True,
        criteria_met=criteria_met,
        user_required_triggers=[],
        routing_reason=(
            f"Only {agent_criteria_passed}/4 agent-resolvable criteria passed. "
            f"Missing: {', '.join(missing)}. Conservative bias at boundary."
        ),
    )


# ─── Notes on evolution ─────────────────────────────────────────────────
#
# This hand-coded predicate set is the bootstrap implementation. Later
# replacements include:
#
# 1. AI-drafted classifier. After ~30+ classifications with recorded
#    outcomes, an AI model can be prompted with the four-criteria spec
#    and produce judgments with calibration data. Failure-tolerant: on
#    AI failure (rate limit, parse error), fall back to this hand-coded
#    version. The AI version produces richer reasoning text but the
#    same dict output, so downstream consumers (audit lane, trust
#    ratchet) don't change.
#
# 2. Per-shape calibration. The trust ratchet's evidence about which
#    shapes have been auto-resolved successfully feeds back into the
#    classifier: shapes with a long acceptance history might warrant
#    relaxed criteria (e.g., implicit doctrine acceptance for very
#    common patterns). Implement only after data shows it's needed.
#
# 3. Cross-model corroboration. For AI-dependent classifications,
#    running the same finding through two independent models and
#    routing to user on disagreement is the structural triangulation
#    per E2. Implement when multiple models are operationally available.
#
# Per CLAUDE.md §11 AI-dependency tracking: the classifier itself is an
# AI-dependent rule. Document the AI dependencies in the calibration
# notes and re-validate on model upgrades.
