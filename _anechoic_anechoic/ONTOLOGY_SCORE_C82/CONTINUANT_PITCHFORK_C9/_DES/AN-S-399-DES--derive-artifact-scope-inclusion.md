---
atom_family: SPEC
atom_id: AN-S-399
container:
  component: C9
tier: 3
context:
  lens: DES
state:
  status: "active"
  version: 37
  updated_at: "2026-11-25T20:52:14.256752+00:00"
---
## Summary

Derive Artifact scope inclusion

## Claim

### Prose Claim

This rule applies to legacy Scope Unit carriers. Use AN-S-3168 for the native Atom Container.


Artifacts contained **in** a Scope Unit.


the resolver **must** resolve **`=1`** direct Scope Unit from the Atom's internally carried ownership, checked against its canonical Carrier address, **or** from the registered canonical Carrier authority for a non-Atom Artifact **and** include that Artifact **in** **every** Scope Unit on the direct Unit's complete ancestor path; missing, multiple, unknown, **or** cyclic scope ownership is invalid.

## Details

For a legacy Project Goal without a Scope Unit, resolve its Operator owner under AN-S-1039@1; a failed Scope Unit resolution does **not** establish that no containing Scope Unit exists.
