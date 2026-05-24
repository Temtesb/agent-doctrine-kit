# F3 — Information has asymmetric durability

## Statement

Information takes work to preserve and zero work to destroy. Once destroyed, recovery is impossible without a prior copy.

## Type

Physical/Logical (grounded in the second law of thermodynamics).

## Falsification condition

A method to reconstruct erased information from nothing — without a backup, redundant copy, or derivable source. Thermodynamics forbids this.

## Implies

- **No hard deletes.** Things that happened do not unhappen; deletion erases history that the system needs. Soft-void via lifecycle states (`closed`, `dismissed`, `voided`) with timestamps. The legitimate exceptions are genuinely transient infrastructure data (expired tokens, temp upload files); document them inline at the call site.
- **Backup discipline.** Every artifact whose loss would be expensive must have a redundant copy. The asymmetric-durability foundation makes this a structural concern, not an operational nicety.
- **Secrets, once leaked, cannot be unleaked.** `.env` files belong in `.gitignore` from the start, not after the first leak. Once a secret is pushed to a remote, rotation is the only fix; the leaked artifact stays leaked.
- **Lock state outlasts the process that held it.** A held lock without an explicit lifetime contract — `.git/index.lock`, `.cowork_run.lock`, database write locks — outlives the durability of the process that wrote it. This is exactly the asymmetric-durability failure F3 names. See [10_followups_patterns/git_lock_coordination.md](../10_followups_patterns/git_lock_coordination.md) for the structural fix at the stack layer.
- **Append-only event logs are durable; mutated status fields are not.** This is the intersection of F1 and F3: time has direction (F1) AND the historical record degrades asymmetrically under mutation (F3). Together they say *"the event log preserves; the status field destroys."*

## Anchor history

- **2026-04-28** — Elevated. Triggered by the closure-as-event discussion that surfaced how hard-delete `CASCADE` clauses encode an assumption that deletion is a legitimate operation. Information asymmetry generalizes the no-hard-deletes principle beyond audit-driven domains — it applies anywhere information can be lost faster than it can be reconstructed.

## AI-dependency note

None. F3 is independent of AI capabilities.

## What derives from this foundation in this kit

- The no-hard-deletes discipline embedded across [02_audit_as_shape/](../02_audit_as_shape/), [03_classifier_and_audit_lane/](../03_classifier_and_audit_lane/), [05_lessons_loop/](../05_lessons_loop/).
- [10_followups_patterns/git_lock_coordination.md](../10_followups_patterns/git_lock_coordination.md) — explicit acquire/release semantics with watchdog cleanup, derived from F3's lock-state-outlasts-holder implication.
- The contributing-guide / kit-maintenance discipline that this kit's repo itself must be backed up (git remote, multiple clones) — the kit is itself information subject to F3.
