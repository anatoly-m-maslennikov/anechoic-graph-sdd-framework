---
atom_family: SPEC
atom_id: AN-S-3391
container:
  component: C14
tier: 4
context:
  template: component_manifest
  lens: SPEC
state:
  status: draft
  version: 3
  updated_at: "2026-11-24T23:12:55.813309+00:00"
---
## Summary

Declare Architecture Analysis

## Purpose

Measure the size of code and the Spec it realizes. Use ownership and dependency evidence to help maintainers review Package boundaries.

Delegate measuring code and Spec and reviewing Package boundaries to Code and Spec Metrics. Delegate checking implementation behavior against its formal Spec to Implementation Verification.

This Component delegates implementation to its child Components. A child report alone does not establish complete coverage. Coverage criteria remain open; report unresolved coverage until both children have complete coverage evidence. Each report must arrive before its child coverage is confirmed.

## Formal manifest

```python
from anechoic.formal_claims import declare_entity
from anechoic.model import ComponentManifest

declare_entity(
    entity_name='Component Manifest',
    instance=ComponentManifest(
        component_id='C73',
        name='Architecture Analysis',
        lens_whitelist=['DES', 'SPEC'],
        boundaries={
            'code': {'imports': []},
            'io': {'server': {'report_architecture_analysis': {'outcomes': {'complete': {
                'must_effect': [('file_and_spec_bindings', 'identified'), ('selected_cases', 'compared'),
                                ('C76', 'complete'), ('C74', 'complete')],
            }}}}},
        },
    ),
)
```
