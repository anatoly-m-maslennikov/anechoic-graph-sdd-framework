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
  version: 8
  updated_at: "2026-11-27T05:39:19.358055+00:00"
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
                               'FEATURE_PROGRAMMATIC.SPEC_ENGINE_C75._package__shared.verify_formal_chain',
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
 'state': {'reads': ['selected source pin request, carrier source and formal inputs'],
           'writes': ['temporary Lean comparison file']},
 'io': {'server': {'carrier_compare': {'transport': 'cli',
                                       'runner': 'managed_python',
                                       'module': 'ARCHITECTURE_ANALYSIS_C73.IMPLEMENTATION_VERIFICATION_C74.carrier_compare',
                                       'arguments': ['--root '
                                                     '<project-root>',
                                                     '[--lean '
                                                     '<executable>]',
                                                     '[--pins <source-pin-request.json>]',
                                                     '[--component C30|C90]']}}}}
```

## Component Contract

### Compare a bounded carrier model

#### Guarantee

Derive Lean from the pinned Python source and compare carrier bounds and body with the pinned Manifest Contract and Solution. Return source pins, checked cases, mismatches, and unresolved coverage in JSON.

With `--pins`, supply a JSON object with `manifest`, `solution`, and `implementation_sha256`. Each Spec pin supplies `path`, `atom_id`, `version`, `status`, `container_component`, and `sha256`. Paths in Spec pins are relative to the Project. The default C30 check covers the admitted framing operations and their witnesses.

With `--component C90 --pins`, translate the pinned Diagnostics implementation through Autoform. Compare each declared finding value equality with the Solution bindings and one executed Lean witness. Report unsupported evidence as unresolved.
