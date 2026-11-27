---
atom_family: SPEC
atom_id: AN-S-5021
container:
  component: C75
tier: 1
context:
  template: component_manifest
  lens: SPEC
state:
  status: archived
  version: 1
  updated_at: '2026-11-26T21:24:56+00:00'
---
## Summary

Declare Source Adapters

## Purpose

Read pinned Spec carriers and validate source identity without executing source.

## Component Identity

```python
from anechoic.model import ComponentManifest

ComponentManifest(
    component_id='C95',
    layer=1,
    name='Source Adapters',
    lens_whitelist=['DES', 'SPEC'],
)
```

## Component Boundaries

```python
{'code': {'imports': ['atom_reference__pub.derive_atom_ref', 'spec_file_reader.read_spec_file'],
          'exports': {'_package__shared.SpecSnapshot': {'shared': ['C75', 'LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/SPEC_ENGINE_C75/SPEC_ENGINE_C75__tests/functional']},
                      '_package__shared.SourceError': {'shared': ['C83', 'LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/SPEC_ENGINE_C75/SPEC_ENGINE_C75__tests/functional',
                          'LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/SPEC_ENGINE_C75/LAYER_2_FORMAL_SPECIFICATION_C94/LAYER_2_SPEC_READING_C83']},
                      '_package__shared.read_source': {'shared': ['C83',
                          'LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/SPEC_ENGINE_C75/LAYER_2_FORMAL_SPECIFICATION_C94/LAYER_2_SPEC_READING_C83']}}},
 'state': {'reads': ['pinned Spec carrier files'], 'writes': []}}
```

## Component Contract

### Read a pinned Spec

#### Guarantee

Return the parsed carrier and its SHA-256 digest when its identity and state
match the supplied pin. Reject a path outside the Project or a carrier that
differs from the pin.
