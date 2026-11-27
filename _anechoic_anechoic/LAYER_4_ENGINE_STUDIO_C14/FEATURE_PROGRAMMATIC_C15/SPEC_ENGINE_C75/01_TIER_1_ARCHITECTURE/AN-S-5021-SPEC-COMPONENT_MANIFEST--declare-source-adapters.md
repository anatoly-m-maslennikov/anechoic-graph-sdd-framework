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
  status: active
  version: 3
  updated_at: '2026-11-27T13:11:57.826197+00:00'
---
## Summary

Declare Source Adapters

## Purpose

Supply a consistent DuckDB snapshot of ingested sources to Spec Engine.

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
                      '_package__shared.SourceError': {'shared': ['C75', 'C83', 'C85', 'C89', 'LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/SPEC_ENGINE_C75/SPEC_ENGINE_C75__tests/functional',
                          'LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/SPEC_ENGINE_C75/LAYER_2_FORMAL_SPECIFICATION_C94/LAYER_2_SPEC_READING_C83']},
                      '_package__shared.read_source': {'shared': ['C83', 'C89',
                          'LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/SPEC_ENGINE_C75/SPEC_ENGINE_C75__tests/functional',
                          'LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/SPEC_ENGINE_C75/LAYER_2_FORMAL_SPECIFICATION_C94/LAYER_2_SPEC_READING_C83']}}},
 'state': {'reads': ['ingested Project Spec snapshot'], 'writes': []}}
```

## Component Contract

### Source adapters responsibilities

#### Guarantee

Receive one Project-bound snapshot with an admitted receipt through the Worker. Return the Header, body, exact ref, Project-relative path, and original carrier digest from that snapshot. The Spec Engine passes those rows to Formal Model, Project Structure, and Formal Specification. Confirm each requested pin. A pin contains the Project-relative
path, Atom ID, version, status, and container Component. If a pin
supplies SHA-256, it must equal the original carrier digest. Return
that digest even when the request omits it. Report unavailable until a snapshot has been ingested. Report a missing or mismatched pin as an explicit source error.

```python trace
declare_trace_contract(
    action='read_spec_snapshot',
    cases={
        'ready': {'must_effect': (('C95.source_snapshot', 'ready'),),
                  'value_types': {('C95.source_snapshot', 'snapshot_id'): 'nonempty_string'}},
        'unavailable': {'forbid_effect': ('C95.source_snapshot',)},
        'failed': {'forbid_effect': ('C95.source_snapshot',)},
    },
)
```
