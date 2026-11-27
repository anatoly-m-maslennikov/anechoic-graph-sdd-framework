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
  status: archived
  version: 5
  updated_at: '2026-11-26T23:53:37.973370+00:00'
---

## Summary

Declare Project Structure

## Purpose

Compile the Project's Component and Seed Structure against an admitted Model.

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
        'component_manifest__pub.parse_component_manifest', 'code_access_rules__pub.parse_code_access',
        'lens_scopes__pub.compile_lens_groups', 'lens_scopes__pub.validate_lens_whitelist',
        'atom_reference__pub.derive_atom_ref', 'atom_reference__pub.COMPONENT_MANIFEST_FILENAME',
        'carrier_read__pub.parse_carrier',
        'project_manifest__pub.manifest_summary_fields',
        'component_seed_manifest__pub.read_component_seed_manifest',
        'source_row__pub.json_value',
    ],
    'exports': {'LAYER_2_PROJECT_STRUCTURE_C93__shared.compile_structure': {'shared': ['C75']},
                'LAYER_2_PROJECT_STRUCTURE_C93__rows.compile_structure_rows': {'shared': ['C75']}},
}, 'io': {'server': {'compile_project_structure': {
    'transport': 'in_process', 'entry': 'LAYER_2_PROJECT_STRUCTURE_C93__shared.compile_structure',
}, 'compile_pinned_structure': {
    'transport': 'in_process', 'entry': 'LAYER_2_PROJECT_STRUCTURE_C93__rows.compile_structure_rows',
}}}, 'state': {'reads': ['admitted Model', 'pinned Structure rows',
                         'active Project, Component, and Component Seed Manifests'], 'writes': []}}
```

## Component Contract

### Compile Project Structure against an admitted Model

#### Guarantee

Return Project Structure bound to the supplied Model fingerprint and Project Manifest digest. Include Component ownership, source pins, authored Component purposes, and Seed owners and fields.

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

### Compile from a staged snapshot

Consume the supplied snapshot rows and selected Manifest pin. Validate
containment against the supplied Model. Return the Structure with its
Model fingerprint, Project Manifest digest, and carrier pins.

```python trace
declare_trace_contract(action='compile_pinned_structure', interface='compile_pinned_structure',
    transport='in_process', cases={
        'succeeded': {'must_effect': (('C93.structure_snapshot', 'ready'),)},
        'failed': {'forbid_effect': ('C93.structure_snapshot',)},
})
```
