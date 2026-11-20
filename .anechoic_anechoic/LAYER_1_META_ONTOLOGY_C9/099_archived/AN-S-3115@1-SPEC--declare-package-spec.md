---
identity:
  atom_id: AN-S-3115
context:
  container:
    component: C9
  lens: SPEC
state:
  status: archived
  version: 1
  updated_at: '2026-11-20T11:17:59+00:00'
---

## Summary

Declare Package Spec

## Claim scope

MODEL//ANECHOIC <+ Node//Artifact//Atom//Spec Atom//Package Spec

## Claim

### Formal Claim

```python
from anechoic.formal_claims import declare_entity
from anechoic.model import SpecAtom

class PackageSpec(SpecAtom):
    package_id: str
    purpose: str
    contract: str
    tier: int | None = None

def check_package_spec(spec: PackageSpec) -> bool:
    return bool(spec.package_id.strip() and spec.package_id != spec.atom_id
                and spec.purpose.strip() and spec.contract.strip())

declare_entity(
    entity_name="Package Spec",
    entity_class=PackageSpec,
    instance_relation_constraints={
        "CONTAINED_BY": {"target_entity_paths": ("Node//Artifact//Component",), "targets_per_source": 1},
    },
    instance_check=check_package_spec,
)
```
