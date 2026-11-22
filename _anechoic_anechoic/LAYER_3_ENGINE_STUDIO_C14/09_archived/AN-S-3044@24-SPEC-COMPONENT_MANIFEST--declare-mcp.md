---
atom_family: SPEC
atom_id: AN-S-3044
container:
  component: C14
tier: 0
context:
  template: component_manifest
  lens: SPEC
state:
  status: "archived"
  version: 24
  updated_at: "2026-11-22T09:01:27.697384+00:00"
---

## Summary

Declare MCP

## Purpose

Bridge AI Agents to the Backend Tool API. Map the Backend JSON catalog to
MCP Tools, forward named calls, and return results through MCP.

## Formal manifest

```python
from anechoic.formal_claims import declare_entity
from anechoic.model import ComponentManifest

declare_entity(
    entity_name='Component Manifest',
    instance=ComponentManifest(
        component_id='C21',
        name='MCP',
        lens_whitelist=['DES', 'DevOps', 'QA', 'SWD'],
        boundaries={
            'code': {
                'imports': {'only': [
                    'errors.QueryExecutionError',
                    'errors.WorkbenchUnavailableError',
                    'native_query_runtime.NativeQueryInputs',
                    'native_source_rows__pub.capture_native',
                    'native_manifest_test_support__pub.validate_manifest',
                    'source._parse',
                    'C15', 'C16', 'C62',
                    'import_cache.read_import_sources',
                    'import_tables.publish_imports',
                    'native_service_owner.NativeQueryOwner',
                    'spec_trace._read_pins',
                    'workbench_operations.WorkbenchOperations',
                    'backend_process._release_command',
                    'project_admission.project_tool_policy',
                    'generate_tool_registry.generate',
                    'registry_lifecycle_provider.LIFECYCLE_TOOL_NAMES',
                    'registry_lifecycle_provider.NativeLifecycleProvider',
                    'registry_lifecycle_provider.tool_descriptors',
                    'registry_release_command_provider.RELEASE_COMMAND_TOOLS',
                    'registry_workbench_provider.WorkbenchProvider',
                    'tool_registry_assets.FEATURE_RELATIVE',
                    'tool_registry_assets.ToolRegistryAssetError',
                    'tool_registry_assets.read_inventory',
                    'tool_registry_runtime.ToolInputValidationError',
                    'tool_registry_runtime.ToolOutputValidationError',
                    'tool_registry_runtime.ToolRegistryRuntimeError',
                    'tool_registry_runtime.ToolRegistryStaleError',
                    'tool_registry_runtime.load_active_registry',
                    'workbench_links.public_saved',
                    'workbench_links.public_workspace',
                    'workbench_links.validate_reference',
                    'workbench_tools.CHECK',
                    'workbench_tools.LOAD',
                    'workbench_tools.NATIVE_TOOLS',
                    'workbench_tools.PAGE',
                    'workbench_tools.QUERY_LOG_LIST',
                    'workbench_tools.RUN',
                    'workbench_tools.SAVED_LIST',
                    'workbench_tools.SAVE_VIEW',
                    'workbench_tools.SCHEMA',
                    'workbench_tools.VIEW_CREATE',
                    'workbench_tools.VIEW_DUPLICATE',
                    'workbench_tools.WORKSPACE_OPEN',
                    'workbench_tools.native_tools',
                    'ADAPTERS_C30__pub.CEILINGS',
                    'ADAPTERS_C30__pub.ReadContext',
                    'ADAPTERS_C30__pub.open_regular',
                    'native_carrier_header__pub.canonical_native_header',
                    'work_journal__pub.PROJECT_DATABASE',
                    'work_journal__pub.append_sealed_events',
                    'work_journal__pub.journal_inbox',
                    'smalltest_support__pub.extension_directory',
                    'smalltest_support__pub.polling_source_watcher',
                    'scope_declaration_test_support__pub.write_scope_unit_declarations',
                    'legacy_selection_test_support__pub.select_legacy_project',
                    'model_host_pkg2__pub.reviewed_native_model',
                    'structure_host_pkg3__pub.read_structure',
                ]},
            },
            'io': {
                'server': {
                    'candidate_test_image_build': {
                        'transport': 'cli',
                        'runner': 'uv',
                        'module': 'LAYER_3_ENGINE_STUDIO_C14.MCP_PATCHBAY_C21.FEATURE_MCP.docker.candidate_image_cli',
                        'arguments': ['build', '--project-root', '<project-root>', '--attempt', '<attempt-id>', '--scratch', '<attempt-directory>', '[--packaged-assets]'],
                    },
                    'candidate_test_image_cleanup': {
                        'transport': 'cli',
                        'runner': 'uv',
                        'module': 'LAYER_3_ENGINE_STUDIO_C14.MCP_PATCHBAY_C21.FEATURE_MCP.docker.candidate_image_cli',
                        'arguments': ['cleanup', '--project-root', '<project-root>', '--attempt', '<attempt-id>', '--image', '<image-id>'],
                    },
                    'shared_mcp_launcher': {
                        'transport': 'cli',
                        'runner': 'uv',
                        'path': 'LAYER_3_ENGINE_STUDIO_C14/MCP_PATCHBAY_C21/FEATURE_MCP/docker/shared_mcp_launcher.py',
                    },
                    'shared_runtime_mcp': {
                        'transport': 'http',
                        'path': '/anechoic/mcp',
                        'protocol': 'mcp',
                    },
                },
                'client': [
                    {'component': 'C45', 'interface': 'project_admission'},
                    {'component': 'C45', 'interface': 'tool_api'},
                    {'component': 'C45', 'interface': 'workbench_api'},
                    {'component': 'C45', 'interface': 'previous_image_model_claim_selection'},
                    {'component': 'C50', 'interface': 'image_model_compile'},
                ],
            },
        },
    ),
)
```
