---
atom_family: SPEC
atom_id: AN-S-3375
container:
  component: C50
tier: 1
context:
  template: DECISION
  lens: DES
relations:
  IS_SOLUTION_FOR:
  - AN-S-3308@3-draft
state:
  status: draft
  version: 3
  updated_at: '2026-11-25T09:37:43Z'
---

## Summary

Compile a Project Structure snapshot against an admitted Model.

## Claim

### Prose Claim

For the admitted-Model open path, request the Model from C53 and select
the Project Manifest in C50. Compile only after the Model opens and the
Project selection succeeds. Reject invalid or changed inputs. The formal
workflow covers this path of the compiler.

### Formal Claim

```python
component_workflow(
    component='C50',
    action='compile_project_structure',
    machine={
        'id': 'c50_compile_project_structure',
        'initial': 'idle',
        'states': {
            'idle': {'on': {
                'compilation_requested': {'target': 'admitting', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'trigger', 'target': 'manifest_compile', 'detail': {
                        'transport': 'cli', 'runner': 'managed_python',
                        'module': 'LAYER_4_ENGINE_STUDIO_C14.FEATURE_PROGRAMMATIC.SPEC_ENGINE_C75.compile_project__pub',
                    }}}},
            }},
            'admitting': {'on': {
                'request_admitted_model': {'target': 'opening_model', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'effect', 'target': 'C53', 'outcome': 'requested',
                     'detail': {'interface': 'admitted_model', 'transport': 'in_process',
                                'entry': 'FEATURE_MODEL_VALIDATION__shared.open_admitted_model',
                                'action': 'open_admitted_model'}}}},
                'admission_or_selection_rejected': {'target': 'failed', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'output', 'outcome': 'failed'}}},
            }},
            'opening_model': {'on': {
                'admitted_model_opened': {'target': 'selecting_project', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'effect', 'target': 'C53.admitted_model', 'outcome': 'opened',
                     'detail': {'component': 'C53', 'action': 'open_admitted_model', 'output': 'succeeded'}}}},
                'admission_or_selection_rejected': {'target': 'failed', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'output', 'outcome': 'failed'}}},
            }},
            'selecting_project': {'on': {
                'project_selected': {'target': 'compiling', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'effect', 'target': 'C50.project_manifest', 'outcome': 'selected'}}},
                'admission_or_selection_rejected': {'target': 'failed', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'output', 'outcome': 'failed'}}},
            }},
            'compiling': {'on': {
                'compile_structure_snapshot': {'target': 'responding', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'effect', 'target': 'C50', 'outcome': 'compiled'}}},
                'invalid_or_changed_inputs': {'target': 'failed', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'output', 'outcome': 'failed'}}},
            }},
            'responding': {'on': {
                'snapshot_returned': {'target': 'succeeded', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'output', 'outcome': 'succeeded', 'detail': {
                        'encoding': 'json', 'record_properties': ['project_manifest_reference', 'project_manifest_digest', 'component_ownership', 'component_source_pins', 'component_seed_owner', 'component_seed_manifest_reference'],
                    }}}},
            }},
            'succeeded': {'type': 'final'},
            'failed': {'type': 'final'},
        },
    },
)
```

The following workflow covers only staging with a supplied previous image.
The outcome names are logical; the CLI wire data and exact values remain
unresolved.

```python
component_workflow(
    component='C50', action='stage_previous_image',
    machine={
        'id': 'c50_stage_previous_image', 'initial': 'idle',
        'states': {
            'idle': {'on': {
                'previous_image_supplied': {'target': 'checking_image', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'trigger', 'target': 'image_model_stage', 'detail': {
                        'transport': 'cli', 'runner': 'managed_python',
                        'module': 'LAYER_4_ENGINE_STUDIO_C14.FEATURE_PROGRAMMATIC.SPEC_ENGINE_C75.LAYER_2_FORMAL_MODEL_C51.FEATURE_FORMAL_MODEL_GENERATOR.manifest_compiler_CS1.image_model_stage'}}}},
            }},
            'checking_image': {'on': {
                'image_available': {'target': 'matching_selection', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'effect', 'target': 'previous_image_availability', 'outcome': 'available'}}},
                'image_unavailable': {'target': 'unavailable', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'output', 'outcome': 'unavailable'}}},
                'inventory_changed': {'target': 'inventory_changed', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'output', 'outcome': 'inventory_changed'}}},
            }},
            'matching_selection': {'on': {
                'selection_matched': {'target': 'checking_inventory', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'effect', 'target': 'previous_image_selection', 'outcome': 'matched'}}},
                'selection_mismatched': {'target': 'mismatch', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'output', 'outcome': 'mismatch'}}},
                'inventory_changed': {'target': 'inventory_changed', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'output', 'outcome': 'inventory_changed'}}},
            }},
            'checking_inventory': {'on': {
                'inventory_unchanged': {'target': 'accepting', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'effect', 'target': 'staged_source_inventory', 'outcome': 'unchanged'}}},
                'inventory_changed': {'target': 'inventory_changed', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'output', 'outcome': 'inventory_changed'}}},
            }},
            'accepting': {'on': {
                'accept_previous_image': {'target': 'responding', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'effect', 'target': 'previous_image', 'outcome': 'accepted'}}},
                'inventory_changed': {'target': 'inventory_changed', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'output', 'outcome': 'inventory_changed'}}},
            }},
            'responding': {'on': {
                'accepted': {'target': 'accepted', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'output', 'outcome': 'accepted'}}},
            }},
            'accepted': {'type': 'final'}, 'unavailable': {'type': 'final'},
            'mismatch': {'type': 'final'}, 'inventory_changed': {'type': 'final'},
        },
    },
)
```
