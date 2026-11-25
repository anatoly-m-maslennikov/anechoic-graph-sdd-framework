---
atom_family: SPEC
atom_id: AN-S-3043
container:
  component: C14
tier: 4
context:
  template: component_manifest
  lens: SPEC
state:
  status: draft
  version: 4
  updated_at: '2026-11-25T12:36:15+00:00'
---

## Summary

Declare AGENTIC

## Purpose

This definition delegates prompt guidance to C24 and skill guidance to C23. Its direct definition has no executable imports, exports, reads, or writes. The delegated Components retain their own boundaries.

## Formal manifest

```python
from anechoic.formal_claims import declare_entity
from anechoic.model import ComponentManifest

declare_entity(
    entity_name='Component Manifest',
    instance=ComponentManifest(
        component_id='C22',
        name='AGENTIC',
        lens_whitelist=['DES', 'DevOps', 'SPEC', 'SWD'],
        boundaries={
            'code': {'imports': []},
            'state': {'reads': [], 'writes': []},
            'io': {'server': {'consume_agent_guidance': {
                'outcomes': {'guidance_received': {
                    'must_effect': [('guidance', 'available')],
                    'forbid_effect': ['operation_execution'],
                }},
            }}},
        },
    ),
)
```
