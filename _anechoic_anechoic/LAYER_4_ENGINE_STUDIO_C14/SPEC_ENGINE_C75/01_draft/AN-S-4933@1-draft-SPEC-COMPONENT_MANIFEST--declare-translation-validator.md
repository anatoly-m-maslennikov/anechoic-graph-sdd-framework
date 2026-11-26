---
atom_family: SPEC
atom_id: AN-S-4933
container:
  component: C75
tier: 4
context:
  template: component_manifest
  lens: SPEC
state:
  status: draft
  version: 1
  updated_at: '2026-11-25T20:39:08.202192+00:00'
---
## Summary

Declare Translation Validator

## Purpose

Check emitted Lean declarations and executable shapes against the
normalized source. Check framing with bounded byte witnesses. Report
unverified expectations and witness bounds.

## Formal manifest

```python
from anechoic.formal_claims import declare_entity
from anechoic.model import ComponentManifest

declare_entity(
    entity_name='Component Manifest',
    instance=ComponentManifest(
        component_id='C86',
        layer=4,
        name='Translation Validator',
        lens_whitelist=['DES', 'SPEC'],
        boundaries={
            'io': {'server': {'validate_translation': {'outcomes': {
                'matched': {'must_effect': [('C86.lean_declarations', 'validated')],
                            'forbid_effect': ['C86.translation_findings']},
                'conflicting': {'must_effect': [('C86.translation_findings', 'reported')]},
                'unresolved': {'must_effect': [('C86.translation_findings', 'reported')]},
            }}}},
        },
    ),
)
```
