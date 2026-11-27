---
atom_family: SPEC
atom_id: AN-S-1241
container:
  component: C15
tier: 3
context:
  lens: DES
state:
  status: archived
  version: 24
  updated_at: "2026-11-27T16:16:01.404965+00:00"
---
## Summary

Preserve Git and Journal as independent provenance systems

## Claim scope

PROGRAMMATIC behavior governing PROGRAMMATIC.

## Claim

### Prose Claim

PROGRAMMATIC **must** preserve Git **and** the Project Work Journal as two independent, intentionally redundant provenance **and** history systems. Git owns carrier bytes, tree state, commit identity, **and** ancestry. The Journal owns governed semantic action history, human-origin Initiative context, affected identities **and** revisions, **and** explicit cross-system bindings. **every** committed Journal carrier revision is independently recoverable through Git, but neither system substitutes for the other.

Technical warnings emitted while a bounded scan skips an isolated schema-invalid
Atom are not business Journal history. They must not fabricate a business action,
Run, or Journal record, or rewrite historical Journal carriers. The operation must
report `complete: false` when the scan is incomplete. The business Journal remains
business-only.

One sealed action **may** pass through `git_complete_journal_pending`, `journal_recorded_git_pending`, **and** `reconciled`. A real-change commit **may** complete **before** its canonical Journal record is appended; a Journal record **may** be prepared **before** that commit, but its canonical binding is complete **only** once the exact reachable real-change commit SHA is known. `reconciled` requires **=1** canonical action record, **=1** reachable real-change commit binding, **and** a later separate Git commit that versions the Journal carrier containing that record. The Journal record does **not** embed the SHA of the Git commit that **contains** that same record: reconciliation derives that Journal-to-Git binding from the exact carrier revision **and** reachable Git history, avoiding a self-referential digest cycle.

Journal incompleteness or unreconciled bindings **must not** gate Atom creation, update, Status change, promotion, ordinary later work, or release. Preserve observable pending states and detect missing events, unreachable commits, duplicates, digest mismatches and Journal commit lag; report or repair them without turning Journal completeness into effect-admission permission. Independent Git and other applicable release safeguards remain unchanged.

