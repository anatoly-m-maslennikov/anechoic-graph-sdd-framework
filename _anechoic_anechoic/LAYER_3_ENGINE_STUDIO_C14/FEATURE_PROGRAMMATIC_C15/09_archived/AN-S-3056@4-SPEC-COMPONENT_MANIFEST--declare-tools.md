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
  version: 4
  updated_at: "2026-11-22T01:27:40.490953+00:00"
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
                'imports': [
                    'import_graph__shared.capture',
                    'import_graph__shared.code_access_occurrences',
                    'FEATURE_MODEL_VALIDATION__shared.build_code_access_ownership',
                    'FEATURE_MODEL_VALIDATION__shared.check_code_access',
                ],
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
                    'FEATURE_TOOLS__pub.mcp_tool_blacklist': 'public',
                    'FEATURE_TOOLS__pub.rebind_native_selection': 'public',
                    'FEATURE_TOOLS__pub.resolve_native_project': 'public',
                },
            },
        },
    ),
)
```
