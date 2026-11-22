---
atom_family: SPEC
atom_id: AN-S-3056
container:
  component: C15
tier: 0
context:
  template: component_manifest
  lens: SPEC
state:
  status: "archived"
  version: 3
  updated_at: "2026-11-22T01:14:11.426139+00:00"
---

## Summary

Declare TOOLS

## Formal manifest

```python
from anechoic.formal_claims import declare_entity
from anechoic.model import ComponentManifest

declare_entity(
    entity_name='Component Manifest',
    instance=ComponentManifest(
        component_id='C16',
        name='TOOLS',
        lens_whitelist=['DES', 'DevOps', 'QA', 'SPEC', 'SWD'],
        boundaries={
            'code': {
                'exports': {
                    'FEATURE_TOOLS__shared': None,
                    'FEATURE_TOOLS__shared.ScopeDeclarationError': None,
                    'FEATURE_TOOLS__shared.ScopeUnitDeclarations': None,
                    'FEATURE_TOOLS__shared.atomic_tempfile': None,
                    'FEATURE_TOOLS__shared.bind_native_runtime': None,
                    'FEATURE_TOOLS__shared.derive_atom_ref': None,
                    'FEATURE_TOOLS__shared.owned_temporary_root': None,
                    'FEATURE_TOOLS__shared.read_scope_unit_declarations': None,
                    'FEATURE_TOOLS__pub': 'public',
                    'FEATURE_TOOLS__pub.FailureRecord': 'public',
                    'FEATURE_TOOLS__pub.ExplicitBlockingRuntimeFailure': 'public',
                    'FEATURE_TOOLS__pub.operation_error_boundary': 'public',
                    'FEATURE_TOOLS__pub.report_failure': 'public',
                    'FEATURE_TOOLS__pub.run_process': 'public',
                    'FEATURE_TOOLS__pub.ManifestIdentity': 'public',
                    'FEATURE_TOOLS__pub.NativeProjectSelection': 'public',
                    'FEATURE_TOOLS__pub.ProjectSelection': 'public',
                    'FEATURE_TOOLS__pub.ProjectSelectionError': 'public',
                    'FEATURE_TOOLS__pub.is_native_control_name': 'public',
                    'FEATURE_TOOLS__pub.rebind_native_selection': 'public',
                    'FEATURE_TOOLS__pub.resolve_native_project': 'public',
                },
            },
        },
    ),
)
```
