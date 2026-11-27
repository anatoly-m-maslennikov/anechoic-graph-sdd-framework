---
atom_family: SPEC
atom_id: AN-S-4704
container:
  component: C27
tier: 4
context:
  template: component_manifest
  lens: SPEC
state:
  status: draft
  version: 5
  updated_at: "2026-11-24T23:12:55.813309+00:00"
---

## Summary

Declare Runtime Images

## Purpose

Build and run runtime images. Delegate shared container launch to the Engine shared MCP launcher and provide reusable Project-scoped container start for Local Release.

## Formal manifest

```python
from anechoic.formal_claims import declare_entity
from anechoic.model import ComponentManifest

declare_entity(
    entity_name='Component Manifest',
    instance=ComponentManifest(
        component_id='C81',
        name='Runtime Images',
        layer=1,
        lens_whitelist=['DevOps'],
        boundaries={
            'code': {'exports': {'LAYER_1_RUNTIME_IMAGES_C81__shared.Cleanup': {'private': ['parent',
                                                                                    'C63',
                                                                                    'LAYER_3_DEVOPS_C80/LAYER_2_RELEASE_C27/LAYER_2_LOCAL_RELEASE_C63/LAYER_2_LOCAL_RELEASE_C63__tests']},
                         'LAYER_1_RUNTIME_IMAGES_C81__shared.Container': {'private': ['parent', 'C63']},
                         'LAYER_1_RUNTIME_IMAGES_C81__shared.FINGERPRINT': {'private': ['parent',
                                                                                        'C63',
                                                                                        'LAYER_3_DEVOPS_C80/LAYER_2_RELEASE_C27/LAYER_2_LOCAL_RELEASE_C63/LAYER_2_LOCAL_RELEASE_C63__tests']},
                         'LAYER_1_RUNTIME_IMAGES_C81__shared.IDENTIFIER': {'private': ['parent', 'C63']},
                         'LAYER_1_RUNTIME_IMAGES_C81__shared.IMAGE': {'private': ['parent', 'C63']},
                         'LAYER_1_RUNTIME_IMAGES_C81__shared.INSTALLATION_LOCK_PATH': {'private': ['parent',
                                                                                                   'C63',
                                                                                                   'LAYER_3_DEVOPS_C80/LAYER_2_RELEASE_C27/LAYER_2_LOCAL_RELEASE_C63/LAYER_2_LOCAL_RELEASE_C63__tests']},
                         'LAYER_1_RUNTIME_IMAGES_C81__shared.ImageManager': {'private': ['parent',
                                                                                         'C63',
                                                                                         'LAYER_3_DEVOPS_C80/LAYER_2_RELEASE_C27/LAYER_2_LOCAL_RELEASE_C63/LAYER_2_LOCAL_RELEASE_C63__tests']},
                         'LAYER_1_RUNTIME_IMAGES_C81__shared.LICENSE_INPUTS': {'private': ['parent',
                                                                                           'C63',
                                                                                           'LAYER_3_DEVOPS_C80/LAYER_2_RELEASE_C27/LAYER_1_RUNTIME_IMAGES_C81/LAYER_1_RUNTIME_IMAGES_C81__tests']},
                         'LAYER_1_RUNTIME_IMAGES_C81__shared.LocalReleaseError': {'private': ['parent',
                                                                                              'C63',
                                                                                              'LAYER_3_DEVOPS_C80/LAYER_2_RELEASE_C27/LAYER_2_LOCAL_RELEASE_C63/LAYER_2_LOCAL_RELEASE_C63__tests']},
                         'LAYER_1_RUNTIME_IMAGES_C81__shared.RETIRED_ASSETS': {'private': ['parent', 'C63']},
                         'LAYER_1_RUNTIME_IMAGES_C81__shared.Runner': {'private': ['parent', 'C63']},
                         'LAYER_1_RUNTIME_IMAGES_C81__shared.SCHEMA': {'private': ['parent',
                                                                                   'C63',
                                                                                   'LAYER_3_DEVOPS_C80/LAYER_2_RELEASE_C27/LAYER_2_LOCAL_RELEASE_C63/LAYER_2_LOCAL_RELEASE_C63__tests']},
                         'LAYER_1_RUNTIME_IMAGES_C81__shared.TOOL_REGISTRY': {'private': ['parent', 'C63']},
                         'LAYER_1_RUNTIME_IMAGES_C81__shared._BETA_REQUIRED': {'private': ['parent',
                                                                                           'C63',
                                                                                           'LAYER_3_DEVOPS_C80/LAYER_2_RELEASE_C27/LAYER_1_RUNTIME_IMAGES_C81/LAYER_1_RUNTIME_IMAGES_C81__tests']},
                         'LAYER_1_RUNTIME_IMAGES_C81__shared._LAYER_NAMES': {'private': ['parent', 'C63']},
                         'LAYER_1_RUNTIME_IMAGES_C81__shared._RUN_ID': {'private': ['parent', 'C63']},
                         'LAYER_1_RUNTIME_IMAGES_C81__shared._cleanup_staging': {'private': ['parent', 'C63']},
                         'LAYER_1_RUNTIME_IMAGES_C81__shared._clear_owned': {'private': ['parent', 'C63']},
                         'LAYER_1_RUNTIME_IMAGES_C81__shared._clear_target': {'private': ['parent', 'C63']},
                         'LAYER_1_RUNTIME_IMAGES_C81__shared._copy_tree': {'private': ['parent', 'C63']},
                         'LAYER_1_RUNTIME_IMAGES_C81__shared._file_identity': {'private': ['parent', 'C63']},
                         'LAYER_1_RUNTIME_IMAGES_C81__shared._git_checkpoint': {'private': ['parent', 'C63']},
                         'LAYER_1_RUNTIME_IMAGES_C81__shared._ignored': {'private': ['parent', 'C63']},
                         'LAYER_1_RUNTIME_IMAGES_C81__shared._image_manager': {'private': ['parent', 'C63']},
                         'LAYER_1_RUNTIME_IMAGES_C81__shared._install_bootstrap': {'private': ['parent', 'C63']},
                         'LAYER_1_RUNTIME_IMAGES_C81__shared._installation_lock': {'private': ['parent', 'C63']},
                         'LAYER_1_RUNTIME_IMAGES_C81__shared._native_release_sources': {'private': ['parent',
                                                                                                    'C63',
                                                                                                    'LAYER_3_DEVOPS_C80/LAYER_2_RELEASE_C27/LAYER_2_LOCAL_RELEASE_C63/LAYER_2_LOCAL_RELEASE_C63__tests']},
                         'LAYER_1_RUNTIME_IMAGES_C81__shared._new_staging_directory': {'private': ['parent',
                                                                                                   'C63']},
                         'LAYER_1_RUNTIME_IMAGES_C81__shared._owned_directory': {'private': ['parent', 'C63']},
                         'LAYER_1_RUNTIME_IMAGES_C81__shared._project_path': {'private': ['parent', 'C63']},
                         'LAYER_1_RUNTIME_IMAGES_C81__shared._relative': {'private': ['parent', 'C63']},
                         'LAYER_1_RUNTIME_IMAGES_C81__shared._release_lock': {'private': ['parent', 'C63']},
                         'LAYER_1_RUNTIME_IMAGES_C81__shared._root': {'private': ['parent', 'C63']},
                         'LAYER_1_RUNTIME_IMAGES_C81__shared._target': {'private': ['parent', 'C63']},
                         'LAYER_1_RUNTIME_IMAGES_C81__shared._verify_package': {'private': ['parent', 'C63']},
                         'LAYER_1_RUNTIME_IMAGES_C81__shared._walk_regular_files': {'private': ['parent', 'C63']},
                         'LAYER_1_RUNTIME_IMAGES_C81__shared.build_image': {'private': ['parent', 'C63']},
                         'LAYER_1_RUNTIME_IMAGES_C81__shared.find_release_container': {'private': ['C63']},
                         'LAYER_1_RUNTIME_IMAGES_C81__shared.image_labels': {'private': ['parent', 'C63']},
                         'LAYER_1_RUNTIME_IMAGES_C81__shared.image_metadata': {'private': ['parent', 'C63']},
                         'LAYER_1_RUNTIME_IMAGES_C81__shared.launch_shared_image': {'private': ['parent', 'C63']},
                         'LAYER_1_RUNTIME_IMAGES_C81__shared.local_release_safety': {'private': ['parent',
                                                                                                 'C63',
                                                                                                 'LAYER_3_DEVOPS_C80/LAYER_2_RELEASE_C27/LAYER_2_LOCAL_RELEASE_C63/LAYER_2_LOCAL_RELEASE_C63__tests']},
                         'LAYER_1_RUNTIME_IMAGES_C81__shared.owner_labels': {'private': ['parent',
                                                                                         'C63',
                                                                                         'LAYER_3_DEVOPS_C80/LAYER_2_RELEASE_C27/LAYER_2_LOCAL_RELEASE_C63/LAYER_2_LOCAL_RELEASE_C63__tests']},
                         'LAYER_1_RUNTIME_IMAGES_C81__shared.read_release_selection': {'private': ['parent',
                                                                                                   'C63',
                                                                                                   'LAYER_3_DEVOPS_C80/LAYER_2_RELEASE_C27/LAYER_2_LOCAL_RELEASE_C63/LAYER_2_LOCAL_RELEASE_C63__tests']},
                         'LAYER_1_RUNTIME_IMAGES_C81__shared.ready_predecessor': {'private': ['parent', 'C63']},
                         'LAYER_1_RUNTIME_IMAGES_C81__shared.reconcile_release_container': {'private': ['C63']},
                         'LAYER_1_RUNTIME_IMAGES_C81__shared.release_image_provenance': {'private': ['parent',
                                                                                                     'C63',
                                                                                                     'LAYER_3_DEVOPS_C80/LAYER_2_RELEASE_C27/LAYER_2_LOCAL_RELEASE_C63/LAYER_2_LOCAL_RELEASE_C63__tests']},
                         'LAYER_1_RUNTIME_IMAGES_C81__shared.release_inputs': {'private': ['parent', 'C63']},
                         'LAYER_1_RUNTIME_IMAGES_C81__shared.run_docker': {'private': ['parent', 'C63']},
                         'LAYER_1_RUNTIME_IMAGES_C81__shared.start_container': {'private': ['parent', 'C63']},
                         'LAYER_1_RUNTIME_IMAGES_C81__shared.verify_release_container': {'private': ['C63',
                                                                                                     'LAYER_3_DEVOPS_C80/LAYER_2_RELEASE_C27/LAYER_1_RUNTIME_IMAGES_C81/LAYER_1_RUNTIME_IMAGES_C81__tests']},
                         'release_assets.LocalReleaseError': {'private': ['LAYER_3_DEVOPS_C80/LAYER_2_RELEASE_C27/LAYER_1_RUNTIME_IMAGES_C81/LAYER_1_RUNTIME_IMAGES_C81__tests']},
                         'release_container.start_container': {'private': ['LAYER_3_DEVOPS_C80/LAYER_2_RELEASE_C27/LAYER_1_RUNTIME_IMAGES_C81/LAYER_1_RUNTIME_IMAGES_C81__tests']},
                         'release_images': {'private': ['LAYER_3_DEVOPS_C80/LAYER_2_RELEASE_C27/LAYER_1_RUNTIME_IMAGES_C81/LAYER_1_RUNTIME_IMAGES_C81__tests']},
                         'release_inputs': {'private': ['LAYER_3_DEVOPS_C80/LAYER_2_RELEASE_C27/LAYER_1_RUNTIME_IMAGES_C81/LAYER_1_RUNTIME_IMAGES_C81__tests']},
                         'runtime_build': {'private': ['LAYER_3_DEVOPS_C80/LAYER_2_RELEASE_C27/LAYER_1_RUNTIME_IMAGES_C81/LAYER_1_RUNTIME_IMAGES_C81__tests']}},
             'imports': {'only': ['C81',
                                  'release_assets.LocalReleaseError',
                                  'release_container.start_container',
                                  'release_images',
                                  'release_inputs',
                                  'runtime_build']}},
            'io': {
                'server': {
                    'build_and_run_runtime_images': {'outcomes': {
                        'image_result_reported': {'must_effect': [('C81.image_result', 'reported')]},
                    }},
                    'build_project_image': {'outcomes': {'succeeded': {
                        'must_effect': [('C81.image', 'built')],
                    }}},
                    'start_project_runtime': {'outcomes': {'succeeded': {
                        'must_effect': [('C81.project_container', 'launch_requested'), ('C81.mcp_endpoint', 'healthy')],
                    }}},
                    'apply_shared_runtime_launch': {'outcomes': {
                        'runtime_ready': {
                            'must_effect': [('shared_runtime_launch', 'apply_selected'), ('C21', 'launch_requested'), ('C21', 'ready')],
                            'forbid_effect': ['shared_runtime_mcp_probe', 'shared_runtime_mcp'],
                        },
                        'mcp_verified': {
                            'must_effect': [('shared_runtime_launch', 'apply_selected'), ('C21', 'launch_requested'), ('C21', 'ready'), ('shared_runtime_mcp_probe', 'requested'), ('shared_runtime_mcp', 'verified')],
                        },
                    }},
                    'runtime_images': {
                        'transport': 'cli', 'runner': 'uv',
                        'path': 'LAYER_3_DEVOPS_C80/LAYER_2_RELEASE_C27/release.py',
                        'subcommands': {'build-image': 'C81', 'run-image': 'C81'},
                    },
                },
                'client': [{'component': 'C21', 'interface': 'shared_mcp_launcher'}],
            },
        },
    ),
)
```
