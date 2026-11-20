---
identity:
  atom_id: AN-S-399
context:
  container:
    component: C9
  tier: 3
  lens: DES
state:
  status: active
  version: 36
  updated_at: 2026-11-02 19:44:26 +0400
---
## Summary

Derive Artifact scope inclusion

## Claim

### Prose Claim


Artifacts contained **in** a Scope Unit.


the resolver **must** resolve **`=1`** direct Scope Unit from the Atom's internally carried ownership, checked against its canonical Carrier address, **or** from the registered canonical Carrier authority for a non-Atom Artifact **and** include that Artifact **in** **every** Scope Unit on the direct Unit's complete ancestor path; missing, multiple, unknown, **or** cyclic scope ownership is invalid.

## Details

an Atom with no containing Scope Unit uses the external-Atom Author fallback under CA-D-657-CORE_META_MODEL-ENG_DECISION--use-economical-yaml-frontmatter; a failed Scope Unit resolution does **not** establish that no containing Scope Unit exists.
