---
atom_family: SPEC
atom_id: AN-S-2632
container:
  component: C9
tier: 1
context:
  lens: DES
state:
  status: archived
  version: 33
  updated_at: 2026-11-04 22:00:28 +0400
---
## Summary

Register implementation_of relation

## Claim

### Prose Claim

implementation_of is the direct Relation owned by a governed Implementation Carrier. The Host is that governed Implementation Carrier and each tuple targets the specification Atom it implements.

### Formal Claim

```CFEL
# model
Relation//implementation_of ((HAS_CLASSIFICATION)) Derivation == Direct;

# instances
Carrier//$implementation_carrier ((implementation_of)) Atom//$specification_atom
```

