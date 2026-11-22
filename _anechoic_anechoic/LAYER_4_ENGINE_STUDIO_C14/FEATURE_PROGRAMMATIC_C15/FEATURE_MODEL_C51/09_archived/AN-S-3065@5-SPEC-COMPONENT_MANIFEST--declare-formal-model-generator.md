---
atom_family: SPEC
atom_id: AN-S-3065
container:
  component: C51
tier: 0
context:
  template: component_manifest
  lens: SPEC
state:
  status: "archived"
  version: 5
  updated_at: "2026-11-22T03:15:21.193752+00:00"
---

## Summary

Declare FORMAL_MODEL_GENERATOR

## Formal manifest

```python
from anechoic.formal_claims import declare_entity
from anechoic.model import ComponentManifest

declare_entity(
    entity_name='Component Manifest',
    instance=ComponentManifest(
        component_id='C50',
        name='FORMAL_MODEL_GENERATOR',
        lens_whitelist=['DES', 'QA', 'SWD'],
        boundaries={'code': {'imports': [
            'native_model_claim__pub.NativeModelClaimError',
            'native_model_claim__pub.parse_native_model_claim',
            'model_class_subject__pub.model_class_target',
            'subject_notation__pub',
            'atom_reference__pub.derive_atom_ref',
            'carrier_compat__pub.matches_named_value',
        ]}},
    ),
)
```
