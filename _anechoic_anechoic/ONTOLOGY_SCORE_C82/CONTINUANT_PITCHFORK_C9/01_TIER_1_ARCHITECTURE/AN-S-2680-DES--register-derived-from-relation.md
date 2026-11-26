---
atom_family: SPEC
atom_id: AN-S-2680
container:
  component: C9
tier: 1
context:
  lens: DES
state:
  status: "active"
  version: 40
  updated_at: "2026-11-24T23:26:21.445860+00:00"
---
## Summary

Register derived_from relation

## Claim

### Prose Claim

#### Applicability
direct derivation relations between exact represented content versions.

IS_DERIVED_FROM means the directed Relation from a derived represented content version to an exact source content version used to derive it. Version references identify the relevant states; this does not introduce a Revision entity.

The Host is a derived represented-content version and the Target is the exact source content version used to derive it.
Forward `Host ((IS_DERIVED_FROM)) Target` and reverse `Target <((IS_DERIVED_FROM)) Host` are views of the same Relation fact.
IS_DERIVED_FROM relates derived represented content version to exact source content version.
### Formal Claim

```python
from anechoic.formal_claims import declare_relation

declare_relation(
    relation_name='IS_DERIVED_FROM',
    source_endpoint={'level': 'instances', 'reference_form': 'represented_content_version'},
    target_endpoint={'level': 'instances', 'reference_form': 'exact_source_content_version'},
)
```
