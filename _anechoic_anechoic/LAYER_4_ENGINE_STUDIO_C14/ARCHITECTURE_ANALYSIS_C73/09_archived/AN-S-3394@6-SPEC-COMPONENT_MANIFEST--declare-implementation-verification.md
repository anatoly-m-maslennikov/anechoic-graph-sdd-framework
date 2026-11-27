---
atom_family: SPEC
atom_id: AN-S-3394
container:
  component: C73
tier: 1
context:
  template: component_manifest
  lens: SPEC
state:
  status: archived
  version: 6
  updated_at: "2026-11-26T15:52:28.126871+00:00"
---
## Summary

Declare Implementation Verification

## Purpose

Derive bounded Lean models from authored implementation and Realization Graph facts, including code units, calls, conditions, and effects. Keep source references and report unresolved coverage. Compare with the Lean model supplied by Spec Engine when a matching Spec exists.

## Component Identity

```python
from anechoic.model import ComponentManifest

ComponentManifest(
    component_id='C74',
    name='Implementation Verification',
    lens_whitelist=['DES', 'SPEC'],
)
```

## Component Boundaries

```python
{'code': {'imports': {'only': ['WORKERS_beta_C69__shared.python_code_units',
                               'ADAPTERS_C30__shared.frontmatter_bounds',
                               'ADAPTERS_C30__shared.source_body',
                               'ADAPTERS_C30__shared.parse_carrier',
                               'ADAPTERS_C30__shared.parse_component_manifest',
                               'ADAPTERS_C30__shared.formal_claim_fences',
                               'carrier_compare.compare',
                               'carrier_model._SOURCE',
                               'carrier_model.generate',
                               'carrier_runtime_effects',
                               'carrier_formal._PATHS',
                               'carrier_formal.formal_inputs']},
          'exports': {'carrier_compare.compare': {'private': ['LAYER_4_ENGINE_STUDIO_C14/ARCHITECTURE_ANALYSIS_C73/IMPLEMENTATION_VERIFICATION_C74/IMPLEMENTATION_VERIFICATION_C74__tests/functional']},
                      'carrier_model._SOURCE': {'private': ['LAYER_4_ENGINE_STUDIO_C14/ARCHITECTURE_ANALYSIS_C73/IMPLEMENTATION_VERIFICATION_C74/IMPLEMENTATION_VERIFICATION_C74__tests/functional']},
                      'carrier_model.generate': {'private': ['LAYER_4_ENGINE_STUDIO_C14/ARCHITECTURE_ANALYSIS_C73/IMPLEMENTATION_VERIFICATION_C74/IMPLEMENTATION_VERIFICATION_C74__tests/functional']},
                      'carrier_runtime_effects': {'private': ['LAYER_4_ENGINE_STUDIO_C14/ARCHITECTURE_ANALYSIS_C73/IMPLEMENTATION_VERIFICATION_C74/IMPLEMENTATION_VERIFICATION_C74__tests/functional']},
                      'carrier_formal._PATHS': {'private': ['LAYER_4_ENGINE_STUDIO_C14/ARCHITECTURE_ANALYSIS_C73/IMPLEMENTATION_VERIFICATION_C74/IMPLEMENTATION_VERIFICATION_C74__tests/functional']},
                      'carrier_formal.formal_inputs': {'private': ['LAYER_4_ENGINE_STUDIO_C14/ARCHITECTURE_ANALYSIS_C73/IMPLEMENTATION_VERIFICATION_C74/IMPLEMENTATION_VERIFICATION_C74__tests/functional']}}},
 'state': {'reads': ['selected carrier source and formal inputs'],
           'writes': ['temporary Lean comparison file']},
 'io': {'server': {'carrier_compare': {'transport': 'cli',
                                       'runner': 'managed_python',
                                       'module': 'ARCHITECTURE_ANALYSIS_C73.IMPLEMENTATION_VERIFICATION_C74.carrier_compare',
                                       'arguments': ['--root '
                                                     '<project-root>',
                                                     '[--lean '
                                                     '<executable>]']}}}}
```

## Component Contract

### Compare a bounded carrier model

#### Guarantee

For the selected carrier pilot, derive a Lean model from the admitted Python source and compare observed cases with the supplied formal Contract and Draft Solution. Retain source evidence and report unresolved coverage or execution failures. This pilot does not compile arbitrary Python Specs to Lean.
