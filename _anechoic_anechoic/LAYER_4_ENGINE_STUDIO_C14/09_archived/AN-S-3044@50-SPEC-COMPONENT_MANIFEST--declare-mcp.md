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
  status: archived
  version: 50
  updated_at: '2026-11-23T04:47:55.654512+00:00'
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
                    'FEATURE_WORKBENCH_BACKEND__shared.CHECK',
                    'FEATURE_WORKBENCH_BACKEND__shared.LOAD',
                    'FEATURE_WORKBENCH_BACKEND__shared.NATIVE_TOOLS',
                    'FEATURE_WORKBENCH_BACKEND__shared.PAGE',
                    'FEATURE_WORKBENCH_BACKEND__shared.QUERY_LOG_LIST',
                    'FEATURE_WORKBENCH_BACKEND__shared.RUN',
                    'FEATURE_WORKBENCH_BACKEND__shared.SAVED_LIST',
                    'FEATURE_WORKBENCH_BACKEND__shared.SAVE_VIEW',
                    'FEATURE_WORKBENCH_BACKEND__shared.SCHEMA',
                    'FEATURE_WORKBENCH_BACKEND__shared.SharedToolFrontier',
                    'FEATURE_WORKBENCH_BACKEND__shared.ToolInputValidationError',
                    'FEATURE_WORKBENCH_BACKEND__shared.ToolOutputValidationError',
                    'FEATURE_WORKBENCH_BACKEND__shared.ToolRegistryRuntimeError',
                    'FEATURE_WORKBENCH_BACKEND__shared.ToolRegistryStaleError',
                    'FEATURE_WORKBENCH_BACKEND__shared.VIEW_CREATE',
                    'FEATURE_WORKBENCH_BACKEND__shared.VIEW_DUPLICATE',
                    'FEATURE_WORKBENCH_BACKEND__shared.WORKSPACE_OPEN',
                    'FEATURE_WORKBENCH_BACKEND__shared._candidate_paths',
                    'FEATURE_WORKBENCH_BACKEND__shared.discover_frontier',
                    'FEATURE_WORKBENCH_BACKEND__shared.load_active_registry',
                    'FEATURE_WORKBENCH_BACKEND__shared.native_tools',
                    'FEATURE_WORKBENCH_BACKEND__shared.public_tool',
                    'FEATURE_WORKBENCH_BACKEND__shared.shared_project_catalog',
                    'docker.docker__shared',
                    'docker.docker__shared.ImageManager',
                    'docker.docker__shared.ImageError',
                    'docker.docker__shared.TOOL_REGISTRY',
                    'docker.docker__shared.FINGERPRINT_LABEL',
                    'docker.docker__shared.OCI_VERSION_LABEL',
                    'docker.docker__shared.SCHEMA_LABEL',
                    'docker.docker__shared.DOCKER_ROOT',
                    'docker.docker__shared.DOCKERFILE',
                    'docker.docker__shared.DOCKERIGNORE',
                    'docker.docker__shared.ENGINE_ROOT',
                    'docker.docker__shared.IMAGE',
                    'docker.docker__shared.ImageBuildProvenance',
                    'docker.docker__shared.LICENSE_INPUTS',
                    'docker.docker__shared.RETIRED_ASSETS',
                    'docker.docker__shared._REQUIRED',
                    'docker.docker__shared.ready_predecessor',
                    'docker.docker__shared.TOOL_REGISTRY_COMPILER',
                    'docker.docker__shared.TOOL_PROVIDERS',
                    'docker.docker__shared.compile_tool_registry',
                    'FEATURE_MCP.FEATURE_MCP__shared.HEALTH_PATH',
                    'FEATURE_MCP.FEATURE_MCP__shared.MCP_PATH',
                    'FEATURE_MCP.FEATURE_MCP__shared.WORKBENCH_PATH',
                    'FEATURE_MCP.FEATURE_MCP__shared.ExplicitStartupFailure',
                    'FEATURE_MCP.FEATURE_MCP__shared.beta_runtime_arguments',
                    'FEATURE_MCP.FEATURE_MCP__shared.select_runtime_project',
                    'FEATURE_MCP.FEATURE_MCP__shared.ProjectBinding',
                    'FEATURE_MCP.FEATURE_MCP__shared.ProjectAdmissionError',
                    'FEATURE_MCP.FEATURE_MCP__shared.project_admission',
                    'KERNEL_MIXER_C59__shared.QueryExecutionError',
                    'KERNEL_MIXER_C59__shared.WorkbenchUnavailableError',
                    'LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/FEATURE_PROJECT_TOOLS/FEATURE_PROJECT_TOOLS__tests',
                    'errors.QueryExecutionError',
                    'errors.WorkbenchUnavailableError',
                    'KERNEL_MIXER_C59__shared.NativeQueryInputs',
                    'ADAPTERS_C30__shared.capture_native',
                    'FEATURE_TOOLS__shared.ExplicitBlockingRuntimeFailure',
                    'FEATURE_TOOLS__shared.NativeProjectSelection',
                    'FEATURE_TOOLS__shared.resolve_native_project',
                    'backend_tool_api.tool_failure_result',
                    'KERNEL_MIXER_C59__shared.read_import_sources',
                    'KERNEL_MIXER_C59__shared.publish_imports',
                    'KERNEL_MIXER_C59__shared.NativeQueryOwner',
                    'trace_bindings__shared._read_pins',
                    'workbench_operations.WorkbenchOperations',
                    'backend_process._release_command',
                    'project_admission.project_tool_policy',
                    'FEATURE_WORKBENCH_BACKEND__shared.HostRuntimeConfig',
                    'FEATURE_WORKBENCH_BACKEND__shared.HostRuntimeConfigError',
                    'FEATURE_WORKBENCH_BACKEND__shared.load_host_runtime_config',
                    'FEATURE_WORKBENCH_BACKEND__shared.resolve_host_project',
                    'project_tool_session.ToolProtocolError',
                    'shared_backend_process',
                    'shared_backend_process.create_app',
                    'generate_tool_registry.generate',
                    'registry_lifecycle_provider.LIFECYCLE_TOOL_NAMES',
                    'registry_lifecycle_provider.NativeLifecycleProvider',
                    'registry_lifecycle_provider.tool_descriptors',
                    'registry_release_command_provider.RELEASE_COMMAND_TOOLS',
                    'registry_workbench_provider.WorkbenchProvider',
                    'tool_registry_assets.FEATURE_RELATIVE',
                    'tool_registry_assets.ToolRegistryAssetError',
                    'tool_registry_assets.read_inventory',
                    'workbench_links.public_saved',
                    'workbench_links.public_workspace',
                    'workbench_links.validate_reference',
                    'ADAPTERS_C30__shared.ReadContext',
                    'ADAPTERS_C30__shared.canonical_native_header',
                    'work_journal__pub.PROJECT_DATABASE',
                    'work_journal__pub.append_sealed_events',
                    'work_journal__pub.journal_inbox',
                    'FEATURE_TOOLS__tests__shared.select_legacy_project',
                    'model_host_CS2__shared.reviewed_native_model',
                ]},
                'exports': {
                    'FEATURE_MCP.FEATURE_MCP__shared.ExplicitStartupFailure': {'private': ['LAYER_4_ENGINE_STUDIO_C14/MCP_PATCHBAY_C21/FEATURE_MCP/docker']},
                    'FEATURE_MCP.FEATURE_MCP__shared.beta_runtime_arguments': {'private': ['LAYER_4_ENGINE_STUDIO_C14/MCP_PATCHBAY_C21/FEATURE_MCP/docker']},
                    'FEATURE_MCP.FEATURE_MCP__shared.select_runtime_project': {'private': ['LAYER_4_ENGINE_STUDIO_C14/MCP_PATCHBAY_C21/FEATURE_MCP/docker', 'LAYER_4_ENGINE_STUDIO_C14/MCP_PATCHBAY_C21/FEATURE_MCP/FEATURE_MCP__tests']},
                    'FEATURE_MCP.FEATURE_MCP__shared.ProjectBinding': {'private': ['LAYER_4_ENGINE_STUDIO_C14/MCP_PATCHBAY_C21/FEATURE_MCP/docker', 'LAYER_4_ENGINE_STUDIO_C14/MCP_PATCHBAY_C21/FEATURE_MCP/FEATURE_MCP__tests']},
                    'FEATURE_MCP.FEATURE_MCP__shared.ProjectAdmissionError': {'private': ['LAYER_4_ENGINE_STUDIO_C14/MCP_PATCHBAY_C21/FEATURE_MCP/FEATURE_MCP__tests']},
                    'FEATURE_MCP.FEATURE_MCP__shared.project_admission': {'private': ['LAYER_4_ENGINE_STUDIO_C14/MCP_PATCHBAY_C21/FEATURE_MCP/FEATURE_MCP__tests']},
                    'docker.docker__shared': {'private': ['LAYER_4_ENGINE_STUDIO_C14/MCP_PATCHBAY_C21/FEATURE_MCP/FEATURE_MCP__tests']},
                    'docker.docker__shared.ImageManager': {'private': ['LAYER_4_ENGINE_STUDIO_C14/MCP_PATCHBAY_C21/FEATURE_MCP/FEATURE_MCP__tests']},
                    'docker.docker__shared.ImageError': {'private': ['LAYER_4_ENGINE_STUDIO_C14/MCP_PATCHBAY_C21/FEATURE_MCP/FEATURE_MCP__tests']},
                    'docker.docker__shared.TOOL_REGISTRY': {'private': ['LAYER_4_ENGINE_STUDIO_C14/MCP_PATCHBAY_C21/FEATURE_MCP/FEATURE_MCP__tests']},
                    'docker.docker__shared.FINGERPRINT_LABEL': {'private': ['LAYER_4_ENGINE_STUDIO_C14/MCP_PATCHBAY_C21/FEATURE_MCP/FEATURE_MCP__tests']},
                    'docker.docker__shared.OCI_VERSION_LABEL': {'private': ['LAYER_4_ENGINE_STUDIO_C14/MCP_PATCHBAY_C21/FEATURE_MCP/FEATURE_MCP__tests']},
                    'docker.docker__shared.SCHEMA_LABEL': {'private': ['LAYER_4_ENGINE_STUDIO_C14/MCP_PATCHBAY_C21/FEATURE_MCP/FEATURE_MCP__tests']},
                    'docker.docker__shared.DOCKER_ROOT': {'private': ['LAYER_4_ENGINE_STUDIO_C14/MCP_PATCHBAY_C21/FEATURE_MCP/FEATURE_MCP__tests']},
                    'docker.docker__shared.DOCKERFILE': {'private': ['LAYER_4_ENGINE_STUDIO_C14/MCP_PATCHBAY_C21/FEATURE_MCP/FEATURE_MCP__tests']},
                    'docker.docker__shared.DOCKERIGNORE': {'private': ['LAYER_4_ENGINE_STUDIO_C14/MCP_PATCHBAY_C21/FEATURE_MCP/FEATURE_MCP__tests']},
                    'docker.docker__shared.ENGINE_ROOT': {'private': ['LAYER_4_ENGINE_STUDIO_C14/MCP_PATCHBAY_C21/FEATURE_MCP/FEATURE_MCP__tests']},
                    'docker.docker__shared.IMAGE': {'private': ['LAYER_4_ENGINE_STUDIO_C14/MCP_PATCHBAY_C21/FEATURE_MCP/FEATURE_MCP__tests']},
                    'docker.docker__shared.ImageBuildProvenance': {'private': ['LAYER_4_ENGINE_STUDIO_C14/MCP_PATCHBAY_C21/FEATURE_MCP/FEATURE_MCP__tests']},
                    'docker.docker__shared.LICENSE_INPUTS': {'private': ['LAYER_4_ENGINE_STUDIO_C14/MCP_PATCHBAY_C21/FEATURE_MCP/FEATURE_MCP__tests']},
                    'docker.docker__shared.RETIRED_ASSETS': {'private': ['LAYER_4_ENGINE_STUDIO_C14/MCP_PATCHBAY_C21/FEATURE_MCP/FEATURE_MCP__tests']},
                    'docker.docker__shared._REQUIRED': {'private': ['LAYER_4_ENGINE_STUDIO_C14/MCP_PATCHBAY_C21/FEATURE_MCP/FEATURE_MCP__tests']},
                    'docker.docker__shared.ready_predecessor': {'private': ['LAYER_4_ENGINE_STUDIO_C14/MCP_PATCHBAY_C21/FEATURE_MCP/FEATURE_MCP__tests']},
                    'docker.docker__shared.TOOL_REGISTRY_COMPILER': {'private': ['LAYER_4_ENGINE_STUDIO_C14/MCP_PATCHBAY_C21/FEATURE_MCP/FEATURE_MCP__tests']},
                    'docker.docker__shared.TOOL_PROVIDERS': {'private': ['LAYER_4_ENGINE_STUDIO_C14/MCP_PATCHBAY_C21/FEATURE_MCP/FEATURE_MCP__tests']},
                    'docker.docker__shared.compile_tool_registry': {'private': ['LAYER_4_ENGINE_STUDIO_C14/MCP_PATCHBAY_C21/FEATURE_MCP/FEATURE_MCP__tests']},
                    'FEATURE_MCP.FEATURE_MCP__shared.HEALTH_PATH': {'private': ['LAYER_4_ENGINE_STUDIO_C14/MCP_PATCHBAY_C21/FEATURE_MCP/FEATURE_MCP__tests', 'LAYER_4_ENGINE_STUDIO_C14/MCP_PATCHBAY_C21/FEATURE_MCP/FEATURE_MCP__tests/image', 'LAYER_4_ENGINE_STUDIO_C14/MCP_PATCHBAY_C21/FEATURE_MCP/docker']},
                    'FEATURE_MCP.FEATURE_MCP__shared.MCP_PATH': {'private': ['LAYER_4_ENGINE_STUDIO_C14/MCP_PATCHBAY_C21/FEATURE_MCP/FEATURE_MCP__tests', 'LAYER_4_ENGINE_STUDIO_C14/MCP_PATCHBAY_C21/FEATURE_MCP/docker']},
                    'FEATURE_MCP.FEATURE_MCP__shared.WORKBENCH_PATH': {'private': ['LAYER_4_ENGINE_STUDIO_C14/MCP_PATCHBAY_C21/FEATURE_MCP/FEATURE_MCP__tests', 'LAYER_4_ENGINE_STUDIO_C14/MCP_PATCHBAY_C21/FEATURE_MCP/FEATURE_MCP__tests/image']},
                },
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
                    'project_mcp': {
                        'transport': 'cli',
                        'runner': 'managed_python',
                        'module': 'MCP_PATCHBAY_C21.FEATURE_MCP.server',
                        'arguments': ['--project-root', '<project-root>'],
                        'optional_arguments': ['--control-root', '<selected-control-root>',
                                               '--instance-id', '<project-instance>',
                                               '--host-project-root', '<host-project-root>',
                                               '--transport', '<stdio-or-streamable-http>'],
                        'streamable_http_path': '/anechoic/mcp',
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
                    {'component': 'C70', 'interface': 'shared_workbench_api', 'stack': 'beta'},
                    {'component': 'C70', 'interface': 'workbench_api', 'stack': 'beta'},
                    {'component': 'C70', 'interface': 'shared_peer_owner', 'stack': 'beta',
                     'caller': 'packaged shared runtime supervisor'},
                    {'component': 'C30', 'interface': 'guarded_read'},
                    {'component': 'C50', 'interface': 'image_model_stage'},
                ],
            },
            'state': {
                'reads': ['selected Project binding and Manifest', 'validated runtime settings', 'Backend Tool catalog'],
                'writes': ['Project launcher lock and readiness receipts', 'disposable image build context and image ID', 'bounded transport health observations',
                           'parent pipes for packaged Beta peer owners and API processes'],
            },
        },
    ),
)
```
