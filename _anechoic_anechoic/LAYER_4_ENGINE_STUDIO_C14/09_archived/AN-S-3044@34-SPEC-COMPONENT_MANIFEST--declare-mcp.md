---
atom_family: SPEC
atom_id: AN-S-3044
container:
  component: C14
tier: 4
context:
  template: component_manifest
  lens: SPEC
state:
  status: "archived"
  version: 34
  updated_at: "2026-11-22T15:04:32.940760+00:00"
relations:
  CONTRIBUTES_TO:
  - AN-S-3329
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
                    'LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/FEATURE_PROJECT_TOOLS/FEATURE_PROJECT_TOOLS__tests',
                    'errors.QueryExecutionError',
                    'errors.WorkbenchUnavailableError',
                    'native_query_runtime.NativeQueryInputs',
                    'native_source_rows__pub.capture_native',
                    'FEATURE_TOOLS__pub.ExplicitBlockingRuntimeFailure',
                    'FEATURE_TOOLS__pub.NativeProjectSelection',
                    'FEATURE_TOOLS__pub.resolve_native_project',
                    'backend_tool_api.tool_failure_result',
                    'import_cache.read_import_sources',
                    'import_tables.publish_imports',
                    'native_service_owner.NativeQueryOwner',
                    'spec_trace._read_pins',
                    'workbench_operations.WorkbenchOperations',
                    'backend_process._release_command',
                    'project_admission.project_tool_policy',
                    'host_runtime_config.HostRuntimeConfig',
                    'host_runtime_config.HostRuntimeConfigError',
                    'host_runtime_config.load_host_runtime_config',
                    'host_runtime_config.resolve_host_project',
                    'project_tool_session.ToolProtocolError',
                    'shared_backend_process',
                    'shared_backend_process.create_app',
                    'shared_project_catalog',
                    'shared_project_catalog.SharedToolFrontier',
                    'shared_project_catalog._candidate_paths',
                    'shared_project_catalog.discover_frontier',
                    'shared_project_catalog.public_tool',
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
                    'ADAPTERS_C30__pub.ReadContext',
                    'native_carrier_header__pub.canonical_native_header',
                    'work_journal__pub.PROJECT_DATABASE',
                    'work_journal__pub.append_sealed_events',
                    'work_journal__pub.journal_inbox',
                    'legacy_selection_test_support__pub.select_legacy_project',
                    'model_host_CS2__shared.reviewed_native_model',
                    'structure_host_CS3__shared.read_structure',
                ]},
            },
            'io': {
                'server': {
                    'candidate_test_image_build': {
                        'transport': 'cli',
                        'runner': 'uv',
                        'module': 'LAYER_4_ENGINE_STUDIO_C14.MCP_PATCHBAY_C21.FEATURE_MCP.docker.candidate_image_cli',
                        'arguments': ['build', '--project-root', '<project-root>', '--attempt', '<attempt-id>', '--scratch', '<attempt-directory>', '[--packaged-assets]'],
                    },
                    'candidate_test_image_cleanup': {
                        'transport': 'cli',
                        'runner': 'uv',
                        'module': 'LAYER_4_ENGINE_STUDIO_C14.MCP_PATCHBAY_C21.FEATURE_MCP.docker.candidate_image_cli',
                        'arguments': ['cleanup', '--project-root', '<project-root>', '--attempt', '<attempt-id>', '--image', '<image-id>'],
                    },
                    'shared_mcp_launcher': {
                        'transport': 'cli',
                        'runner': 'uv',
                        'path': 'LAYER_4_ENGINE_STUDIO_C14/MCP_PATCHBAY_C21/FEATURE_MCP/docker/shared_mcp_launcher.py',
                    },
                    'workbench_http': {
                        'transport': 'http',
                        'routes': {
                            'page': 'GET /anechoic/workbench/{project_name}',
                            'interface': 'POST /anechoic/{project_name}/api/interface',
                            'operation': 'POST /anechoic/{project_name}/api/{action}',
                        },
                    },
                    'shared_runtime_mcp': {
                        'transport': 'http',
                        'path': '/anechoic/mcp',
                        'protocol': 'mcp',
                    },
                },
                'client': [
                    {'component': 'C45', 'interface': 'project_admission'},
                    {'component': 'C53', 'interface': 'project_admission', 'stack': 'beta'},
                    {'component': 'C45', 'interface': 'tool_api'},
                    {'component': 'C45', 'interface': 'shared_tool_coordinator'},
                    {'component': 'C45', 'interface': 'read_host_settings'},
                    {'component': 'C45', 'interface': 'workbench_api'},
                    {'component': 'C30', 'interface': 'guarded_read'},
                    {'component': 'C50', 'interface': 'image_model_stage'},
                ],
            },
            'state': {
                'reads': ['selected Project binding and Manifest', 'validated runtime settings', 'Backend Tool catalog'],
                'writes': ['Project launcher lock and readiness receipts', 'disposable image build context and image ID', 'bounded transport health observations'],
            },
        },
    ),
)
```
