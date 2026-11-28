---
atom_family: SPEC
atom_id: AN-S-3044
container:
  component: C14
tier: 1
context:
  template: component_manifest
  lens: SPEC
state:
  status: "archived"
  version: 73
  updated_at: "2026-11-28T08:28:50.799564+00:00"
relations:
  CONTRIBUTES_TO:
  - AN-S-3329
---

## Summary

Declare MCP

## Purpose

Bridge AI Agents to the Backend Tool API. Map the Backend JSON catalog to
MCP Tools, forward named calls, and return results through MCP.

## Component Identity

```python
from anechoic.model import ComponentManifest

ComponentManifest(
    component_id='C21',
    name='MCP',
    lens_whitelist=['DES', 'DevOps', 'QA', 'SWD'],
)
```

## Component Boundaries

```python
{'code': {'imports': {'only': ['FEATURE_MCP.FEATURE_MCP__shared.http_main',
                               'FEATURE_MCP.FEATURE_MCP__shared.server_main',
                               'container_settings__pub.CONTAINER_SETTINGS_FILENAME',
                               'container_settings__pub.parse_container_settings',
                               'container_settings__pub.read_container_settings',
                               'settings_carrier__pub.read_settings_carrier',
                               'docker.docker__shared.Launcher',
                               'docker.docker__shared.ProjectMcpBackend',
                               'docker.docker__shared.Runtime',
                               'docker.docker__shared.runtime_main',
                               'docker.docker__shared.SharedMcpLauncher',
                               'docker.docker__shared.shared_mcp_main',
                               'docker.docker__shared.candidate_image_main',
                               'FEATURE_MCP.FEATURE_MCP__shared.BackendClient',
                               'FEATURE_MCP.FEATURE_MCP__shared.DirectGateway',
                               'FEATURE_MCP.FEATURE_MCP__shared.native_project_gateway',
                               'FEATURE_MCP.FEATURE_MCP__shared.native_runtime_gateway',
                               'FEATURE_MCP.FEATURE_MCP__shared.SharedBackendGateway',
                               'FEATURE_MCP.FEATURE_MCP__shared.SharedGatewayRefusal',
                               'FEATURE_MCP.FEATURE_MCP__shared.create_http_app',
                               'FEATURE_MCP.FEATURE_MCP__shared.create_shared_http_app',
                               'FEATURE_MCP.FEATURE_MCP__shared.workbench_routes',
                               'docker.docker__shared.LaunchError',
                               'FEATURE_MCP.FEATURE_MCP__shared.runtime_stack',
                               'FEATURE_MCP.FEATURE_MCP__shared.native_arguments',
                               'FEATURE_MCP.FEATURE_MCP__shared.HealthObservations',
                               'FEATURE_MCP.FEATURE_MCP__shared.render_health_page',
                               'docker.docker__shared.BackendError',
                               'FEATURE_MCP.FEATURE_MCP__shared.ToolProtocolError',
                               'FEATURE_MCP.FEATURE_MCP__shared.RuntimeRequestContext',
                               'FEATURE_MCP.FEATURE_MCP__shared.bind_request_context',
                               'FEATURE_MCP.FEATURE_MCP__shared.current_request_context',
                               'FEATURE_MCP.FEATURE_MCP__tests.native_import_graph_docker_cases',
                               'FEATURE_MCP.FEATURE_MCP__tests.native_shared_candidate_cases.SharedCandidateCases',
                               'FEATURE_MCP.FEATURE_MCP__tests.FEATURE_MCP__tests__shared.CONTROL',
                               'FEATURE_MCP.FEATURE_MCP__tests.FEATURE_MCP__tests__shared.project',
                               'FEATURE_MCP.FEATURE_MCP__tests.FEATURE_MCP__tests__shared.defer_container_cleanup',
                               'FEATURE_MCP.FEATURE_MCP__tests.FEATURE_MCP__tests__shared.docker_deadline_env',
                               'FEATURE_MCP.FEATURE_MCP__tests.FEATURE_MCP__tests__shared.image_mcp_transport',
                               'FEATURE_MCP.FEATURE_MCP__tests.FEATURE_MCP__tests__shared.image_timeout',
                               'FEATURE_MCP.FEATURE_MCP__tests.FEATURE_MCP__tests__shared.observing',
                               'FEATURE_MCP.FEATURE_MCP__tests.FEATURE_MCP__tests__shared.request',
                               'FEATURE_MCP.FEATURE_MCP__tests.FEATURE_MCP__tests__shared.write_manifest',
                               'FEATURE_MCP.FEATURE_MCP__tests.FEATURE_MCP__tests__shared.run_workbench_browser',
                               'FEATURE_MCP.FEATURE_MCP__tests.image.image__shared.PackagedProbe',
                               'FEATURE_MCP.FEATURE_MCP__tests.image.image__shared.cgroup_resources',
                               'FEATURE_MCP.FEATURE_MCP__tests.image.image__shared.cold_throughput',
                               'FEATURE_MCP.FEATURE_MCP__tests.image.image__shared.started_at_ns',
                               'FEATURE_MCP.FEATURE_MCP__tests.image.image__shared.startup_events',
                               'FEATURE_MCP.FEATURE_MCP__tests.image.image__shared.startup_outcome',
                               'FEATURE_MCP.FEATURE_MCP__tests.image.image__shared.timing_summary',
                               'FEATURE_MCP.FEATURE_MCP__tests.image.image__shared.staged_startup',
                               'FEATURE_MCP.FEATURE_MCP__tests.image.image__shared.generation_load',
                               'FEATURE_IWE_CONSOLE_BACKEND__shared.CHECK',
                               'FEATURE_IWE_CONSOLE_BACKEND__shared.LOAD',
                               'FEATURE_IWE_CONSOLE_BACKEND__shared.NATIVE_TOOLS',
                               'FEATURE_IWE_CONSOLE_BACKEND__shared.PAGE',
                               'FEATURE_IWE_CONSOLE_BACKEND__shared.QUERY_LOG_LIST',
                               'FEATURE_IWE_CONSOLE_BACKEND__shared.RUN',
                               'FEATURE_IWE_CONSOLE_BACKEND__shared.SAVED_LIST',
                               'FEATURE_IWE_CONSOLE_BACKEND__shared.SAVE_VIEW',
                               'FEATURE_IWE_CONSOLE_BACKEND__shared.SCHEMA',
                               'FEATURE_IWE_CONSOLE_BACKEND__shared.SharedToolFrontier',
                               'FEATURE_IWE_CONSOLE_BACKEND__shared.ToolInputValidationError',
                               'FEATURE_IWE_CONSOLE_BACKEND__shared.ToolOutputValidationError',
                               'FEATURE_IWE_CONSOLE_BACKEND__shared.ToolRegistryRuntimeError',
                               'FEATURE_IWE_CONSOLE_BACKEND__shared.ToolRegistryStaleError',
                               'FEATURE_IWE_CONSOLE_BACKEND__shared.VIEW_CREATE',
                               'FEATURE_IWE_CONSOLE_BACKEND__shared.VIEW_DUPLICATE',
                               'FEATURE_IWE_CONSOLE_BACKEND__shared.WORKSPACE_OPEN',
                               'FEATURE_IWE_CONSOLE_BACKEND__shared._candidate_paths',
                               'FEATURE_IWE_CONSOLE_BACKEND__shared.discover_frontier',
                               'FEATURE_IWE_CONSOLE_BACKEND__shared.load_active_registry',
                               'FEATURE_IWE_CONSOLE_BACKEND__shared.native_tools',
                               'FEATURE_IWE_CONSOLE_BACKEND__shared.public_tool',
                               'FEATURE_IWE_CONSOLE_BACKEND__shared.shared_project_catalog',
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
                               'import_graph__shared._read_pins',
                               'workbench_operations.WorkbenchOperations',
                               'backend_process._release_command',
                               'project_admission.project_tool_policy',
                               'FEATURE_IWE_CONSOLE_BACKEND__shared.HostRuntimeConfig',
                               'FEATURE_IWE_CONSOLE_BACKEND__shared.HostRuntimeConfigError',
                               'FEATURE_IWE_CONSOLE_BACKEND__shared.load_host_runtime_config',
                               'FEATURE_IWE_CONSOLE_BACKEND__shared.resolve_host_project',
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
                               'model_host_CS2__shared.reviewed_native_model']},
          'exports': {'FEATURE_MCP.FEATURE_MCP__shared.http_main': {'private': ['LAYER_4_ENGINE_STUDIO_C14/MCP_PATCHBAY_C21/FEATURE_MCP/FEATURE_MCP__tests']},
                      'FEATURE_MCP.FEATURE_MCP__shared.server_main': {'private': ['LAYER_4_ENGINE_STUDIO_C14/MCP_PATCHBAY_C21/FEATURE_MCP/FEATURE_MCP__tests']},
                      'docker.docker__shared.Launcher': {'private': ['LAYER_4_ENGINE_STUDIO_C14/MCP_PATCHBAY_C21/FEATURE_MCP/FEATURE_MCP__tests']},
                      'docker.docker__shared.ProjectMcpBackend': {'private': ['LAYER_4_ENGINE_STUDIO_C14/MCP_PATCHBAY_C21/FEATURE_MCP/FEATURE_MCP__tests']},
                      'docker.docker__shared.Runtime': {'private': ['LAYER_4_ENGINE_STUDIO_C14/MCP_PATCHBAY_C21/FEATURE_MCP/FEATURE_MCP__tests']},
                      'docker.docker__shared.runtime_main': {'private': ['LAYER_4_ENGINE_STUDIO_C14/MCP_PATCHBAY_C21/FEATURE_MCP/FEATURE_MCP__tests']},
                      'docker.docker__shared.SharedMcpLauncher': {'private': ['LAYER_4_ENGINE_STUDIO_C14/MCP_PATCHBAY_C21/FEATURE_MCP/FEATURE_MCP__tests']},
                      'docker.docker__shared.shared_mcp_main': {'private': ['LAYER_4_ENGINE_STUDIO_C14/MCP_PATCHBAY_C21/FEATURE_MCP/FEATURE_MCP__tests']},
                      'docker.docker__shared.candidate_image_main': {'private': ['LAYER_4_ENGINE_STUDIO_C14/MCP_PATCHBAY_C21/FEATURE_MCP/FEATURE_MCP__tests']},
                      'FEATURE_MCP.FEATURE_MCP__shared.BackendClient': {'private': ['LAYER_4_ENGINE_STUDIO_C14/MCP_PATCHBAY_C21/FEATURE_MCP/FEATURE_MCP__tests']},
                      'FEATURE_MCP.FEATURE_MCP__shared.DirectGateway': {'private': ['LAYER_4_ENGINE_STUDIO_C14/MCP_PATCHBAY_C21/FEATURE_MCP/FEATURE_MCP__tests']},
                      'FEATURE_MCP.FEATURE_MCP__shared.native_project_gateway': {'private': ['LAYER_4_ENGINE_STUDIO_C14/MCP_PATCHBAY_C21/FEATURE_MCP/FEATURE_MCP__tests']},
                      'FEATURE_MCP.FEATURE_MCP__shared.native_runtime_gateway': {'private': ['LAYER_4_ENGINE_STUDIO_C14/MCP_PATCHBAY_C21/FEATURE_MCP/FEATURE_MCP__tests']},
                      'FEATURE_MCP.FEATURE_MCP__shared.SharedBackendGateway': {'private': ['LAYER_4_ENGINE_STUDIO_C14/MCP_PATCHBAY_C21/FEATURE_MCP/FEATURE_MCP__tests']},
                      'FEATURE_MCP.FEATURE_MCP__shared.SharedGatewayRefusal': {'private': ['LAYER_4_ENGINE_STUDIO_C14/MCP_PATCHBAY_C21/FEATURE_MCP/FEATURE_MCP__tests']},
                      'FEATURE_MCP.FEATURE_MCP__shared.create_http_app': {'private': ['LAYER_4_ENGINE_STUDIO_C14/MCP_PATCHBAY_C21/FEATURE_MCP/FEATURE_MCP__tests']},
                      'FEATURE_MCP.FEATURE_MCP__shared.create_shared_http_app': {'private': ['LAYER_4_ENGINE_STUDIO_C14/MCP_PATCHBAY_C21/FEATURE_MCP/FEATURE_MCP__tests']},
                      'FEATURE_MCP.FEATURE_MCP__shared.workbench_routes': {'private': ['LAYER_4_ENGINE_STUDIO_C14/MCP_PATCHBAY_C21/FEATURE_MCP/FEATURE_MCP__tests']},
                      'docker.docker__shared.LaunchError': {'private': ['LAYER_4_ENGINE_STUDIO_C14/MCP_PATCHBAY_C21/FEATURE_MCP/FEATURE_MCP__tests']},
                      'FEATURE_MCP.FEATURE_MCP__shared.runtime_stack': {'private': ['LAYER_4_ENGINE_STUDIO_C14/MCP_PATCHBAY_C21/FEATURE_MCP/FEATURE_MCP__tests']},
                      'FEATURE_MCP.FEATURE_MCP__shared.native_arguments': {'private': ['LAYER_4_ENGINE_STUDIO_C14/MCP_PATCHBAY_C21/FEATURE_MCP/FEATURE_MCP__tests']},
                      'FEATURE_MCP.FEATURE_MCP__shared.HealthObservations': {'private': ['LAYER_4_ENGINE_STUDIO_C14/MCP_PATCHBAY_C21/FEATURE_MCP/FEATURE_MCP__tests']},
                      'FEATURE_MCP.FEATURE_MCP__shared.render_health_page': {'private': ['LAYER_4_ENGINE_STUDIO_C14/MCP_PATCHBAY_C21/FEATURE_MCP/FEATURE_MCP__tests']},
                      'docker.docker__shared.BackendError': {'private': ['LAYER_4_ENGINE_STUDIO_C14/MCP_PATCHBAY_C21/FEATURE_MCP/FEATURE_MCP__tests']},
                      'FEATURE_MCP.FEATURE_MCP__shared.ToolProtocolError': {'private': ['LAYER_4_ENGINE_STUDIO_C14/MCP_PATCHBAY_C21/FEATURE_MCP/FEATURE_MCP__tests']},
                      'FEATURE_MCP.FEATURE_MCP__shared.RuntimeRequestContext': {'private': ['LAYER_4_ENGINE_STUDIO_C14/MCP_PATCHBAY_C21/FEATURE_MCP/FEATURE_MCP__tests']},
                      'FEATURE_MCP.FEATURE_MCP__shared.bind_request_context': {'private': ['LAYER_4_ENGINE_STUDIO_C14/MCP_PATCHBAY_C21/FEATURE_MCP/FEATURE_MCP__tests']},
                      'FEATURE_MCP.FEATURE_MCP__shared.current_request_context': {'private': ['LAYER_4_ENGINE_STUDIO_C14/MCP_PATCHBAY_C21/FEATURE_MCP/FEATURE_MCP__tests']},
                      'FEATURE_MCP.FEATURE_MCP__tests.native_import_graph_docker_cases': {'private': ['LAYER_4_ENGINE_STUDIO_C14/MCP_PATCHBAY_C21/FEATURE_MCP/FEATURE_MCP__tests/image']},
                      'FEATURE_MCP.FEATURE_MCP__tests.native_shared_candidate_cases.SharedCandidateCases': {'private': ['LAYER_4_ENGINE_STUDIO_C14/MCP_PATCHBAY_C21/FEATURE_MCP/FEATURE_MCP__tests/image']},
                      'FEATURE_MCP.FEATURE_MCP__tests.FEATURE_MCP__tests__shared.CONTROL': {'private': ['LAYER_4_ENGINE_STUDIO_C14/MCP_PATCHBAY_C21/FEATURE_MCP/FEATURE_MCP__tests/image']},
                      'FEATURE_MCP.FEATURE_MCP__tests.FEATURE_MCP__tests__shared.project': {'private': ['LAYER_4_ENGINE_STUDIO_C14/MCP_PATCHBAY_C21/FEATURE_MCP/FEATURE_MCP__tests/image']},
                      'FEATURE_MCP.FEATURE_MCP__tests.FEATURE_MCP__tests__shared.defer_container_cleanup': {'private': ['LAYER_4_ENGINE_STUDIO_C14/MCP_PATCHBAY_C21/FEATURE_MCP/FEATURE_MCP__tests/image']},
                      'FEATURE_MCP.FEATURE_MCP__tests.FEATURE_MCP__tests__shared.docker_deadline_env': {'private': ['LAYER_4_ENGINE_STUDIO_C14/MCP_PATCHBAY_C21/FEATURE_MCP/FEATURE_MCP__tests/image']},
                      'FEATURE_MCP.FEATURE_MCP__tests.FEATURE_MCP__tests__shared.image_mcp_transport': {'private': ['LAYER_4_ENGINE_STUDIO_C14/MCP_PATCHBAY_C21/FEATURE_MCP/FEATURE_MCP__tests/image']},
                      'FEATURE_MCP.FEATURE_MCP__tests.FEATURE_MCP__tests__shared.image_timeout': {'private': ['LAYER_4_ENGINE_STUDIO_C14/MCP_PATCHBAY_C21/FEATURE_MCP/FEATURE_MCP__tests/image']},
                      'FEATURE_MCP.FEATURE_MCP__tests.FEATURE_MCP__tests__shared.observing': {'private': ['LAYER_4_ENGINE_STUDIO_C14/MCP_PATCHBAY_C21/FEATURE_MCP/FEATURE_MCP__tests/image']},
                      'FEATURE_MCP.FEATURE_MCP__tests.FEATURE_MCP__tests__shared.request': {'private': ['LAYER_4_ENGINE_STUDIO_C14/MCP_PATCHBAY_C21/FEATURE_MCP/FEATURE_MCP__tests/image']},
                      'FEATURE_MCP.FEATURE_MCP__tests.FEATURE_MCP__tests__shared.write_manifest': {'private': ['LAYER_4_ENGINE_STUDIO_C14/MCP_PATCHBAY_C21/FEATURE_MCP/FEATURE_MCP__tests/image']},
                      'FEATURE_MCP.FEATURE_MCP__tests.FEATURE_MCP__tests__shared.run_workbench_browser': {'private': ['LAYER_4_ENGINE_STUDIO_C14/MCP_PATCHBAY_C21/FEATURE_MCP/FEATURE_MCP__tests/image']},
                      'FEATURE_MCP.FEATURE_MCP__tests.image.image__shared.PackagedProbe': {'private': ['parent']},
                      'FEATURE_MCP.FEATURE_MCP__tests.image.image__shared.cgroup_resources': {'private': ['parent']},
                      'FEATURE_MCP.FEATURE_MCP__tests.image.image__shared.cold_throughput': {'private': ['parent']},
                      'FEATURE_MCP.FEATURE_MCP__tests.image.image__shared.started_at_ns': {'private': ['parent']},
                      'FEATURE_MCP.FEATURE_MCP__tests.image.image__shared.startup_events': {'private': ['parent']},
                      'FEATURE_MCP.FEATURE_MCP__tests.image.image__shared.startup_outcome': {'private': ['parent']},
                      'FEATURE_MCP.FEATURE_MCP__tests.image.image__shared.timing_summary': {'private': ['parent']},
                      'FEATURE_MCP.FEATURE_MCP__tests.image.image__shared.staged_startup': {'private': ['parent']},
                      'FEATURE_MCP.FEATURE_MCP__tests.image.image__shared.generation_load': {'private': ['parent']},
                      'FEATURE_MCP.FEATURE_MCP__tests.FEATURE_MCP__tests__shared.packaged_identity_reader': {'shared': ['LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/FEATURE_PROJECT_TOOLS/FEATURE_PROJECT_TOOLS__tests']},
                      'FEATURE_MCP.FEATURE_MCP__shared.ExplicitStartupFailure': {'private': ['LAYER_4_ENGINE_STUDIO_C14/MCP_PATCHBAY_C21/FEATURE_MCP/docker',
                                                                                             'LAYER_4_ENGINE_STUDIO_C14/MCP_PATCHBAY_C21/FEATURE_MCP/FEATURE_MCP__tests']},
                      'FEATURE_MCP.FEATURE_MCP__shared.select_runtime_project': {'private': ['LAYER_4_ENGINE_STUDIO_C14/MCP_PATCHBAY_C21/FEATURE_MCP/docker',
                                                                                             'LAYER_4_ENGINE_STUDIO_C14/MCP_PATCHBAY_C21/FEATURE_MCP/FEATURE_MCP__tests']},
                      'FEATURE_MCP.FEATURE_MCP__shared.ProjectBinding': {'private': ['LAYER_4_ENGINE_STUDIO_C14/MCP_PATCHBAY_C21/FEATURE_MCP/docker',
                                                                                     'LAYER_4_ENGINE_STUDIO_C14/MCP_PATCHBAY_C21/FEATURE_MCP/FEATURE_MCP__tests']},
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
                      'FEATURE_MCP.FEATURE_MCP__shared.HEALTH_PATH': {'private': ['LAYER_4_ENGINE_STUDIO_C14/MCP_PATCHBAY_C21/FEATURE_MCP/FEATURE_MCP__tests',
                                                                                  'LAYER_4_ENGINE_STUDIO_C14/MCP_PATCHBAY_C21/FEATURE_MCP/FEATURE_MCP__tests/image',
                                                                                  'LAYER_4_ENGINE_STUDIO_C14/MCP_PATCHBAY_C21/FEATURE_MCP/docker']},
                      'FEATURE_MCP.FEATURE_MCP__shared.MCP_PATH': {'private': ['LAYER_4_ENGINE_STUDIO_C14/MCP_PATCHBAY_C21/FEATURE_MCP/FEATURE_MCP__tests',
                                                                               'LAYER_4_ENGINE_STUDIO_C14/MCP_PATCHBAY_C21/FEATURE_MCP/docker']},
                      'FEATURE_MCP.FEATURE_MCP__shared.WORKBENCH_PATH': {'private': ['LAYER_4_ENGINE_STUDIO_C14/MCP_PATCHBAY_C21/FEATURE_MCP/FEATURE_MCP__tests',
                                                                                     'LAYER_4_ENGINE_STUDIO_C14/MCP_PATCHBAY_C21/FEATURE_MCP/FEATURE_MCP__tests/image']}}},
 'io': {'server': {'candidate_test_image_build': {'transport': 'cli',
                                                  'runner': 'uv',
                                                  'module': 'LAYER_4_ENGINE_STUDIO_C14.MCP_PATCHBAY_C21.FEATURE_MCP.docker.candidate_image_cli',
                                                  'arguments': ['build',
                                                                '--project-root',
                                                                '<project-root>',
                                                                '--attempt',
                                                                '<attempt-id>',
                                                                '--scratch',
                                                                '<attempt-directory>',
                                                                '[--packaged-assets]']},
                   'candidate_test_image_cleanup': {'transport': 'cli',
                                                    'runner': 'uv',
                                                    'module': 'LAYER_4_ENGINE_STUDIO_C14.MCP_PATCHBAY_C21.FEATURE_MCP.docker.candidate_image_cli',
                                                    'arguments': ['cleanup',
                                                                  '--project-root',
                                                                  '<project-root>',
                                                                  '--attempt',
                                                                  '<attempt-id>',
                                                                  '--image',
                                                                  '<image-id>']},
                   'shared_mcp_launcher': {'transport': 'cli',
                                           'runner': 'uv',
                                           'path': 'LAYER_4_ENGINE_STUDIO_C14/MCP_PATCHBAY_C21/FEATURE_MCP/docker/shared_mcp_launcher.py'},
                   'tool_rest': {'transport': 'http',
                                 'routes': {'GET /': 'catalog',
                                            'POST /': 'invoke'}},
                   'workbench_http': {'transport': 'http',
                                      'routes': {'page': 'GET '
                                                         '/anechoic/iwe-console/{project_name}',
                                                 'legacy_page': 'GET '
                                                                '/anechoic/workbench/{project_name}',
                                                 'interface': 'POST '
                                                              '/anechoic/{project_name}/api/interface',
                                                 'operation': 'POST '
                                                              '/anechoic/{project_name}/api/{action}'}},
                   'project_mcp': {'transport': 'cli',
                                   'runner': 'managed_python',
                                   'module': 'MCP_PATCHBAY_C21.FEATURE_MCP.server',
                                   'arguments': ['--project-root',
                                                 '<project-root>'],
                                   'optional_arguments': ['--control-root',
                                                          '<selected-control-root>',
                                                          '--instance-id',
                                                          '<project-instance>',
                                                          '--host-project-root',
                                                          '<host-project-root>',
                                                          '--transport',
                                                          '<stdio-or-streamable-http>'],
                                   'streamable_http_path': '/anechoic/mcp'},
                   'shared_runtime_mcp': {'transport': 'http',
                                          'path': '/anechoic/mcp',
                                          'protocol': 'mcp'}},
        'client': [{'component': 'C91',
                    'interface': 'current_openapi_export',
                    'stage': 'image build'},
                   {'component': 'C45', 'interface': 'project_admission'},
                   {'component': 'C45', 'interface': 'tool_api'},
                   {'component': 'C45',
                    'interface': 'shared_tool_coordinator'},
                   {'component': 'C45', 'interface': 'workbench_api'},
                   {'component': 'C30', 'interface': 'guarded_read'},
                   {'component': 'C50',
                    'interface': 'image_model_stage'}]},
 'state': {'reads': ['selected Project binding and Manifest',
                     'canonical machine-local runtime.toml with byte '
                     'limits and currentness checks',
                     'Backend Tool catalog'],
           'writes': ['Project launcher lock and readiness receipts',
                      'disposable image build context and image ID',
                      'bounded transport health observations',
                      'parent pipe for the shared Backend process']}}
```

## Component Contract

### Delegate admitted MCP Tool calls

#### Guarantee

For an admitted Project, expose the Tools in the Backend JSON catalog.
Preserve each Tool's name, description, and input schema. Forward the
Tool name, arguments, and request context to Backend and return its
result or failure through MCP.

Expose the same delegation over stdio and Streamable HTTP. In shared
HTTP mode bind each call to its explicit Project. Keep the request's
session and public URL context with the bound call.

Backend owns Tool eligibility, validation, and dispatch. MCP can read the
Project Manifest and runtime settings through declared interfaces for
Project binding and startup. The MCP bridge has zero production
cross-Component imports.

#### References

AN-S-1381, AN-S-1391, AN-S-3044, and AN-T-2944.

### Expose the Backend Tool API on the Console origin

#### Guarantee

Serve `GET /` and `POST /` on the Console origin. In shared
mode, forward both operations to the C45 shared Tool coordinator on its
private Unix socket. MCP loads its catalog from the coordinator at startup
and uses the same invocation operation.

C45 owns the shared catalog, Tool validation, Tool dispatch, and Project
admission. C21 checks the HTTP transport and the returned Project receipt.

In each admitted Console page, set the `anechoic-project-instance` meta
element to that Project's instance.

Forward the canonical invocation fields `name`, `arguments`, `session_id`,
and `public_base_url`. For public HTTP, derive `public_base_url` from the
admitted request origin. Forward `X-Anechoic-Project-Instance` when
present. Require same-origin requests when the browser supplies origin
information. Limit both the incoming JSON body and the forwarded shared
invocation to 65,536 bytes. Measure the forwarded body after inserting
the admitted origin.

For shared `GET /`, require a list of valid Tool descriptors. For
shared `POST /`, preserve a valid Backend result or typed refusal
and its HTTP status. Reject an invalid Project receipt with 502. Reject
other malformed Backend envelopes with 503.

In direct mode, serve the Backend-derived Tool catalog loaded at gateway
startup. Invoke Tools through the Backend client bound to the Project.
Keep the existing private Backend envelope.

Retain the legacy named Workbench routes and the `/interface` wrapper
for terminal clients. The wrapper checks the origin, JSON media type, and
65,536-byte body limit. It checks the Project binding and passes the Tool
name unchanged to the Backend. The Backend decides Tool eligibility.

#### References

AN-S-3059@62 and AN-T-4085@1-draft.

```python trace
declare_trace_contract(
    action='forward_tool_rest',
    cases={'shared_catalog': {'must_effect': (('C45.shared_tool_coordinator',
                                     'catalog',
                                     {'endpoint': 'GET /'}),)},
 'shared_invocation': {'must_effect': (('C45.shared_tool_coordinator',
                                        'invoke',
                                        {'endpoint': 'POST '
                                                     '/'}),)},
 'direct_catalog': {'must_effect': (('C21.backend_catalog_snapshot',
                                     'read'),),
                    'forbid_effect': ('bound_backend_client',)},
 'direct_invocation': {'must_effect': (('bound_backend_client',
                                        'invoke',
                                        {'endpoint': 'POST '
                                                     '/'}),)},
 'transport_refused': {'forbid_effect': ('C45.shared_tool_coordinator',
                                         'bound_backend_client')},
 'legacy_forwarded': {'must_effect': (('Backend.tool_dispatch',
                                       'invoke'),),
                      'same_values': ((('legacy_interface', 'name'),
                                       ('legacy_dispatch', 'name')),),
                      'value_types': {('legacy_interface', 'name'): 'string',
                                      ('legacy_dispatch', 'name'): 'string'}},
 'legacy_refused': {'forbid_effect': ('Backend.tool_dispatch',)},
 'shared_receipt_refused': {'must_effect': (('C45.shared_tool_coordinator',
                                             'invoke',
                                             {'endpoint': 'POST '
                                                          '/'}),
                                            ('C21.tool_rest_reply',
                                             'refused',
                                             {'status': 502})),
                            'must_precede': ((('C45.shared_tool_coordinator',
                                               'invoke'),
                                              ('C21.tool_rest_reply',
                                               'refused')),)},
 'shared_reply_invalid': {'must_effect': (('C45.shared_tool_coordinator',
                                           'invoke',
                                           {'endpoint': 'POST '
                                                        '/'}),
                                          ('C21.tool_rest_reply',
                                           'refused',
                                           {'status': 503})),
                          'must_precede': ((('C45.shared_tool_coordinator',
                                             'invoke'),
                                            ('C21.tool_rest_reply',
                                             'refused')),)},
 'shared_catalog_invalid': {'must_effect': (('C45.shared_tool_coordinator',
                                             'catalog',
                                             {'endpoint': 'GET '
                                                          '/'}),
                                            ('C21.tool_rest_reply',
                                             'refused',
                                             {'status': 503})),
                            'must_precede': ((('C45.shared_tool_coordinator',
                                               'catalog'),
                                              ('C21.tool_rest_reply',
                                               'refused')),)}},
)
```

### Package the Current Tool OpenAPI document

#### Guarantee

During the image build, invoke C91's `current_openapi_export` with the
packaged Current Tool registry and Framework Version. Install its output
at `/usr/local/share/anechoic/openapi.json`. Treat exporter failures as
build failures.

Copy only the generated OpenAPI document from the export stage. Keep the
C91 executable and its runtime out of the Current image. The C45 shared
Tool coordinator supplies live discovery and invocation.
