---
atom_family: SPEC
atom_id: AN-S-2150
container:
  component: C9
tier: 2
context:
  lens: DES
state:
  status: archived
  version: 40
  updated_at: 2026-11-02 19:44:26 +0400
---
## Summary

Separate scope ancestry from scope labels

## Claim

### Prose Claim


Scope Unit ancestry **and** Scope Unit Labels.


Scope Unit ancestry **must** follow declared Scope Unit parentage. ANECHOIC **must not** author or persist a Structural Level property; an optional derived depth or path rendering **must not** independently override that parentage under CA-R-1485.

the Operator **may** choose **any** suitable Scope Unit Label, including `Layer`, `Feature`, `group`, `supergroup`, **or** `sub-feature`, **without** changing the unit's ancestry, authority, precedence, **or** Relation semantics. Labels **and** readability fields do **not** replace the active authority for those distinctions.
