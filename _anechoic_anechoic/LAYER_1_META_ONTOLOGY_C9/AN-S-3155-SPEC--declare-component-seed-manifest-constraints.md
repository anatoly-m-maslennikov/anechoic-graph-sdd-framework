---
atom_family: SPEC
atom_id: AN-S-3155
container:
  component: C9
tier: 2
context:
  lens: SPEC
state:
  status: active
  version: 2
  updated_at: '2026-11-22T08:56:40.513203+00:00'
---

## Summary

Declare Component Seed Manifest Constraints

## Claim scope

MODEL//ANECHOIC <+ Node//Artifact//Atom//Spec Atom//Component Seed Manifest.Constraints

## Claim

### Formal Claim

```python
from anechoic.formal_claims import declare_entity
from anechoic.model import ComponentSeedManifest

def check_component_seed_manifest(spec: ComponentSeedManifest) -> bool:
    return bool(spec.component_seed_id.startswith("CS") and spec.component_seed_id[2:].isascii()
                and spec.component_seed_id[2:].isdigit() and spec.purpose.strip() and spec.solution.strip())

declare_entity(
    entity_name='Component Seed Manifest Constraints',
    constraints_for='Node//Artifact//Atom//Spec Atom//Component Seed Manifest',
    instance_relation_constraints={'CONTAINED_BY': {'target_entity_paths': ('Node//Artifact//Component',), 'targets_per_source': 1}},
    instance_check=check_component_seed_manifest,
)
```
