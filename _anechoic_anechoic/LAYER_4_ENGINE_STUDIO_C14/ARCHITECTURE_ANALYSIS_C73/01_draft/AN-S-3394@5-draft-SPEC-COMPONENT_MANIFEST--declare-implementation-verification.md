---
atom_family: SPEC
atom_id: AN-S-3394
container:
  component: C73
tier: 4
context:
  template: component_manifest
  lens: SPEC
state:
  status: draft
  version: 5
  updated_at: '2026-11-25T14:01:36.204750+00:00'
---
## Summary

Declare Implementation Verification

## Purpose

Derive bounded Lean models from authored implementation and Realization Graph facts, including code units, calls, conditions, and effects. Keep source references and report unresolved coverage. Compare with the Lean model supplied by Spec Engine when a matching Spec exists.

## Formal manifest

```python
from anechoic.formal_claims import declare_entity
from anechoic.model import ComponentManifest

declare_entity(
    entity_name='Component Manifest',
    instance=ComponentManifest(
        component_id='C74',
        name='Implementation Verification',
        lens_whitelist=['DES', 'SPEC'],
        boundaries={'code': {'exports': {'carrier_compare.compare': {'private': ['LAYER_4_ENGINE_STUDIO_C14/ARCHITECTURE_ANALYSIS_C73/IMPLEMENTATION_VERIFICATION_C74/IMPLEMENTATION_VERIFICATION_C74__tests/functional']},
                     'carrier_formal._PATHS': {'private': ['LAYER_4_ENGINE_STUDIO_C14/ARCHITECTURE_ANALYSIS_C73/IMPLEMENTATION_VERIFICATION_C74/IMPLEMENTATION_VERIFICATION_C74__tests/functional']},
                     'carrier_formal.formal_inputs': {'private': ['LAYER_4_ENGINE_STUDIO_C14/ARCHITECTURE_ANALYSIS_C73/IMPLEMENTATION_VERIFICATION_C74/IMPLEMENTATION_VERIFICATION_C74__tests/functional']},
                     'carrier_model._SOURCE': {'private': ['LAYER_4_ENGINE_STUDIO_C14/ARCHITECTURE_ANALYSIS_C73/IMPLEMENTATION_VERIFICATION_C74/IMPLEMENTATION_VERIFICATION_C74__tests/functional']},
                     'carrier_model.generate': {'private': ['LAYER_4_ENGINE_STUDIO_C14/ARCHITECTURE_ANALYSIS_C73/IMPLEMENTATION_VERIFICATION_C74/IMPLEMENTATION_VERIFICATION_C74__tests/functional']},
                     'carrier_runtime_effects': {'private': ['LAYER_4_ENGINE_STUDIO_C14/ARCHITECTURE_ANALYSIS_C73/IMPLEMENTATION_VERIFICATION_C74/IMPLEMENTATION_VERIFICATION_C74__tests/functional']},
                     'shape_implementation.compare': 'public'},
         'imports': {'only': ['ADAPTERS_C30__shared.formal_claim_fences',
                              'ADAPTERS_C30__shared.frontmatter_bounds',
                              'ADAPTERS_C30__shared.parse_carrier',
                              'ADAPTERS_C30__shared.parse_component_manifest',
                              'ADAPTERS_C30__shared.source_body',
                              'FEATURE_PROGRAMMATIC.SPEC_ENGINE_C75._package__shared.generate_framing_cases',
                              'FEATURE_PROGRAMMATIC.SPEC_ENGINE_C75._package__shared.verify_formal_chain',
                              'FEATURE_PROGRAMMATIC.SPEC_ENGINE_C75.LAYER_2_FORMAL_SPECIFICATION_C94.LAYER_2_SPEC_READING_C83.SPECIFICATION_MODEL_C85._package__shared.parse_contract',
                              'FEATURE_PROGRAMMATIC.SPEC_ENGINE_C75.LAYER_2_FORMAL_SPECIFICATION_C94.LAYER_3_LEAN_TRANSLATOR_C84._package__shared.lean_string',
                              'FEATURE_PROGRAMMATIC.SPEC_ENGINE_C75.LAYER_2_FORMAL_SPECIFICATION_C94.LAYER_4_SPEC_COMPARISON_C88._package__shared.manifest_tool_api',
                              'WORKERS_beta_C69__shared.python_code_units',
                              'carrier_compare.compare',
                              'carrier_formal._PATHS',
                              'carrier_formal.formal_inputs',
                              'carrier_model._SOURCE',
                              'carrier_model.generate',
                              'carrier_runtime_effects',
                              'shape_implementation.compare']}},
        'state': {
            'reads': ['selected implementation source and formal inputs'],
            'writes': ['temporary Lean comparison file', 'Lean files in the requested emit directory'],
        },
        'io': {
            'server': {
                'carrier_compare': {
                    'transport': 'cli',
                    'runner': 'managed_python',
                    'module': 'ARCHITECTURE_ANALYSIS_C73.IMPLEMENTATION_VERIFICATION_C74.carrier_compare',
                    'arguments': ['--root <project-root>', '[--lean <executable>]', '[--formal-only]'],
                    'outcomes': {'compared': {'must_effect': [
                        ('carrier_model', 'built'), ('source_evidence', 'retained'), ('selected_cases', 'compared'),
                    ]}, 'unresolved': {'must_effect': [
                        ('coverage', 'unresolved'),
                    ]}},
                },
                'carrier_compare_formal_only': {'outcomes': {
                    'formal_compared': {
                        'must_effect': [('formal_cases', 'compared')],
                        'forbid_effect': ['carrier_model', 'source_evidence'],
                    },
                    'unresolved': {'must_effect': [('coverage', 'unresolved')]},
                }},
                'backend_http_compare': {
                    'transport': 'cli',
                    'runner': 'managed_python',
                    'module': 'ARCHITECTURE_ANALYSIS_C73.IMPLEMENTATION_VERIFICATION_C74.backend_http_compare',
                    'arguments': ['--root <project-root>', '[--lean <executable>]', '[--emit <directory>]', '[--formal-only]'],
                },
            },
        },
        },
    ),
)
```
