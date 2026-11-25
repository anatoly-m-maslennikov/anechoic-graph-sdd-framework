---
atom_family: SPEC
atom_id: AN-S-3062
container:
  component: C24
tier: 4
context:
  template: component_manifest
  lens: SPEC
state:
  status: draft
  version: 4
  updated_at: "2026-11-24T23:12:55.813309+00:00"
---

## Summary

Declare AUTONOMOUS_ATOM_REWRITE_PROMPT

## Formal manifest

```python
from anechoic.formal_claims import declare_entity
from anechoic.model import ComponentManifest

declare_entity(
    entity_name='Component Manifest',
    instance=ComponentManifest(
        component_id='C55',
        name='AUTONOMOUS_ATOM_REWRITE_PROMPT',
        lens_whitelist=['DES'],
        boundaries={'code': {'imports': {'only': []}},
                    'state': {'reads': [], 'writes': []},
                    'io': {'server': {'autonomous_atom_rewrite': {'outcomes': {'draft_reported': {
                        'must_effect': [('source_meaning_guidance', 'provided'), ('uncertainty_guidance', 'required')],
                        'forbid_effect': ['draft_lifecycle', 'draft_write', 'carrier_state']}}}}}},
    ),
)
```

## Boundary scope

This definition covers autonomous_atom_rewrite.prompt.md. The carrier instructs a consumer; it does not perform the described lifecycle calls or state effects.
