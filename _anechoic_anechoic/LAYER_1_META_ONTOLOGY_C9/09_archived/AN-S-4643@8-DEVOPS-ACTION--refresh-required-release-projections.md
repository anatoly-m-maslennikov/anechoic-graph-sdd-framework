---
atom_family: SPEC
atom_id: AN-S-4643
container:
  component: C9
tier: 3
context:
  template: action
  lens: DevOps
state:
  status: archived
  version: 8
  updated_at: 2026-10-24 00:38:25 +0400
---
## Summary

Refresh required release Projections

# Refresh required release Projections

Refresh Required Release Projections **means** the Action that makes the selected release candidate's required Projections current under their existing governing authority.

1. resolve the exact required Projection set **and** its source Revisions from the selected release gates.
2. retain an existing Projection **when** its governing currentness check passes for those sources; **otherwise** execute its registered derivation **and** Delivery procedure.
3. use the applicable reconciliation Workflow for a Reconciled Projection, including CA-O-011 for Applicable Methodology. do **not** change projected Claims **to** fix source conflicts.
4. check the resulting Projection against its own required Evaluations **and** current source binding.
5. return the exact checked results **or** the blocking failure; preserve actual execution evidence **in** the shared Journal.

an enabled Projection **not** required by the selected gate does **not** require refresh merely because an Atom changed. unresolved source conflicts, changed source bindings, failed publication, **or** missing required checks block success. this Action does **not** select a new Projection contract, authorize source corrections, **or** infer release readiness from successful refresh alone.
