---
identity:
  atom_id: AN-S-1590
context:
  container:
    component: C9
  tier: 1
  lens: DES
state:
  status: active
  version: 27
  updated_at: 2026-11-02 00:18:22 +0400
---
## Summary

Resolve Status Domains from Complete Qualified Paths

## Claim

### Prose Claim


Status domains resolved from complete qualified paths.


a global Status value domain **must not** override the Status domain resolved from the complete qualified path of an Artifact Type **or** Atom Content Role **and** Type.

## Details

for Atoms, resolution from the complete qualified Content Role and Type path includes the allowed values inherited from Atom.Header.Status and the additional values admitted for that path. Inheritance does **not** replace the qualified model with a flat global domain or remove its additions. A narrower Atom kind **must not** remove inherited Status values.
