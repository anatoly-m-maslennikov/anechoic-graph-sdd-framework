---
atom_family: SPEC
atom_id: AN-S-2633
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

Register evidence_for relation

## Claim

### Prose Claim

evidence_for is the direct Relation owned by an evidence Carrier. The Host is that evidence Carrier and each tuple targets the Evaluation or Implementation Carrier it supports.

### Formal Claim

```CFEL
# model
Relation//evidence_for ((HAS_CLASSIFICATION)) Derivation == Direct;

# instances
Carrier//$evidence_carrier ((evidence_for)) Carrier//$supported_carrier
```

