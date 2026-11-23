---
atom_family: SPEC
atom_id: AN-S-2694
container:
  component: C9
tier: 1
context:
  lens: DES
state:
  status: archived
  version: 12
  updated_at: 2026-11-04 23:01:11 +0400
---
## Summary

Define is derived relation of relation

## Claim

### Prose Claim

IS_DERIVED_RELATION_OF relates a derived Relation Type instance to its source Relation Type instance. It does not itself specify the endpoint transformation or any qualification. A direct Declaration's inverse binding entails the bound inverse's IS_DERIVED_RELATION_OF link to the direct Relation. A qualified derivation must retain its explicit qualification; it must not be normalized to an unconditional inverse.
### Formal Claim

```CFEL
# model
Relation//$relation ((IS_DERIVED_RELATION_OF)) Relation//$relation_2;

Relation//IS_DERIVED_RELATION_OF ((HAS_CLASSIFICATION)) Derivation == Direct
```

