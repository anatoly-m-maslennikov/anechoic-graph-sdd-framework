---
atom_family: SPEC
atom_id: AN-S-3155
container:
  component: C9
tier: 2
context:
  lens: SPEC
state:
  status: archived
  version: 1
  updated_at: '2026-11-20T14:42:07.157939+00:00'
---

## Summary

Declare Package Spec Constraints

## Claim scope

MODEL//ANECHOIC <+ Node//Artifact//Atom//Spec Atom//Package Spec.Constraints

## Claim

### Formal Claim

```python
from anechoic.formal_claims import declare_entity
from anechoic.model import PackageSpec

def check_package_spec(spec: PackageSpec) -> bool:
    return bool(spec.package_id.strip() and spec.package_id != spec.atom_id
                and spec.purpose.strip() and spec.contract.strip())

declare_entity(
    entity_name='Package Spec Constraints',
    constraints_for='Node//Artifact//Atom//Spec Atom//Package Spec',
    instance_relation_constraints={'CONTAINED_BY': {'target_entity_paths': ('Node//Artifact//Component',), 'targets_per_source': 1}},
    instance_check=check_package_spec,
)
```
