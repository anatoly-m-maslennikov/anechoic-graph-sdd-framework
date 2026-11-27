---
atom_family: SPEC
atom_id: AN-S-5018
container:
  component: C75
tier: 1
context:
  template: component_manifest
  lens: SPEC
state:
  status: draft
  version: 1
  updated_at: '2026-11-26T21:05:53.403332+00:00'
---

## Summary

Declare Project Structure

## Component Identity

```python
from anechoic.model import ComponentManifest

ComponentManifest(
    component_id='C93',
    name='PROJECT_STRUCTURE',
    layer=2,
    lens_whitelist=['DES', 'SPEC'],
)
```

## Component Boundaries

```python
{'code': {
    'imports': [
        'ADAPTERS_C30__shared.CEILINGS', 'ADAPTERS_C30__shared.CarrierError',
        'ADAPTERS_C30__shared.LimitReached', 'ADAPTERS_C30__shared.ReadContext',
        'ADAPTERS_C30__shared.open_regular', 'ADAPTERS_C30__shared.native_header_view',
        'ADAPTERS_C30__shared.spec_folder_layout', 'ADAPTERS_C30__shared.select_manifest_carriers',
        'ADAPTERS_C30__shared.manifest_inputs', 'ADAPTERS_C30__shared.manifest_state_fields',
        'component_manifest__pub.parse_component_manifest_fields', 'code_access_rules__pub.parse_code_access',
        'lens_scopes__pub.compile_lens_groups', 'lens_scopes__pub.validate_lens_whitelist',
        'atom_reference__pub.derive_atom_ref', 'carrier_read__pub.parse_carrier',
        'project_manifest__pub.manifest_summary_fields',
        'component_seed_manifest__pub.read_component_seed_manifest',
    ],
    'exports': {'LAYER_2_PROJECT_STRUCTURE_C93__shared.compile_structure': {'shared': ['C50', 'CS1']}},
}, 'io': {'server': {'compile_project_structure': {
    'transport': 'in_process', 'entry': 'LAYER_2_PROJECT_STRUCTURE_C93__shared.compile_structure',
}}}, 'state': {'reads': ['active Project, Component, and Component Seed Manifests'], 'writes': []}}
```

## Component Contract

### Compile Project Structure against an admitted Model

#### Guarantee

Return Project Structure bound to the supplied Model fingerprint and Project Manifest digest. Include Component ownership, source pins, and Seed owners.

Reject invalid identity or containment, duplicate Component IDs or paths, and Structure inputs that change during compilation.

```python trace
declare_trace_contract(
    action='compile_project_structure',
    cases={
        'succeeded': {'must_effect': (('C93.structure_snapshot', 'ready'),)},
        'failed': {'forbid_effect': ('C93.structure_snapshot',)},
    },
)
```
