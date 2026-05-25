# Ingestion record template

Copy this template into your kit's ingestion records when you complete an ingestion. Records live in the kit (or the consuming project) as permanent artifacts; they make the kit's structural evolution auditable.

Filename convention: `YYYY-MM-DD_<source-short-name>_ingestion.md` (e.g., `2026-05-24_prizmforge_ingestion.md`).

---

## Template

```markdown
# Ingestion record — <Source short name>

**Ingested on:** YYYY-MM-DD
**Ingested by:** <agent name or human identifier>
**Source artifact:** <full URL or citation>
**Source version:** <commit SHA, version number, edition, etc.>
**Source license:** <MIT, Apache 2.0, CC-BY, etc. — relevant for attribution and re-use>
**Status:** <complete | partial | aborted at step N>

## Why this ingestion was undertaken

<2-3 sentences naming the trigger. What problem was the kit (or a
consuming project) hitting that made this source look valuable? What
overlap with the kit's existing concerns motivated the investigation?>

---

## Step 1 — Source analysis

### Primitives identified

<List of concrete mechanisms the source defines. For each:>

- **<Primitive name>** — <one-sentence description>
- **<Primitive name>** — <one-sentence description>
- ...

### Principles articulated

<Rules or invariants the source explicitly or implicitly relies on:>

- **<Principle>** — <one-sentence statement>
- **<Principle>** — <one-sentence statement>
- ...

### Anti-patterns the source responds to

<Failure modes the source is built to prevent:>

- **<Anti-pattern>** — <one-sentence description of the failure mode>
- ...

### Assumptions the source makes

<What the source takes as given:>

- **<Assumption>** — <what's assumed, why it matters for ingestion fit>
- ...

---

## Step 2 — Principle extraction (per primitive)

### Primitive: <Name>

**Source description:** <quote or paraphrase from Step 1>

**Derivation:** <which kit foundation this derives from — F1/F2/F3/E1/E2/E3>

**Derivation rationale:** <2-3 sentences explaining how the primitive
implements the named foundation. If the derivation required articulating
a new "implies" entry on the foundation, note that here.>

**Outcome:** <derivation_found | derivation_requires_new_framing | derivation_not_found>

(Repeat for each primitive from Step 1.)

---

## Step 3 — Subsystem fit assessment (per primitive that passed Step 2)

### Primitive: <Name>

**Target subsystem:** <existing subsystem N | new subsystem proposal | no fit>

**Fit rationale:** <2-3 sentences explaining why the primitive belongs in
this subsystem. If proposing a new subsystem, name what concern it covers
and what other primitives would join it.>

**Adaptation scope:** <minor extension | subsystem-level revision | new subsystem>

(Repeat for each primitive that passed Step 2.)

---

## Step 4 — Adaptation (per primitive being ingested)

### Primitive: <Name>

**Landing location:** <relative path to where the primitive will live in the kit>

**Adaptation notes:** <what changed from the source — naming conventions,
restructuring, integration with kit idioms (ratchet patterns, derives-from
headers, cross-reference style)>

**Gaps surfaced during adaptation:** <issues in the source that the
adaptation revealed — e.g., the source didn't address concurrency, didn't
address how the primitive degrades under model upgrade, didn't have a
falsification condition. These are interesting findings worth recording.>

(Repeat for each primitive being ingested.)

---

## Step 5 — Provenance summary

### What got ingested

| Primitive | Source location | Landed at | Adaptation scope |
|---|---|---|---|
| <name> | <where in source> | <where in kit> | <minor / revision / new> |
| ... | | | |

### What didn't get ingested

| Primitive | Reason | Status |
|---|---|---|
| <name> | <Step N failure or judgment not to import> | <may revisit / closed> |
| ... | | |

### Cross-references created

<List of cross-references added between ingested primitives and existing
kit content. Bidirectional citation matters per the patterns-local-
enforcers-home meta-stance.>

### Attribution

<Explicit acknowledgment that the source was external, with the
attribution language appropriate to the source's license and the
adapter's discretion. Examples:>

- "Primitive X was adapted from <Source>, originally by <Author>, MIT licensed."
- "The general shape of <subsystem> was inspired by <Source>; the specific implementation is original to this kit."

### Open questions / followups

<Anything the ingestion surfaced that warrants future work:>

- <Question or followup>
- ...
```

---

## How to use the record

**During ingestion:** fill in Step 1 first, then walk Steps 2-5 in order. The record evolves as the ingestion proceeds; don't wait until everything is settled to start writing.

**After ingestion:** commit the record to the kit (or consuming project) and link to it from the affected subsystem READMEs. The cross-references make the record discoverable from the artifacts it produced.

**For aborted ingestions:** if the ingestion gets aborted partway through (the source turned out not to fit; a primitive failed Step 3; the work was deprioritized), still commit the record. An aborted ingestion is a real finding — future attempts to ingest the same source can pick up where this one stopped, and the analysis isn't lost.

## What the record protects against

- **Silent absorption.** An ingestion without a record is theft, not ingestion. The record is what makes the difference.
- **Re-investigation.** A future encounter with the same source doesn't need to redo Step 1 — the prior record's analysis is the starting point.
- **Provenance loss.** Ten years from now, when someone asks "where did this kit's `line_guid` primitive come from?" the record is the answer.
- **Echo-chamber drift.** The kit's structural commitments don't become exclusionary when ingestion has a defined process. The record is the audit trail proving external sources were considered, even when they were not ultimately incorporated.

## Cross-references

- [../doctrine/five_step_process.md](../doctrine/five_step_process.md) — the protocol the record documents.
- [../examples/prizmforge_ingestion.md](../examples/prizmforge_ingestion.md) — a fully worked-out record using this template.
