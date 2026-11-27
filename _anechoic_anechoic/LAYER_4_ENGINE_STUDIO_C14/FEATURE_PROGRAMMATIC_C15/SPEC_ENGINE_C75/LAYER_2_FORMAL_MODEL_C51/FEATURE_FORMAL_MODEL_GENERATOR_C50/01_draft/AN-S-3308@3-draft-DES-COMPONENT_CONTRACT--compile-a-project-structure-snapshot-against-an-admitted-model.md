---
atom_family: SPEC
atom_id: AN-S-3308
container:
  component: C50
tier: 0
context:
  template: component_contract
  lens: DES
relations:
  ANSWERS:
  - AN-S-3065
state:
  status: draft
  version: 3
  updated_at: '2026-11-25T09:37:43Z'
---
## Summary

Compile a Project Structure snapshot against an admitted Model

## Guarantee

Compile a selected Project Manifest against the admitted Model.
Include the Seed properties for each admitted Component Seed.

Reject invalid Component identity or containment, duplicate Component
paths, and inputs that change during compilation.

Verify that a supplied previous image is an admitted immutable image.
For staged native Model Claims, require its selection to match the
staged Claims and reject inventory changes. For the bundled Model, use
the reviewed fingerprint.

## Claim

### Prose Claim

The record property names identify logical Structure fields.

### Formal Claim

```python cli
declare_cli_contract(
    interface='manifest_compile',
    action='compile_project_structure',
    runner='managed_python',
    module='LAYER_4_ENGINE_STUDIO_C14.FEATURE_PROGRAMMATIC.SPEC_ENGINE_C75.compile_project__pub',
    checks={
        'output_format': {
            'encoding': 'json',
            'record_properties': (
                'project_manifest_reference', 'project_manifest_digest',
                'component_ownership', 'component_source_pins',
                'component_seed_owner', 'component_seed_manifest_reference',
            ),
        },
    },
)
```

The following logical outcomes cover only staging with a supplied previous
image. They do not specify wire data or exact selection and inventory values.

```python trace
declare_trace_contract(
    action='stage_previous_image', output='accepted',
    must_effect=(('previous_image_selection', 'matched'), ('staged_source_inventory', 'unchanged'), ('previous_image', 'accepted')),
    must_precede=((('previous_image_selection', 'matched'), ('previous_image', 'accepted')), (('staged_source_inventory', 'unchanged'), ('previous_image', 'accepted'))),
)
```

```python trace
declare_trace_contract(action='stage_previous_image', output='unavailable', forbid_effect=('previous_image',))
```

```python trace
declare_trace_contract(action='stage_previous_image', output='mismatch', forbid_effect=('previous_image',))
```

```python trace
declare_trace_contract(action='stage_previous_image', output='inventory_changed', forbid_effect=('previous_image',))
```
