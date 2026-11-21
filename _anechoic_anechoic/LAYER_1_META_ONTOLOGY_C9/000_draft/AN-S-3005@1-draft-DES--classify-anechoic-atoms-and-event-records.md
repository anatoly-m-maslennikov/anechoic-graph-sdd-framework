---
atom_family: SPEC
atom_id: AN-S-3005
structure:
  container:
    component: C9
  tier: 3
context:
  lens: DES
state:
  status: draft
  version: 1
  updated_at: '2026-11-18T22:04:32.894618+00:00'
---
## Summary

Classify Anechoic Atoms and Event Records

## Claim

### Prose Claim

`IS_CLASSIFIED_BY` groups entities through a named Relation, independently of their narrowing hierarchy. Spec Atom and PMETA Atom are classified as Continuant. Ticket Atom is classified as Occurrent. Spec Atom and Event Record are classified as SSOT. These statements specify the listed memberships; they do not assert that the lists are exhaustive. The family bound is Matter-bound (Realization) for Spec Atom, Matter-bound (Project) for PMETA Atom, and Time-bound for Ticket Atom.

## Details

Acceptance: a Spec Atom is both Continuant and SSOT; a Ticket Atom is Occurrent; classification does not turn Continuant or SSOT into an Artifact subtype.

Sources: CA-A-1462@1-draft. Task: CA-P-3080.
