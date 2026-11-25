---
atom_family: SPEC
atom_id: AN-S-2712
container:
  component: C9
tier: 3
context:
  lens: DES
state:
  status: archived
  version: 5
  updated_at: 2026-11-03 20:00:05 +0400
---
## Summary

Define NARROWER_THAN

## Claim

### Prose Claim

NARROWER_THAN relates a narrower MODEL kind to a broader MODEL kind. A Property does not narrow. Both endpoints are MODEL kinds; Property bearers and instance populations do not become kinds through this notation. The narrower kind inherits applicable Relation and Property constraints without cloning declarations or instance facts. HAS_NARROWER is its derived inverse. In `X/Y`, Y is narrower than X; traversal runs from broader to narrower.
### Formal Claim

```python
# model
relation(source='$narrower', name='NARROWER_THAN', target='$broader')
relation(source='Relation//NARROWER_THAN', name='HAS_INVERSE', target='Relation//HAS_NARROWER')
set_value(address='alias(Relation//NARROWER_THAN)', value='"/"')
classify(address='Relation//NARROWER_THAN', axis='Derivation', value='Direct', notation='relation')
```

