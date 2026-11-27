---
atom_family: SPEC
atom_id: AN-S-4933
container:
  component: C94
tier: 1
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

## Component Identity

```python
from anechoic.formal_claims import declare_entity
from anechoic.model import ComponentManifest

declare_entity(
    entity_name='Component Manifest',
    instance=ComponentManifest(component_id='C86', layer=4, name='Translation Validator', lens_whitelist=['DES', 'SPEC']),
)
```

## Component Boundaries

```python
{'code': {'exports': {'_package__shared.validate_translation': {'shared': ['C75',
                                                                           'LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/SPEC_ENGINE_C75/LAYER_2_FORMAL_SPECIFICATION_C94/LAYER_4_TRANSLATION_VALIDATOR_C86/LAYER_4_TRANSLATION_VALIDATOR_C86__tests/functional']}}},
 'io': {'server': {'validate_translation': {'outcomes': {'matched': {'must_effect': [('C86.lean_declarations',
                                                                                      'validated',
                                                                                      {'model': 'request_normalized_model'})],
                                                                     'forbid_effect': ['C86.translation_findings']},
                                                         'bounded_match': {'must_effect': [('C86.framing_comparison',
                                                                                            'reported')]},
                                                         'conflicting': {'must_effect': [('C86.translation_findings',
                                                                                          'reported')]},
                                                         'unresolved': {'must_effect': [('C86.translation_findings',
                                                                                         'reported')]}}}},
        'client': {'lean_evaluation': {'component': 'C84',
                                       'interface': 'run_lean_json',
                                       'transport': 'in_process'}}}}
```

## Component Contract

Compare emitted Lean declarations with the normalized source and check
applicable executable shapes. Report conflicts and unresolved expectations.
If the framing witnesses pass on the default path, report the witness count
and leave framing equivalence unresolved.

On a bounded framing request, return `bounded_match` when the declaration
checks and the finite byte witnesses for both framing roles pass and no issue
or unresolved translation finding remains. Report the witness input bytes,
the results for both roles, and unresolved coverage. Unbounded framing
equivalence remains unresolved.


```python trace
declare_trace_contract(
    action='validate_translation',
    output='matched',
    must_effect=(('C86.lean_declarations', 'validated', {'model': 'request_normalized_model'}),),
    forbid_effect=('C86.translation_findings',),
)
```

```python trace
declare_trace_contract(
    action='validate_translation',
    output='bounded_match',
    must_effect=(('C86.framing_comparison', 'reported'),),
    value_types={('C86.framing_comparison', 'witnesses'): 'nonempty_array'},
)
```

```python trace
declare_trace_contract(
    action='validate_translation',
    output='conflicting',
    must_effect=(('C86.translation_findings', 'reported'),),
)
```

```python trace
declare_trace_contract(
    action='validate_translation',
    output='unresolved',
    must_effect=(('C86.translation_findings', 'reported'),),
)
```

A Lean execution or result-shape error raises before translation validation
returns. The failure cannot publish validated declarations.

```python trace
declare_trace_contract(
    action='validate_translation',
    output='failed',
    forbid_effect=('C86.lean_declarations',),
)
```
