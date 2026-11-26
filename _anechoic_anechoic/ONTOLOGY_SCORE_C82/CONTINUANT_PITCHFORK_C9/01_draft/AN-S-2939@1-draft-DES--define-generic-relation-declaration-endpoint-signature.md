---
atom_family: SPEC
atom_id: AN-S-2939
container:
  component: C9
tier: 3
context:
  lens: DES
state:
  status: draft
  version: 1
  updated_at: 2026-11-05 16:33:24 +0400
---
## Summary

Define generic Relation Declaration endpoint signature

## Claim

### Prose Claim

Within a Relation Declaration Formal Claim only, `$host ((RELATION)) $target` is the reusable generic endpoint signature. `$host` and `$target` range over the endpoint domains explicitly admitted by the Relation Declaration. Those domains are declared model entities or instances, including Carrier and CFEL, except for the literal values and constraint data explicitly admitted as endpoints of HAS_ALLOWED_VALUE, HAS_VALUE_CONSTRAINT and their declared derived inverses. CFEL glyphs are not endpoints. This signature creates neither a Relation fact nor instance data. Known endpoint kinds remain typed selectors; the generic signature does not extend untyped variables to any other CFEL context.
