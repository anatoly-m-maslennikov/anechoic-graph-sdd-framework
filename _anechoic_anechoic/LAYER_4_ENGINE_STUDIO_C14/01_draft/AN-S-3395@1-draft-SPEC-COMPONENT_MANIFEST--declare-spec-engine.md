---
atom_family: SPEC
atom_id: AN-S-3395
container:
  component: C14
tier: 4
context:
  template: component_manifest
  lens: SPEC
state:
  status: draft
  version: 1
  updated_at: '2026-11-23T04:22:11.735620+00:00'
---
## Summary

Declare Spec Engine

## Purpose

Validate formal Manifests, Contracts, and Solutions. Compare their
obligations and derive Lean and Mermaid from the same model.

Coordinate Spec Sources and Diagnostics (L1), Formal Model (L2),
Lean Translator and Mermaid Renderer (L3), Translation Validator
and Spec Comparison (L4), and Delegation Verification (L5).

## Formal manifest

```python
from anechoic.formal_claims import declare_entity
from anechoic.model import ComponentManifest

declare_entity(
    entity_name='Component Manifest',
    instance=ComponentManifest(
        component_id='C75',
        name='Spec Engine',
        lens_whitelist=['DES', 'SPEC'],
        boundaries={
            'io': {'server': {'verify_formal_chain': {'outcomes': {
                'compared': {'must_effect': [
                    ('C83.pinned_sources', 'loaded', {'component': 'C83', 'action': 'load_boundary_model', 'output': 'loaded'}),
                    ('C85.formal_declarations', 'normalized', {'component': 'C85', 'action': 'normalize_spec', 'output': 'normalized', 'model': 'request_normalized_model'}),
                    ('C84.lean_source', 'generated', {'component': 'C84', 'action': 'compile_lean', 'output': 'compiled', 'model': 'request_normalized_model'}),
                    ('C86.lean_declarations', 'validated', {'component': 'C86', 'action': 'validate_translation', 'output': 'matched', 'model': 'request_normalized_model'}),
                    ('C87.mermaid_diagram', 'rendered', {'component': 'C87', 'action': 'render_solution', 'output': 'rendered', 'model': 'request_normalized_model'}),
                    ('C88.manifest_contract', 'compared', {'component': 'C88', 'action': 'compare_obligations', 'output': 'compared'}),
                    ('C88.manifest_solution', 'compared', {'component': 'C88', 'action': 'compare_obligations', 'output': 'compared'}),
                    ('C88.contract_solution', 'compared', {'component': 'C88', 'action': 'compare_obligations', 'output': 'compared'}),
                    ('C75.comparison_complete', 'reported'),
                ]},
                'incomplete': {
                    'must_effect': [('C75.diagnostics', 'reported')],
                    'forbid_effect': ['C75.comparison_complete'],
                },
            }}}},
        },
    ),
)
```
