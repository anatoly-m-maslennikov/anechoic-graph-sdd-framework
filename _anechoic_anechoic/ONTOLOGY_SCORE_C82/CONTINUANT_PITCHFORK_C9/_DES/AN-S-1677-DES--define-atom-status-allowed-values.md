---
atom_family: SPEC
atom_id: AN-S-1677
container:
  component: C9
tier: 2
context:
  lens: DES
state:
  status: active
  version: 13
  updated_at: 2026-11-02 00:18:22 +0400
---
## Summary

Define Atom.Status allowed values

## Claim

### Prose Claim


The base allowed values inherited by narrower Atom kinds.


Atom.Header.Status **must** admit (Draft, Active, Archived). Narrower Atom kinds inherit these values and **may** add allowed values under their applicable Content Role or Type. An inherited value does **not** require a separate declaration for every narrower kind.

## Details

CA-R-1412 requires exactly one Status but does not declare the base allowed values. CA-R-1309 declares Draft, Active and Archived only for Requirements; it must not be retargeted to all Atoms as a Subjects-only change.
