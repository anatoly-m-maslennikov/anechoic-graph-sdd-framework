---
atom_family: SPEC
atom_id: AN-S-4930
container:
  component: C94
tier: 1
context:
  template: component_manifest
  lens: SPEC
state:
  status: active
  version: 2
  updated_at: '2026-11-27T13:09:58.959794+00:00'
---
## Summary

Declare Spec Reading

## Purpose

Validate declarations and links from pinned Spec sources supplied by C95.
Managed reads use the staged snapshot. Offline reads use explicit file pins.

## Component Identity

```python
from anechoic.formal_claims import declare_entity
from anechoic.model import ComponentManifest

declare_entity(
    entity_name='Component Manifest',
    instance=ComponentManifest(
        component_id='C83',
        layer=2,
        name='Spec Reading',
        lens_whitelist=['DES', 'SPEC'],
    ),
)
```

## Component Boundaries

```python
{
            'code': {'exports': {'_package__shared.SourceError': {'shared': ['C75', 'C85', 'C89', 'LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/SPEC_ENGINE_C75/SPEC_ENGINE_C75__tests/functional']},
                         '_package__shared.read_source': {'shared': ['C89']},
                         '_package__shared.load_boundary_model': {'shared': ['C75',
                                                                             'C88',
                                                                             'C89',
                                                                             'LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/SPEC_ENGINE_C75/LAYER_2_FORMAL_SPECIFICATION_C94/LAYER_4_TRANSLATION_VALIDATOR_C86/LAYER_4_TRANSLATION_VALIDATOR_C86__tests/functional',
                                                                             'LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/SPEC_ENGINE_C75/SPEC_ENGINE_C75__tests/functional']},
                         '_package__shared.load_formal_claim': {'shared': ['C85',
                                                                           'C89',
                                                                           'LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/SPEC_ENGINE_C75/SPEC_ENGINE_C75__tests/functional']},
                         '_package__shared.load_manifest': {'shared': ['C85', 'C88',
                                                                       'C89',
                                                                       'LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/SPEC_ENGINE_C75/SPEC_ENGINE_C75__tests/functional']},
                         '_package__shared.recognized_claim': {'shared': ['LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/SPEC_ENGINE_C75/SPEC_ENGINE_C75__tests/functional']}},
             'imports': ['C30', 'C95', 'atom_reference__pub.derive_atom_ref']},
            'io': {'server': {'load_boundary_model': {'outcomes': {
                'loaded': {'must_effect': [('C83.pinned_sources', 'loaded')]},
            }}}},
        }
```

## Component Contract

Load the exact pinned Manifest, Contract, and Solution. Check their Component, declared roles, and required links. Preserve each source record supplied by C95, including its observed
carrier SHA-256. Return the same source records with the loaded roles.
Report unsupported claims with their source.

```python trace
declare_trace_contract(
    action='load_boundary_model',
    output='loaded',
    must_effect=(('C83.pinned_sources', 'loaded'),),
    same_values=((('C83.pinned_sources', 'source_pins'),
                  ('result_returned', 'source_pins')),),
    value_types={('C83.pinned_sources', 'source_pins'): 'object'},
)
```
