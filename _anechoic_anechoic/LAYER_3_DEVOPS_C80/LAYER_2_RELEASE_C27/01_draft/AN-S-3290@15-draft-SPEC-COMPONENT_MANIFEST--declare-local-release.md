---
atom_family: SPEC
atom_id: AN-S-3290
container:
  component: C27
tier: 1
context:
  template: component_manifest
  lens: SPEC
state:
  status: draft
  version: 15
  updated_at: "2026-11-24T23:12:55.813309+00:00"
---

## Summary

Declare Local Release

## Purpose

Verify and install a selected Framework Release and report its outcome.

## Component Identity

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
    ),
)
```

## Component Boundaries

```python
{
            'code': {'exports': {'LAYER_2_LOCAL_RELEASE_C63__shared.LocalReleaseRun': {'private': ['LAYER_3_DEVOPS_C80/LAYER_2_RELEASE_C27/LAYER_2_LOCAL_RELEASE_C63/LAYER_2_LOCAL_RELEASE_C63__tests']},
                         'LAYER_2_LOCAL_RELEASE_C63__shared.SnapshotReleaseRun': {'private': ['LAYER_3_DEVOPS_C80/LAYER_2_RELEASE_C27/LAYER_2_LOCAL_RELEASE_C63/LAYER_2_LOCAL_RELEASE_C63__tests']},
                         'LAYER_2_LOCAL_RELEASE_C63__shared._GENERATED_ASSETS': {'private': ['LAYER_3_DEVOPS_C80/LAYER_2_RELEASE_C27/LAYER_2_LOCAL_RELEASE_C63/LAYER_2_LOCAL_RELEASE_C63__tests']},
                         'LAYER_2_LOCAL_RELEASE_C63__shared.build_package': {'private': ['LAYER_3_DEVOPS_C80/LAYER_2_RELEASE_C27/LAYER_2_LOCAL_RELEASE_C63/LAYER_2_LOCAL_RELEASE_C63__tests']},
                         'LAYER_2_LOCAL_RELEASE_C63__shared.local_release': {'private': ['LAYER_3_DEVOPS_C80/LAYER_2_RELEASE_C27/LAYER_2_LOCAL_RELEASE_C63/LAYER_2_LOCAL_RELEASE_C63__tests']},
                         'LAYER_2_LOCAL_RELEASE_C63__shared.phase_inputs': {'private': ['LAYER_3_DEVOPS_C80/LAYER_2_RELEASE_C27/LAYER_2_LOCAL_RELEASE_C63/LAYER_2_LOCAL_RELEASE_C63__tests']},
                         'LAYER_2_LOCAL_RELEASE_C63__shared.prepare_local': {'private': ['parent']},
                         'LAYER_2_LOCAL_RELEASE_C63__shared.run_local_release': {'private': ['parent',
                                                                                             'LAYER_3_DEVOPS_C80/LAYER_2_RELEASE_C27/LAYER_2_LOCAL_RELEASE_C63/LAYER_2_LOCAL_RELEASE_C63__tests']},
                         'LAYER_2_LOCAL_RELEASE_C63__shared.run_snapshot_release': {'private': ['parent',
                                                                                                'LAYER_3_DEVOPS_C80/LAYER_2_RELEASE_C27/LAYER_2_LOCAL_RELEASE_C63/LAYER_2_LOCAL_RELEASE_C63__tests']},
                         'LAYER_2_LOCAL_RELEASE_C63__shared.test_environment': {'private': ['LAYER_3_DEVOPS_C80/LAYER_2_RELEASE_C27/LAYER_2_LOCAL_RELEASE_C63/LAYER_2_LOCAL_RELEASE_C63__tests']},
                         'LAYER_2_LOCAL_RELEASE_C63__shared.verify_image': {'private': ['parent',
                                                                                        'LAYER_3_DEVOPS_C80/LAYER_2_RELEASE_C27/LAYER_2_LOCAL_RELEASE_C63/LAYER_2_LOCAL_RELEASE_C63__tests']},
                         'LAYER_2_LOCAL_RELEASE_C63__shared.write_receipt': {'private': ['LAYER_3_DEVOPS_C80/LAYER_2_RELEASE_C27/LAYER_2_LOCAL_RELEASE_C63/LAYER_2_LOCAL_RELEASE_C63__tests']},
                         'local_release_package_phases': {'private': ['LAYER_3_DEVOPS_C80/LAYER_2_RELEASE_C27/LAYER_2_LOCAL_RELEASE_C63/LAYER_2_LOCAL_RELEASE_C63__tests']},
                         'local_release_runner': {'private': ['LAYER_3_DEVOPS_C80/LAYER_2_RELEASE_C27/LAYER_2_LOCAL_RELEASE_C63/LAYER_2_LOCAL_RELEASE_C63__tests']},
                         'local_release_runner._launcher_image': {'private': ['LAYER_3_DEVOPS_C80/LAYER_2_RELEASE_C27/LAYER_2_LOCAL_RELEASE_C63/LAYER_2_LOCAL_RELEASE_C63__tests']},
                         'local_release_test_process.run_logged_test_process': {'private': ['LAYER_3_DEVOPS_C80/LAYER_2_RELEASE_C27/LAYER_2_LOCAL_RELEASE_C63/LAYER_2_LOCAL_RELEASE_C63__tests']},
                         'release_cleanup.cleanup_obsolete_images': {'private': ['LAYER_3_DEVOPS_C80/LAYER_2_RELEASE_C27/LAYER_2_LOCAL_RELEASE_C63/LAYER_2_LOCAL_RELEASE_C63__tests']},
                         'release_cleanup.cleanup_stopped_containers': {'private': ['LAYER_3_DEVOPS_C80/LAYER_2_RELEASE_C27/LAYER_2_LOCAL_RELEASE_C63/LAYER_2_LOCAL_RELEASE_C63__tests']},
                         'release_cleanup_images.record_ready_images': {'private': ['LAYER_3_DEVOPS_C80/LAYER_2_RELEASE_C27/LAYER_2_LOCAL_RELEASE_C63/LAYER_2_LOCAL_RELEASE_C63__tests']},
                         'release_cleanup_tmp.prune_temporary_files': {'private': ['LAYER_3_DEVOPS_C80/LAYER_2_RELEASE_C27/LAYER_2_LOCAL_RELEASE_C63/LAYER_2_LOCAL_RELEASE_C63__tests']}},
             'imports': {'only': ['C63',
                                  'C81',
                                  'local_release_package_phases',
                                  'local_release_runner',
                                  'local_release_runner._launcher_image',
                                  'local_release_test_process.run_logged_test_process',
                                  'release_cleanup.cleanup_obsolete_images',
                                  'release_cleanup.cleanup_stopped_containers',
                                  'release_cleanup_images.record_ready_images',
                                  'release_cleanup_tmp.prune_temporary_files']}},
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
                'client': [
                    {'component': 'C19', 'interface': 'test_suite'},
                    {'component': 'C81', 'interface': 'build_project_image'},
                    {'component': 'C81', 'interface': 'start_project_runtime'},
                ],
            },
            'state': {
                'reads': ['Project Manifest literals', 'Checked-in registry', 'Active sources', 'Project checkout'],
                'writes': ['Project checkout', 'Local Framework installation', 'Project MCP runtime', 'Local Release receipts'],
            },
        }
```

## Component Contract

Local Release checkpoints Git, bumps the candidate version, and selects
Active source Atoms.
Selecting a test module leaves both required gates in force.

Use `prepare-local` with an exact base commit, literal changed paths, and
an isolated loopback port to prepare a private checkout for Local Release.
Report its exact revision. Installation belongs to the subsequent Local Release.

Install the verified package and its `ane` Skill. Preserve authoring sources and
protected configuration. Delegate the candidate image build and Project runtime
launch to C81. Request `build_project_image` for the selected checkout and
use its returned candidate image for verification and installation. Request
`start_project_runtime` for that image and the Project Manifest port; use its
returned health-checked MCP endpoint as readiness evidence. C81 uses its
`start_container` helper to launch Docker directly for the Project runtime.

The installed candidate is promoted as the Project runtime when its production
MCP endpoint is healthy. Then update its production image display tag.

If the tag update fails, report cleanup pending. Do not remove obsolete images
or prune the build cache or temporary files.

After a successful tag update, apply the retention standard. Report incomplete cleanup separately from runtime promotion failure.

Report the failed step and observed effects on failure. Write release receipts
under `.anechoic_runtime/simple_local_release/` and test logs under
`.anechoic_tmp/simple_local_release/`.

If Project selection fails before execution, report
`validate_project_selection` and an empty list of effects.

`exact_candidate` requires passing end-to-end and canary checks on the image
built for this release and installed by this release. The workflow uses the same
symbolic image reference for build, verification, and installation.
Both completion outcomes require the candidate image and a healthy MCP
endpoint confirmed for that release.

```python cli
declare_cli_contract(
    interface='local_release',
    action='run_local_release',
    command='local',
    checks={
        'guarantees': {
            'host_checks_before_build': 'static_then_functional',
            'image_checks_before_install': 'exact_candidate',
            'build_owner': 'C81',
            'install_owner': 'C63',
            'start_owner': 'C81',
        },
    },
    cases={
        'completed': {
            'must_effect': (('C81.image', 'built'), ('C81.mcp_endpoint', 'healthy'), ('project_runtime', 'promoted'), ('production_image_display_tag', 'updated'), ('eligible_cleanup', 'completed')),
            'must_precede': ((('C81.image', 'built'), ('C81.mcp_endpoint', 'healthy')), (('C81.mcp_endpoint', 'healthy'), ('project_runtime', 'promoted')), (('project_runtime', 'promoted'), ('production_image_display_tag', 'updated')), (('production_image_display_tag', 'updated'), ('eligible_cleanup', 'completed'))),
        },
        'failed': {'must_effect': (('release_failure', 'reported'),)},
        'completed_with_cleanup_pending': {
            'must_effect': (('C81.image', 'built'), ('C81.mcp_endpoint', 'healthy'), ('project_runtime', 'promoted'), ('eligible_cleanup', 'pending')),
        },
    },
)
```
