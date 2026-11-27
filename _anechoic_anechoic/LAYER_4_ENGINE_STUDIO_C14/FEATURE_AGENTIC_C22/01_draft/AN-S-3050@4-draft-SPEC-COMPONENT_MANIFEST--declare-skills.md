---
atom_family: SPEC
atom_id: AN-S-3050
container:
  component: C22
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

Declare SKILLS

## Formal manifest

```python
from anechoic.formal_claims import declare_entity
from anechoic.model import ComponentManifest

declare_entity(
    entity_name='Component Manifest',
    instance=ComponentManifest(
        component_id='C23',
        name='SKILLS',
        lens_whitelist=['DES', 'DevOps', 'QA', 'SWD'],
        boundaries={'code': {'exports': {}, 'imports': {'only': []}},
                    'state': {'reads': [], 'writes': []},
                    'io': {'server': {'guided_anechoic_mcp_use': {'outcomes': {
                        'guidance_provided': {
                            'must_effect': [('guidance.tools', 'discovery_required'), ('guidance.tool_help', 'reading_required'), ('guidance.project_binding', 'preservation_required'), ('guidance.mcp_operation', 'use_required'), ('guidance.result', 'verification_required'), ('guidance.blockers', 'reporting_required')],
                            'forbid_effect': ['mcp_operation'],
                        },
                    }}}}},
    ),
)
```

## Boundary scope

This definition covers the ane skill carrier. It provides instructions for a consumer; it performs no MCP calls or state effects.
