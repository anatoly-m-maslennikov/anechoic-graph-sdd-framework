---
atom_family: SPEC
atom_id: AN-S-2630
container:
  component: C9
tier: 1
context:
  lens: DES
state:
  status: "archived"
  version: 40
  updated_at: "2026-11-25T23:14:23.134607+00:00"
---
## Summary

Register Evaluation targets

## Claim

### Prose Claim

#### Applicability
direct `IS_EVALUATION_FOR` relations.

`IS_EVALUATION_FOR` **means** the direct relation from an Evaluation Atom to an
Atom whose authority the Evaluation checks.

Forward `Host ((IS_EVALUATION_FOR)) Target` and reverse `Target <((IS_EVALUATION_FOR)) Host` are views of the same Relation fact.
IS_EVALUATION_FOR relates Evaluation Atom to Atom whose authority is evaluated.
### Formal Claim

```python
from anechoic.formal_claims import declare_relation

declare_relation(
    relation_name='IS_EVALUATION_FOR',
    source_endpoint={'level': 'instances', 'entity_paths': ('Atom/(.Header.Context.Role := Evaluation)',)},
    target_endpoint={'level': 'instances', 'entity_paths': ('Atom',)},
)
```
