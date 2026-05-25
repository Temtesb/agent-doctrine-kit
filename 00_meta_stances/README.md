# 00 — Meta-stances

These are not concepts. They're **stances** — frames for *how* the rest of the kit should be received and adopted. Each is a one-page principle that reshapes how you think about the operational layers below it.

The five stances:

| File | What it does |
|---|---|
| [prefer_enforcers_over_principles.md](prefer_enforcers_over_principles.md) | Closes the gap between what doctrine claims and what runtime honors. Push enforcement into code that fails at write/build/run time; principles are the fallback for what can't be enforced. |
| [patterns_local_enforcers_home.md](patterns_local_enforcers_home.md) | The companion principle to the above. Project-side pattern records and stack-side enforcers carry different work and cite each other. |
| [hypothesis_posture.md](hypothesis_posture.md) | Closes the gap between static doctrine and evolving substrate. Doctrine is the corpus's *current best understanding* with a falsification condition, not authority text. Matters more under AI authorship than human-only. |
| [three_layer_architecture.md](three_layer_architecture.md) | The structural model the rest of the kit derives from: universal foundations → stack-shape patterns → project-specific rules. Lessons promote to the right layer based on evidence. |
| [user_is_a_participant.md](user_is_a_participant.md) | The user is one row in the participant registry, not architecturally a supervisor. Enables leveraged effort among agents (the axe-head-and-handle framing). Scales the protocol uniformly as the agent population grows. |

---

## Read these first

Every concept directory in this kit (`01_foundations/` through `13_safe_code_modification/`) is grounded in these five stances. Concepts in isolation read as features; the stances reframe them as integrated parts of a self-improving system.

If you're going to adopt anything from this kit, adopt the stances first. The schemas and enforcers in later directories assume you've already framed your project as something that:

1. Prefers enforcers wherever possible (so the schemas and tests aren't surprising additions)
2. Distinguishes patterns from enforcers (so the pattern library and architecture invariant tests have their natural homes)
3. Holds doctrine as hypothesis (so doctrine entries are written with falsification conditions and anchor histories)
4. Has explicit doctrine layers (so the cross-references in later directories make sense)
5. Treats the user as a participant rather than a supervisor (so the message/edge/vote protocol is uniform across user and agents, and the system can scale to N agents without special-casing the user)

Without these stances, the operational pieces still work in isolation but they don't compose into the system the kit describes.

---

## Cross-references

- Per the hypothesis posture, every operational rule in this kit declares its anchor — which foundation (see [01_foundations/](../01_foundations/)) it derives from.
- Per the three-layer architecture, every concept is tagged with its layer in the top-level [README.md](../README.md).
- Per "patterns are local sightings; enforcers are the home," the pattern library template lives in [06_patterns_and_dissonance/](../06_patterns_and_dissonance/) and the architecture invariants live in [04_pre_flight_and_invariants/](../04_pre_flight_and_invariants/) — and they cite each other.
- Per "prefer enforcers over principles," the [10_followups_patterns/](../10_followups_patterns/) directory holds three concrete enforcers ready to lift.
