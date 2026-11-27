---
atom_family: SPEC
atom_id: AN-S-3290
container:
  component: C27
tier: 4
context:
  template: component_manifest
  lens: SPEC
state:
  status: "archived"
  version: 14
  updated_at: "2026-11-26T15:54:00.682069+00:00"
---

## Summary

Declare Local Release

## Formal manifest

```python
from anechoic.formal_claims import declare_entity
from anechoic.model import ComponentManifest

declare_entity(
    entity_name='Component Manifest',
    instance=ComponentManifest(
        component_id='C63',
        name='Local Release',
        layer=2,
        lens_whitelist=['DevOps'],
        boundaries={
            'code': {
                'imports': {
                    'only': [
                        'C63', 'C81', 'local_release_package_phases', 'local_release_runner',
                        'local_release_runner._launcher_image', 'local_release_test_process.run_logged_test_process',
                        'release_cleanup.cleanup_obsolete_images',
                        'release_cleanup.cleanup_stopped_containers', 'release_cleanup_images.record_ready_images',
                        'release_cleanup_tmp.prune_temporary_files',
                    ],
                },
                'exports': {
                    'LAYER_2_LOCAL_RELEASE_C63__shared.LocalReleaseRun': {'private': ['LAYER_3_DEVOPS_C80/LAYER_2_RELEASE_C27/LAYER_2_LOCAL_RELEASE_C63/LAYER_2_LOCAL_RELEASE_C63__tests']},
                    'LAYER_2_LOCAL_RELEASE_C63__shared.SnapshotReleaseRun': {'private': ['LAYER_3_DEVOPS_C80/LAYER_2_RELEASE_C27/LAYER_2_LOCAL_RELEASE_C63/LAYER_2_LOCAL_RELEASE_C63__tests']},
                    'LAYER_2_LOCAL_RELEASE_C63__shared.build_package': {'private': ['LAYER_3_DEVOPS_C80/LAYER_2_RELEASE_C27/LAYER_2_LOCAL_RELEASE_C63/LAYER_2_LOCAL_RELEASE_C63__tests']},
                    'LAYER_2_LOCAL_RELEASE_C63__shared.phase_inputs': {'private': ['LAYER_3_DEVOPS_C80/LAYER_2_RELEASE_C27/LAYER_2_LOCAL_RELEASE_C63/LAYER_2_LOCAL_RELEASE_C63__tests']},
                    'LAYER_2_LOCAL_RELEASE_C63__shared.test_environment': {'private': ['LAYER_3_DEVOPS_C80/LAYER_2_RELEASE_C27/LAYER_2_LOCAL_RELEASE_C63/LAYER_2_LOCAL_RELEASE_C63__tests']},
                    'LAYER_2_LOCAL_RELEASE_C63__shared.write_receipt': {'private': ['LAYER_3_DEVOPS_C80/LAYER_2_RELEASE_C27/LAYER_2_LOCAL_RELEASE_C63/LAYER_2_LOCAL_RELEASE_C63__tests']},
                    'LAYER_2_LOCAL_RELEASE_C63__shared.prepare_local': {'private': ['parent']},
                    'LAYER_2_LOCAL_RELEASE_C63__shared.run_snapshot_release': {'private': ['parent', 'LAYER_3_DEVOPS_C80/LAYER_2_RELEASE_C27/LAYER_2_LOCAL_RELEASE_C63/LAYER_2_LOCAL_RELEASE_C63__tests']},
                    'LAYER_2_LOCAL_RELEASE_C63__shared.verify_image': {'private': ['parent', 'LAYER_3_DEVOPS_C80/LAYER_2_RELEASE_C27/LAYER_2_LOCAL_RELEASE_C63/LAYER_2_LOCAL_RELEASE_C63__tests']},
                    'local_release_package_phases': {'private': ['LAYER_3_DEVOPS_C80/LAYER_2_RELEASE_C27/LAYER_2_LOCAL_RELEASE_C63/LAYER_2_LOCAL_RELEASE_C63__tests']},
                    'local_release_runner': {'private': ['LAYER_3_DEVOPS_C80/LAYER_2_RELEASE_C27/LAYER_2_LOCAL_RELEASE_C63/LAYER_2_LOCAL_RELEASE_C63__tests']},
                    'local_release_runner._launcher_image': {'private': ['LAYER_3_DEVOPS_C80/LAYER_2_RELEASE_C27/LAYER_2_LOCAL_RELEASE_C63/LAYER_2_LOCAL_RELEASE_C63__tests']},
                    'local_release_test_process.run_logged_test_process': {'private': ['LAYER_3_DEVOPS_C80/LAYER_2_RELEASE_C27/LAYER_2_LOCAL_RELEASE_C63/LAYER_2_LOCAL_RELEASE_C63__tests']},
                    'release_cleanup.cleanup_obsolete_images': {'private': ['LAYER_3_DEVOPS_C80/LAYER_2_RELEASE_C27/LAYER_2_LOCAL_RELEASE_C63/LAYER_2_LOCAL_RELEASE_C63__tests']},
                    'release_cleanup.cleanup_stopped_containers': {'private': ['LAYER_3_DEVOPS_C80/LAYER_2_RELEASE_C27/LAYER_2_LOCAL_RELEASE_C63/LAYER_2_LOCAL_RELEASE_C63__tests']},
                    'release_cleanup_images.record_ready_images': {'private': ['LAYER_3_DEVOPS_C80/LAYER_2_RELEASE_C27/LAYER_2_LOCAL_RELEASE_C63/LAYER_2_LOCAL_RELEASE_C63__tests']},
                    'release_cleanup_tmp.prune_temporary_files': {'private': ['LAYER_3_DEVOPS_C80/LAYER_2_RELEASE_C27/LAYER_2_LOCAL_RELEASE_C63/LAYER_2_LOCAL_RELEASE_C63__tests']},
                    'LAYER_2_LOCAL_RELEASE_C63__shared.run_local_release': {'private': ['parent', 'LAYER_3_DEVOPS_C80/LAYER_2_RELEASE_C27/LAYER_2_LOCAL_RELEASE_C63/LAYER_2_LOCAL_RELEASE_C63__tests']},
                    'LAYER_2_LOCAL_RELEASE_C63__shared.local_release': {'private': ['LAYER_3_DEVOPS_C80/LAYER_2_RELEASE_C27/LAYER_2_LOCAL_RELEASE_C63/LAYER_2_LOCAL_RELEASE_C63__tests']},
                    'LAYER_2_LOCAL_RELEASE_C63__shared._GENERATED_ASSETS': {'private': ['LAYER_3_DEVOPS_C80/LAYER_2_RELEASE_C27/LAYER_2_LOCAL_RELEASE_C63/LAYER_2_LOCAL_RELEASE_C63__tests']},
                },
            },
            'io': {
                'server': {
                    'test_packaged_image_identity': {
                        'transport': 'cli',
                        'runner': 'uv',
                        'module': 'LAYER_2_LOCAL_RELEASE_C63.LAYER_2_LOCAL_RELEASE_C63__tests.packaged_image_fixture',
                        'arguments': ['<fixture-root>'],
                    },
                    'local_release': {
                        'transport': 'cli',
                        'runner': 'uv',
                        'path': 'LAYER_3_DEVOPS_C80/LAYER_2_RELEASE_C27/release.py',
                        'command': 'local',
                    },
                },
                'client': [{'component': 'C19', 'interface': 'test_suite'}],
            },
            'state': {
                'reads': ['Project Manifest literals', 'Checked-in registry', 'Active sources', 'Project checkout'],
                'writes': ['Project checkout', 'Local Framework installation', 'Project MCP runtime', 'Local Release receipts'],
            },
        },
    ),
)
```
