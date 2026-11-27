---
atom_family: SPEC
atom_id: AN-S-4931
container:
  component: C94
tier: 1
context:
  template: component_manifest
  lens: SPEC
state:
  status: active
  version: 1
  updated_at: '2026-11-25T20:39:08.202192+00:00'
---
## Summary

Declare Lean Translator

## Purpose

Take pinned declarations and translate the model normalized by C85
into Lean declarations.

## Component Identity

```python
from anechoic.formal_claims import declare_entity
from anechoic.model import ComponentManifest

declare_entity(
    entity_name='Component Manifest',
    instance=ComponentManifest(component_id='C84', layer=3, name='Lean Translator', lens_whitelist=['DES', 'SPEC']),
)
```

## Component Boundaries

```python
{'code': {'exports': {'_package__shared.capture_lean_json': {'shared': ['C75']},
                      '_package__shared._JSON_INTEGER_RULE': {'shared': ['C88']},
                      '_package__shared._effect': {'shared': ['C88']},
                      '_package__shared._effect_rules': {'shared': ['C88']},
                      '_package__shared._program': {'shared': ['C88',
                                                               'LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/SPEC_ENGINE_C75/LAYER_2_FORMAL_SPECIFICATION_C94/LAYER_3_LEAN_TRANSLATOR_C84/LEAN_TRANSLATOR_C84__tests/functional',
                                                               'LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/SPEC_ENGINE_C75/LAYER_2_FORMAL_SPECIFICATION_C94/LAYER_4_TRANSLATION_VALIDATOR_C86/LAYER_4_TRANSLATION_VALIDATOR_C86__tests/functional',
                                                               'LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/SPEC_ENGINE_C75/SPEC_ENGINE_C75__tests/functional']},
                      '_package__shared.compile_lean': {'shared': ['C75',
                                                                   'C88',
                                                                   'C89',
                                                                   'LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/SPEC_ENGINE_C75/LAYER_2_FORMAL_SPECIFICATION_C94/LAYER_3_LEAN_TRANSLATOR_C84/LEAN_TRANSLATOR_C84__tests/functional',
                                                                   'LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/SPEC_ENGINE_C75/LAYER_2_FORMAL_SPECIFICATION_C94/LAYER_4_TRANSLATION_VALIDATOR_C86/LAYER_4_TRANSLATION_VALIDATOR_C86__tests/functional',
                                                                   'LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/SPEC_ENGINE_C75/SPEC_ENGINE_C75__tests/functional']},
                      '_package__shared.framing_to_lean': {'shared': ['LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/SPEC_ENGINE_C75/SPEC_ENGINE_C75__tests/functional']},
                      '_package__shared.lean_string': {'shared': ['C74',
                                                                  'C88',
                                                                  'LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/SPEC_ENGINE_C75/LAYER_2_FORMAL_SPECIFICATION_C94/LAYER_4_TRANSLATION_VALIDATOR_C86/LAYER_4_TRANSLATION_VALIDATOR_C86__tests/functional',
                                                                  'LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/SPEC_ENGINE_C75/SPEC_ENGINE_C75__tests/functional']},
                      '_package__shared.run_lean_json': {'shared': ['C86',
                                                                    'C88',
                                                                    'LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/SPEC_ENGINE_C75/LAYER_2_FORMAL_SPECIFICATION_C94/LAYER_3_LEAN_TRANSLATOR_C84/LEAN_TRANSLATOR_C84__tests/functional',
                                                                    'LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/SPEC_ENGINE_C75/LAYER_2_FORMAL_SPECIFICATION_C94/LAYER_4_TRANSLATION_VALIDATOR_C86/LAYER_4_TRANSLATION_VALIDATOR_C86__tests/functional',
                                                                    'LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/SPEC_ENGINE_C75/SPEC_ENGINE_C75__tests/functional']}}},
 'io': {'server': {'compile_lean': {'outcomes': {'compiled': {'must_effect': [('C84.lean_source',
                                                                               'generated',
                                                                               {'model': 'request_normalized_model'})]}}},
                   'run_lean_json': {'transport': 'in_process',
                                     'entry': '_package__shared.run_lean_json',
                                     'outcomes': {'fulfilled': {'must_effect': [('C84.lean_evaluation',
                                                                                 'returned')]},
                                                  'failed': {'must_effect': [('C84.lean_evaluation',
                                                                              'failed')]}}}}}}
```

## Component Contract

Obtain normalized claims and source-linked gaps from C85. Encode the
claims with their source references and return the Lean source and those
normalized results.


```python trace
declare_trace_contract(
    action='compile_lean',
    output='compiled',
    must_effect=(('C84.lean_source', 'generated', {'model': 'request_normalized_model'}),),
)
```

Run the supplied Lean program and decode its JSON output. Return the decoded
value on success. Raise `ValueError` for process or JSON decoding failure.

```python trace
declare_trace_contract(
    interface='run_lean_json', transport='in_process', action='run_lean_json',
    output='fulfilled', must_effect=(('C84.lean_evaluation', 'returned'),),
)
```

```python trace
declare_trace_contract(
    interface='run_lean_json', transport='in_process', action='run_lean_json',
    output='failed', must_effect=(('C84.lean_evaluation', 'failed'),),
)
```
