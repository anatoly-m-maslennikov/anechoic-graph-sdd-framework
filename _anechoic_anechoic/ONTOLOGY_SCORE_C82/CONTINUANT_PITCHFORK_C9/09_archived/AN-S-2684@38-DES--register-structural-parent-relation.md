---
atom_family: SPEC
atom_id: AN-S-2684
container:
  component: C9
tier: 1
context:
  lens: DES
state:
  status: "archived"
  version: 38
  updated_at: '2026-11-12T20:21:10.600815+00:00'
---
## Summary

Register structural parent relation

## Claim

### Prose Claim

#### Applicability
the Structural Parent Relation directed from a child to its immediate parent.

the Structural Parent Relation **must** be the kind-independent Structural ownership relation directed from a child **to** its immediate parent. Project Structure owns Scope Unit parent declarations; structural graph views derive the corresponding `structural_parent` edge **without** maintaining a second source. a Carrier's physical containment **must not** silently replace a declared logical parent.

The Host is a structural child and the Target is its immediate structural parent.
Forward `Host ((structural_parent)) Target` and reverse `Target <((structural_parent)) Host` are views of the same Relation fact.
structural_parent relates structural child to immediate structural parent.
### Formal Claim

```python
from anechoic.formal_claims import declare_relation

declare_relation(
    relation_name='structural_parent',
    source_endpoint={'level': 'instances'},
    target_endpoint={'level': 'instances'},
)
```

