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
  status: "active"
  version: 20
  updated_at: "2026-11-28T14:47:45+00:00"
---

## Summary

Declare Local Release

## Component Identity

```python
from anechoic.model import ComponentManifest

ComponentManifest(
    component_id='C63',
    name='Local Release',
    layer=2,
    lens_whitelist=['DevOps'],
)
```

## Component Boundaries

```python
{'code': {'imports': {'only': [
                               'local_release_delivery.COPY_PHASES',
                               'local_release_delivery.INSTALL_PHASES',
                               'local_release_delivery.PRESERVE_FRAMEWORK',
                               'local_release_delivery.abort_lock',
                               'local_release_delivery.check_targets',
                               'local_release_delivery.launcher_lock',
                               'local_release_delivery.verify_recorded_targets',
                               'local_release_gates._LOGS',
                               'local_release_gates._ROOT',
                               'local_release_gates._canary_endpoint',
                               'local_release_gates.run_gate',
                               'local_release_git.ReleaseGitCheckpoints',
                               'local_release_previous.previous_container',
                               'local_release_progress.BUILD',
                               'local_release_progress.CANARY',
                               'local_release_progress.COPY',
                               'local_release_progress.IMAGE',
                               'local_release_progress.IMAGE_TEST',
                               'local_release_progress.ReleaseProgress',
                               'local_release_progress.STATIC',
                               'local_release_reports',
                               'local_release_state.Journal',
                               'local_release_state.PHASES',
                               'local_release_state.atomic_write',
                               'local_release_state.failure_evidence',
                               'local_release_state.open_artifacts',
                               'local_release_state.release_evidence',
                               'local_release_state.source_identity',
                               'prepare_local_files._overlay',
                               'prepare_local_files._parts',
                               'prepare_local_port._project_port',
                               'prepare_local_port._rewrite_port',
                               'prepare_test_environment.check_locked_engine',
                               'prepare_test_environment.ensure_test_environment',
                               'release_phase_inputs.phase_inputs',
                               'release_support._BOOTSTRAP',
                               'release_support._DEFAULT_PRODUCT',
                               'release_support._GENERATED_ASSETS',
                               'release_support._PRESERVED_NAMES',
                               'release_support._ROOT_PROJECT_GOAL',
                               'release_support._build_predecessor',
                               'release_support._failed_test_output',
                               'release_support._launcher_image',
                               'release_support._prepare_package',
                               'release_support._read_version',
                               'snapshot_inputs._COMMIT',
                               'snapshot_inputs._source_version',
                               'snapshot_inputs.target_runtime_digest','C63',
                               'C81',
                               'image_builder.image_builder__shared.ImageManager',
                               'image_builder.image_builder__shared.ready_predecessor',
                               'image_container.image_container__shared.find_release_container',
                               'image_container.image_container__shared.reconcile_release_container',
                               'image_container.image_container__shared.start_container',
                               'image_container.image_container__shared.verify_release_container',
                               'image_identity.image_identity__shared.RETIRED_ASSETS',
                               'image_identity.image_identity__shared.TOOL_REGISTRY',
                               'input_selection.input_selection__shared.read_release_selection',
                               'local_release_package_phases',
                               'local_release_runner',
                               'local_release_runner._launcher_image',
                               'local_release_test_process.run_logged_test_process',
                               'release_cleanup.cleanup_obsolete_images',
                               'release_cleanup.cleanup_stopped_containers',
                               'release_cleanup_images.record_ready_images',
                               'release_cleanup_tmp.prune_temporary_files',
                               'release_cleanup_ops._package__shared.release_cleanup',
                               'release_cleanup_ops._package__shared.release_support',
                               'release_cleanup_ops._package__shared.release_cleanup_image_scan',
                               'release_cleanup_ops._package__shared.release_cleanup_images',
                               'release_cleanup_ops._package__shared.release_cleanup_tmp',
                               'release_cleanup_ops._package__shared.release_package_copy',
                               'release_preparation._package__shared.prepare_local',
                               'release_preparation._package__shared.local_release_package_phases',
                               'release_preparation._package__shared.local_release_proofs',
                               'release_preparation._package__shared.local_release_settings',
                               'release_preparation._package__shared.local_release_progress',
                               'release_state._package__shared.local_release_state',
                               'release_state._package__shared.local_release_journal',
                               'release_state._package__shared.local_release_previous',
                               'release_state._package__shared.release_phase_inputs',
                               'release_state._package__shared.snapshot_inputs',
                               'release_environment._package__shared.local_release_delivery',
                               'release_environment._package__shared.prepare_test_environment',
                               'release_environment._package__shared.local_release_gate_flow',
                               'release_environment._package__shared.local_release_test_process',
                               'release_environment._package__shared.local_release_gates',
                               'release_environment._package__shared.local_release_git',
                               'release_environment._package__shared.prepare_local_port',
                               'release_environment._package__shared.prepare_local_files',
                               'release_execution._package__shared.local_release_recovery',
                               'release_execution._package__shared.local_release_runner_phases',
                               'release_execution._package__shared.local_release_runner_delivery',
                               'release_execution._package__shared.local_release_runner',
                               'release_execution._package__shared.local_release_recovery_artifacts',
                               'LAYER_2_LOCAL_RELEASE_C63__tests.cleanup.test_release_cleanup',
                               'LAYER_2_LOCAL_RELEASE_C63__tests.simple.test_simple_local_release',
                               'LAYER_2_LOCAL_RELEASE_C63__tests.LAYER_2_LOCAL_RELEASE_C63__tests__shared.SimpleReleaseFixture',
                               'LAYER_2_LOCAL_RELEASE_C63__tests.LAYER_2_LOCAL_RELEASE_C63__tests__shared',
                               'LAYER_2_LOCAL_RELEASE_C63__tests._prepare_local_fixture',
                               'LAYER_2_LOCAL_RELEASE_C63__tests.simple.first._simple_release_cases_1',
                               'LAYER_2_LOCAL_RELEASE_C63__tests.simple.first._simple_release_cases_2',
                               'LAYER_2_LOCAL_RELEASE_C63__tests.simple.first._simple_release_cases_3',
                               'LAYER_2_LOCAL_RELEASE_C63__tests.simple.second._simple_release_two_cases_1',
                               'LAYER_2_LOCAL_RELEASE_C63__tests.simple.second._simple_release_two_cases_2',
                               'LAYER_2_LOCAL_RELEASE_C63__tests.simple.second._simple_release_two_cases_3',
                               'LAYER_2_LOCAL_RELEASE_C63__tests.simple.third._simple_release_three_cases_1',
                               'LAYER_2_LOCAL_RELEASE_C63__tests.simple.third._simple_release_three_cases_2',
                               'LAYER_2_LOCAL_RELEASE_C63__tests.simple.fourth._simple_release_four_cases_1',
                               'LAYER_2_LOCAL_RELEASE_C63__tests.simple.fourth._simple_release_four_cases_2']},
          'exports': {'LAYER_2_LOCAL_RELEASE_C63__shared.LocalReleaseRun': {'private': ['LAYER_3_DEVOPS_C80/LAYER_2_RELEASE_C27/LAYER_2_LOCAL_RELEASE_C63/LAYER_2_LOCAL_RELEASE_C63__tests',
                                                                                        'LAYER_3_DEVOPS_C80/LAYER_2_RELEASE_C27/LAYER_2_LOCAL_RELEASE_C63/LAYER_2_LOCAL_RELEASE_C63__tests/simple/fourth']},
                      'LAYER_2_LOCAL_RELEASE_C63__shared.SnapshotReleaseRun': {'private': ['LAYER_3_DEVOPS_C80/LAYER_2_RELEASE_C27/LAYER_2_LOCAL_RELEASE_C63/LAYER_2_LOCAL_RELEASE_C63__tests',
                                                                                           'LAYER_3_DEVOPS_C80/LAYER_2_RELEASE_C27/LAYER_2_LOCAL_RELEASE_C63/LAYER_2_LOCAL_RELEASE_C63__tests/snapshot']},
                      'LAYER_2_LOCAL_RELEASE_C63__shared.build_package': {'private': ['LAYER_3_DEVOPS_C80/LAYER_2_RELEASE_C27/LAYER_2_LOCAL_RELEASE_C63/LAYER_2_LOCAL_RELEASE_C63__tests',
                                                                                      'LAYER_3_DEVOPS_C80/LAYER_2_RELEASE_C27/LAYER_2_LOCAL_RELEASE_C63/LAYER_2_LOCAL_RELEASE_C63__tests/preparation/verification']},
                      'LAYER_2_LOCAL_RELEASE_C63__shared.phase_inputs': {'private': ['LAYER_3_DEVOPS_C80/LAYER_2_RELEASE_C27/LAYER_2_LOCAL_RELEASE_C63/LAYER_2_LOCAL_RELEASE_C63__tests',
                                                                                     'LAYER_3_DEVOPS_C80/LAYER_2_RELEASE_C27/LAYER_2_LOCAL_RELEASE_C63/LAYER_2_LOCAL_RELEASE_C63__tests/preparation/verification']},
                      'LAYER_2_LOCAL_RELEASE_C63__shared.test_environment': {'private': ['LAYER_3_DEVOPS_C80/LAYER_2_RELEASE_C27/LAYER_2_LOCAL_RELEASE_C63/LAYER_2_LOCAL_RELEASE_C63__tests',
                                                                                         'LAYER_3_DEVOPS_C80/LAYER_2_RELEASE_C27/LAYER_2_LOCAL_RELEASE_C63/LAYER_2_LOCAL_RELEASE_C63__tests/snapshot']},
                      'LAYER_2_LOCAL_RELEASE_C63__shared.write_receipt': {'private': ['LAYER_3_DEVOPS_C80/LAYER_2_RELEASE_C27/LAYER_2_LOCAL_RELEASE_C63/LAYER_2_LOCAL_RELEASE_C63__tests',
                                                                                      'LAYER_3_DEVOPS_C80/LAYER_2_RELEASE_C27/LAYER_2_LOCAL_RELEASE_C63/LAYER_2_LOCAL_RELEASE_C63__tests/simple/second']},
                      'LAYER_2_LOCAL_RELEASE_C63__shared.prepare_local': {'private': ['parent',
                                                                                      'LAYER_3_DEVOPS_C80/LAYER_2_RELEASE_C27/LAYER_2_LOCAL_RELEASE_C63/LAYER_2_LOCAL_RELEASE_C63__tests',
                                                                                      'LAYER_3_DEVOPS_C80/LAYER_2_RELEASE_C27/LAYER_2_LOCAL_RELEASE_C63/LAYER_2_LOCAL_RELEASE_C63__tests/preparation']},
                      'LAYER_2_LOCAL_RELEASE_C63__shared.project_port': {'private': ['LAYER_3_DEVOPS_C80/LAYER_2_RELEASE_C27/LAYER_2_LOCAL_RELEASE_C63/LAYER_2_LOCAL_RELEASE_C63__tests',
                                                                                     'LAYER_3_DEVOPS_C80/LAYER_2_RELEASE_C27/LAYER_2_LOCAL_RELEASE_C63/LAYER_2_LOCAL_RELEASE_C63__tests/preparation']},
                      'LAYER_2_LOCAL_RELEASE_C63__shared._rewrite_port': {'private': ['LAYER_3_DEVOPS_C80/LAYER_2_RELEASE_C27/LAYER_2_LOCAL_RELEASE_C63/LAYER_2_LOCAL_RELEASE_C63__tests',
                                                                                      'LAYER_3_DEVOPS_C80/LAYER_2_RELEASE_C27/LAYER_2_LOCAL_RELEASE_C63/LAYER_2_LOCAL_RELEASE_C63__tests/preparation']},
                      'LAYER_2_LOCAL_RELEASE_C63__shared._assert_source_clean': {'private': ['LAYER_3_DEVOPS_C80/LAYER_2_RELEASE_C27/LAYER_2_LOCAL_RELEASE_C63/LAYER_2_LOCAL_RELEASE_C63__tests',
                                                                                             'LAYER_3_DEVOPS_C80/LAYER_2_RELEASE_C27/LAYER_2_LOCAL_RELEASE_C63/LAYER_2_LOCAL_RELEASE_C63__tests/preparation']},
                      'LAYER_2_LOCAL_RELEASE_C63__shared.run_snapshot_release': {'private': ['parent',
                                                                                             'LAYER_3_DEVOPS_C80/LAYER_2_RELEASE_C27/LAYER_2_LOCAL_RELEASE_C63/LAYER_2_LOCAL_RELEASE_C63__tests',
                                                                                             'LAYER_3_DEVOPS_C80/LAYER_2_RELEASE_C27/LAYER_2_LOCAL_RELEASE_C63/LAYER_2_LOCAL_RELEASE_C63__tests/snapshot']},
                      'LAYER_2_LOCAL_RELEASE_C63__shared.verify_image': {'private': ['parent',
                                                                                     'LAYER_3_DEVOPS_C80/LAYER_2_RELEASE_C27/LAYER_2_LOCAL_RELEASE_C63/LAYER_2_LOCAL_RELEASE_C63__tests',
                                                                                     'LAYER_3_DEVOPS_C80/LAYER_2_RELEASE_C27/LAYER_2_LOCAL_RELEASE_C63/LAYER_2_LOCAL_RELEASE_C63__tests/preparation/verification']},
                      'local_release_package_phases': {'private': ['LAYER_3_DEVOPS_C80/LAYER_2_RELEASE_C27/LAYER_2_LOCAL_RELEASE_C63/LAYER_2_LOCAL_RELEASE_C63__tests',
                                                                   'LAYER_3_DEVOPS_C80/LAYER_2_RELEASE_C27/LAYER_2_LOCAL_RELEASE_C63/release_execution',
                                                                   'LAYER_3_DEVOPS_C80/LAYER_2_RELEASE_C27/LAYER_2_LOCAL_RELEASE_C63/LAYER_2_LOCAL_RELEASE_C63__tests/lifecycle',
                                                                   'LAYER_3_DEVOPS_C80/LAYER_2_RELEASE_C27/LAYER_2_LOCAL_RELEASE_C63/LAYER_2_LOCAL_RELEASE_C63__tests/simple/first',
                                                                   'LAYER_3_DEVOPS_C80/LAYER_2_RELEASE_C27/LAYER_2_LOCAL_RELEASE_C63/LAYER_2_LOCAL_RELEASE_C63__tests/simple/fourth',
                                                                   'LAYER_3_DEVOPS_C80/LAYER_2_RELEASE_C27/LAYER_2_LOCAL_RELEASE_C63/LAYER_2_LOCAL_RELEASE_C63__tests/simple/third',
                                                                   'LAYER_3_DEVOPS_C80/LAYER_2_RELEASE_C27/LAYER_2_LOCAL_RELEASE_C63/LAYER_2_LOCAL_RELEASE_C63__tests/snapshot']},
                      'local_release_runner': {'private': ['LAYER_3_DEVOPS_C80/LAYER_2_RELEASE_C27/LAYER_2_LOCAL_RELEASE_C63/LAYER_2_LOCAL_RELEASE_C63__tests',
                                                           'LAYER_3_DEVOPS_C80/LAYER_2_RELEASE_C27/LAYER_2_LOCAL_RELEASE_C63/LAYER_2_LOCAL_RELEASE_C63__tests/cleanup',
                                                           'LAYER_3_DEVOPS_C80/LAYER_2_RELEASE_C27/LAYER_2_LOCAL_RELEASE_C63/LAYER_2_LOCAL_RELEASE_C63__tests/simple/third']},
                      'local_release_runner._launcher_image': {'private': ['LAYER_3_DEVOPS_C80/LAYER_2_RELEASE_C27/LAYER_2_LOCAL_RELEASE_C63/LAYER_2_LOCAL_RELEASE_C63__tests',
                                                                           'LAYER_3_DEVOPS_C80/LAYER_2_RELEASE_C27/LAYER_2_LOCAL_RELEASE_C63/LAYER_2_LOCAL_RELEASE_C63__tests/simple/first']},
                      'local_release_test_process.run_logged_test_process': {'private': ['LAYER_3_DEVOPS_C80/LAYER_2_RELEASE_C27/LAYER_2_LOCAL_RELEASE_C63/LAYER_2_LOCAL_RELEASE_C63__tests',
                                                                                         'LAYER_3_DEVOPS_C80/LAYER_2_RELEASE_C27/LAYER_2_LOCAL_RELEASE_C63/release_execution',
                                                                                         'LAYER_3_DEVOPS_C80/LAYER_2_RELEASE_C27/LAYER_2_LOCAL_RELEASE_C63/LAYER_2_LOCAL_RELEASE_C63__tests/preparation/verification']},
                      'release_cleanup.cleanup_obsolete_images': {'private': ['LAYER_3_DEVOPS_C80/LAYER_2_RELEASE_C27/LAYER_2_LOCAL_RELEASE_C63/LAYER_2_LOCAL_RELEASE_C63__tests',
                                                                              'LAYER_3_DEVOPS_C80/LAYER_2_RELEASE_C27/LAYER_2_LOCAL_RELEASE_C63/release_execution',
                                                                              'LAYER_3_DEVOPS_C80/LAYER_2_RELEASE_C27/LAYER_2_LOCAL_RELEASE_C63/LAYER_2_LOCAL_RELEASE_C63__tests/cleanup/image',
                                                                              'LAYER_3_DEVOPS_C80/LAYER_2_RELEASE_C27/LAYER_2_LOCAL_RELEASE_C63/LAYER_2_LOCAL_RELEASE_C63__tests/cleanup']},
                      'release_cleanup.cleanup_stopped_containers': {'private': ['LAYER_3_DEVOPS_C80/LAYER_2_RELEASE_C27/LAYER_2_LOCAL_RELEASE_C63/LAYER_2_LOCAL_RELEASE_C63__tests',
                                                                                 'LAYER_3_DEVOPS_C80/LAYER_2_RELEASE_C27/LAYER_2_LOCAL_RELEASE_C63/release_execution',
                                                                                 'LAYER_3_DEVOPS_C80/LAYER_2_RELEASE_C27/LAYER_2_LOCAL_RELEASE_C63/LAYER_2_LOCAL_RELEASE_C63__tests/cleanup']},
                      'release_cleanup_images.record_ready_images': {'private': ['LAYER_3_DEVOPS_C80/LAYER_2_RELEASE_C27/LAYER_2_LOCAL_RELEASE_C63/LAYER_2_LOCAL_RELEASE_C63__tests',
                                                                                 'LAYER_3_DEVOPS_C80/LAYER_2_RELEASE_C27/LAYER_2_LOCAL_RELEASE_C63/release_execution',
                                                                                 'LAYER_3_DEVOPS_C80/LAYER_2_RELEASE_C27/LAYER_2_LOCAL_RELEASE_C63/LAYER_2_LOCAL_RELEASE_C63__tests/cleanup']},
                      'release_cleanup_tmp.prune_temporary_files': {'private': ['LAYER_3_DEVOPS_C80/LAYER_2_RELEASE_C27/LAYER_2_LOCAL_RELEASE_C63/LAYER_2_LOCAL_RELEASE_C63__tests',
                                                                                'LAYER_3_DEVOPS_C80/LAYER_2_RELEASE_C27/LAYER_2_LOCAL_RELEASE_C63/release_execution',
                                                                                'LAYER_3_DEVOPS_C80/LAYER_2_RELEASE_C27/LAYER_2_LOCAL_RELEASE_C63/LAYER_2_LOCAL_RELEASE_C63__tests/cleanup']},
                      'LAYER_2_LOCAL_RELEASE_C63__shared.run_local_release': {'private': ['parent',
                                                                                          'LAYER_3_DEVOPS_C80/LAYER_2_RELEASE_C27/LAYER_2_LOCAL_RELEASE_C63/LAYER_2_LOCAL_RELEASE_C63__tests',
                                                                                          'LAYER_3_DEVOPS_C80/LAYER_2_RELEASE_C27/LAYER_2_LOCAL_RELEASE_C63/LAYER_2_LOCAL_RELEASE_C63__tests/cleanup',
                                                                                          'LAYER_3_DEVOPS_C80/LAYER_2_RELEASE_C27/LAYER_2_LOCAL_RELEASE_C63/LAYER_2_LOCAL_RELEASE_C63__tests/cleanup/image',
                                                                                          'LAYER_3_DEVOPS_C80/LAYER_2_RELEASE_C27/LAYER_2_LOCAL_RELEASE_C63/LAYER_2_LOCAL_RELEASE_C63__tests/lifecycle',
                                                                                          'LAYER_3_DEVOPS_C80/LAYER_2_RELEASE_C27/LAYER_2_LOCAL_RELEASE_C63/LAYER_2_LOCAL_RELEASE_C63__tests/preparation',
                                                                                          'LAYER_3_DEVOPS_C80/LAYER_2_RELEASE_C27/LAYER_2_LOCAL_RELEASE_C63/LAYER_2_LOCAL_RELEASE_C63__tests/simple/first',
                                                                                          'LAYER_3_DEVOPS_C80/LAYER_2_RELEASE_C27/LAYER_2_LOCAL_RELEASE_C63/LAYER_2_LOCAL_RELEASE_C63__tests/simple/fourth',
                                                                                          'LAYER_3_DEVOPS_C80/LAYER_2_RELEASE_C27/LAYER_2_LOCAL_RELEASE_C63/LAYER_2_LOCAL_RELEASE_C63__tests/simple/second',
                                                                                          'LAYER_3_DEVOPS_C80/LAYER_2_RELEASE_C27/LAYER_2_LOCAL_RELEASE_C63/LAYER_2_LOCAL_RELEASE_C63__tests/simple/third',
                                                                                          'LAYER_3_DEVOPS_C80/LAYER_2_RELEASE_C27/LAYER_2_LOCAL_RELEASE_C63/LAYER_2_LOCAL_RELEASE_C63__tests/snapshot']},
                      'LAYER_2_LOCAL_RELEASE_C63__shared.local_release': {'private': ['LAYER_3_DEVOPS_C80/LAYER_2_RELEASE_C27/LAYER_2_LOCAL_RELEASE_C63/LAYER_2_LOCAL_RELEASE_C63__tests',
                                                                                      'LAYER_3_DEVOPS_C80/LAYER_2_RELEASE_C27/LAYER_2_LOCAL_RELEASE_C63/LAYER_2_LOCAL_RELEASE_C63__tests/preparation']},
                      'LAYER_2_LOCAL_RELEASE_C63__shared._GENERATED_ASSETS': {'private': ['LAYER_3_DEVOPS_C80/LAYER_2_RELEASE_C27/LAYER_2_LOCAL_RELEASE_C63/LAYER_2_LOCAL_RELEASE_C63__tests',
                                                                                          'LAYER_3_DEVOPS_C80/LAYER_2_RELEASE_C27/LAYER_2_LOCAL_RELEASE_C63/LAYER_2_LOCAL_RELEASE_C63__tests/preparation',
                                                                                          'LAYER_3_DEVOPS_C80/LAYER_2_RELEASE_C27/LAYER_2_LOCAL_RELEASE_C63/LAYER_2_LOCAL_RELEASE_C63__tests/simple/first',
                                                                                          'LAYER_3_DEVOPS_C80/LAYER_2_RELEASE_C27/LAYER_2_LOCAL_RELEASE_C63/LAYER_2_LOCAL_RELEASE_C63__tests/simple/third']},
                      'release_cleanup_ops._package__shared.release_cleanup': {'private': ['parent']},
                      'release_cleanup_ops._package__shared.release_support': {'private': ['parent']},
                      'release_cleanup_ops._package__shared.release_cleanup_image_scan': {'private': ['parent']},
                      'release_cleanup_ops._package__shared.release_cleanup_images': {'private': ['parent']},
                      'release_cleanup_ops._package__shared.release_cleanup_tmp': {'private': ['parent']},
                      'release_cleanup_ops._package__shared.release_package_copy': {'private': ['parent']},
                      'release_preparation._package__shared.prepare_local': {'private': ['parent']},
                      'release_preparation._package__shared.local_release_package_phases': {'private': ['parent']},
                      'release_preparation._package__shared.local_release_proofs': {'private': ['parent']},
                      'release_preparation._package__shared.local_release_settings': {'private': ['parent']},
                      'release_preparation._package__shared.local_release_progress': {'private': ['parent']},
                      'release_state._package__shared.local_release_state': {'private': ['parent']},
                      'release_state._package__shared.local_release_journal': {'private': ['parent']},
                      'release_state._package__shared.local_release_previous': {'private': ['parent']},
                      'release_state._package__shared.release_phase_inputs': {'private': ['parent']},
                      'release_state._package__shared.snapshot_inputs': {'private': ['parent']},
                      'release_environment._package__shared.local_release_delivery': {'private': ['parent']},
                      'release_environment._package__shared.prepare_test_environment': {'private': ['parent']},
                      'release_environment._package__shared.local_release_gate_flow': {'private': ['parent']},
                      'release_environment._package__shared.local_release_test_process': {'private': ['parent']},
                      'release_environment._package__shared.local_release_gates': {'private': ['parent']},
                      'release_environment._package__shared.local_release_git': {'private': ['parent']},
                      'release_environment._package__shared.prepare_local_port': {'private': ['parent']},
                      'release_environment._package__shared.prepare_local_files': {'private': ['parent']},
                      'release_execution._package__shared.local_release_recovery': {'private': ['parent']},
                      'release_execution._package__shared.local_release_runner_phases': {'private': ['parent']},
                      'release_execution._package__shared.local_release_runner_delivery': {'private': ['parent']},
                      'release_execution._package__shared.local_release_runner': {'private': ['parent']},
                      'release_execution._package__shared.local_release_recovery_artifacts': {'private': ['parent']},
                      'local_release_state.open_artifacts': {'private': ['LAYER_3_DEVOPS_C80/LAYER_2_RELEASE_C27/LAYER_2_LOCAL_RELEASE_C63/release_cleanup_ops']},
                      'prepare_local_files._overlay': {'private': ['LAYER_3_DEVOPS_C80/LAYER_2_RELEASE_C27/LAYER_2_LOCAL_RELEASE_C63/release_preparation']},
                      'prepare_local_files._parts': {'private': ['LAYER_3_DEVOPS_C80/LAYER_2_RELEASE_C27/LAYER_2_LOCAL_RELEASE_C63/release_preparation']},
                      'prepare_local_port._project_port': {'private': ['LAYER_3_DEVOPS_C80/LAYER_2_RELEASE_C27/LAYER_2_LOCAL_RELEASE_C63/release_preparation']},
                      'prepare_local_port._rewrite_port': {'private': ['LAYER_3_DEVOPS_C80/LAYER_2_RELEASE_C27/LAYER_2_LOCAL_RELEASE_C63/release_preparation']},
                      'release_support._read_version': {'private': ['LAYER_3_DEVOPS_C80/LAYER_2_RELEASE_C27/LAYER_2_LOCAL_RELEASE_C63/release_preparation',
                                                                    'LAYER_3_DEVOPS_C80/LAYER_2_RELEASE_C27/LAYER_2_LOCAL_RELEASE_C63/release_environment',
                                                                    'LAYER_3_DEVOPS_C80/LAYER_2_RELEASE_C27/LAYER_2_LOCAL_RELEASE_C63/release_execution']},
                      'snapshot_inputs._source_version': {'private': ['LAYER_3_DEVOPS_C80/LAYER_2_RELEASE_C27/LAYER_2_LOCAL_RELEASE_C63/release_preparation']},
                      'release_support._GENERATED_ASSETS': {'private': ['LAYER_3_DEVOPS_C80/LAYER_2_RELEASE_C27/LAYER_2_LOCAL_RELEASE_C63/release_preparation']},
                      'release_support._PRESERVED_NAMES': {'private': ['LAYER_3_DEVOPS_C80/LAYER_2_RELEASE_C27/LAYER_2_LOCAL_RELEASE_C63/release_preparation',
                                                                       'LAYER_3_DEVOPS_C80/LAYER_2_RELEASE_C27/LAYER_2_LOCAL_RELEASE_C63/release_environment']},
                      'release_support._prepare_package': {'private': ['LAYER_3_DEVOPS_C80/LAYER_2_RELEASE_C27/LAYER_2_LOCAL_RELEASE_C63/release_preparation']},
                      'local_release_delivery.PRESERVE_FRAMEWORK': {'private': ['LAYER_3_DEVOPS_C80/LAYER_2_RELEASE_C27/LAYER_2_LOCAL_RELEASE_C63/release_preparation']},
                      'local_release_gates._LOGS': {'private': ['LAYER_3_DEVOPS_C80/LAYER_2_RELEASE_C27/LAYER_2_LOCAL_RELEASE_C63/release_preparation']},
                      'local_release_gates._canary_endpoint': {'private': ['LAYER_3_DEVOPS_C80/LAYER_2_RELEASE_C27/LAYER_2_LOCAL_RELEASE_C63/release_preparation']},
                      'release_support._ROOT_PROJECT_GOAL': {'private': ['LAYER_3_DEVOPS_C80/LAYER_2_RELEASE_C27/LAYER_2_LOCAL_RELEASE_C63/release_preparation']},
                      'snapshot_inputs._COMMIT': {'private': ['LAYER_3_DEVOPS_C80/LAYER_2_RELEASE_C27/LAYER_2_LOCAL_RELEASE_C63/release_preparation']},
                      'local_release_delivery.verify_recorded_targets': {'private': ['LAYER_3_DEVOPS_C80/LAYER_2_RELEASE_C27/LAYER_2_LOCAL_RELEASE_C63/release_preparation',
                                                                                     'LAYER_3_DEVOPS_C80/LAYER_2_RELEASE_C27/LAYER_2_LOCAL_RELEASE_C63/release_execution']},
                      'local_release_gates._ROOT': {'private': ['LAYER_3_DEVOPS_C80/LAYER_2_RELEASE_C27/LAYER_2_LOCAL_RELEASE_C63/release_preparation']},
                      'local_release_git.ReleaseGitCheckpoints': {'private': ['LAYER_3_DEVOPS_C80/LAYER_2_RELEASE_C27/LAYER_2_LOCAL_RELEASE_C63/release_preparation']},
                      'local_release_state.PHASES': {'private': ['LAYER_3_DEVOPS_C80/LAYER_2_RELEASE_C27/LAYER_2_LOCAL_RELEASE_C63/release_preparation',
                                                                 'LAYER_3_DEVOPS_C80/LAYER_2_RELEASE_C27/LAYER_2_LOCAL_RELEASE_C63/release_execution']},
                      'local_release_state.source_identity': {'private': ['LAYER_3_DEVOPS_C80/LAYER_2_RELEASE_C27/LAYER_2_LOCAL_RELEASE_C63/release_preparation']},
                      'prepare_test_environment.check_locked_engine': {'private': ['LAYER_3_DEVOPS_C80/LAYER_2_RELEASE_C27/LAYER_2_LOCAL_RELEASE_C63/release_preparation']},
                      'prepare_test_environment.ensure_test_environment': {'private': ['LAYER_3_DEVOPS_C80/LAYER_2_RELEASE_C27/LAYER_2_LOCAL_RELEASE_C63/release_preparation']},
                      'release_phase_inputs.phase_inputs': {'private': ['LAYER_3_DEVOPS_C80/LAYER_2_RELEASE_C27/LAYER_2_LOCAL_RELEASE_C63/release_preparation']},
                      'snapshot_inputs.target_runtime_digest': {'private': ['LAYER_3_DEVOPS_C80/LAYER_2_RELEASE_C27/LAYER_2_LOCAL_RELEASE_C63/release_preparation']},
                      'release_support._BOOTSTRAP': {'private': ['LAYER_3_DEVOPS_C80/LAYER_2_RELEASE_C27/LAYER_2_LOCAL_RELEASE_C63/release_environment']},
                      'local_release_state.atomic_write': {'private': ['LAYER_3_DEVOPS_C80/LAYER_2_RELEASE_C27/LAYER_2_LOCAL_RELEASE_C63/release_environment']},
                      'local_release_delivery.COPY_PHASES': {'private': ['LAYER_3_DEVOPS_C80/LAYER_2_RELEASE_C27/LAYER_2_LOCAL_RELEASE_C63/release_execution']},
                      'local_release_delivery.INSTALL_PHASES': {'private': ['LAYER_3_DEVOPS_C80/LAYER_2_RELEASE_C27/LAYER_2_LOCAL_RELEASE_C63/release_execution']},
                      'local_release_delivery.abort_lock': {'private': ['LAYER_3_DEVOPS_C80/LAYER_2_RELEASE_C27/LAYER_2_LOCAL_RELEASE_C63/release_execution']},
                      'local_release_delivery.check_targets': {'private': ['LAYER_3_DEVOPS_C80/LAYER_2_RELEASE_C27/LAYER_2_LOCAL_RELEASE_C63/release_execution']},
                      'local_release_delivery.launcher_lock': {'private': ['LAYER_3_DEVOPS_C80/LAYER_2_RELEASE_C27/LAYER_2_LOCAL_RELEASE_C63/release_execution']},
                      'local_release_progress.BUILD': {'private': ['LAYER_3_DEVOPS_C80/LAYER_2_RELEASE_C27/LAYER_2_LOCAL_RELEASE_C63/release_execution']},
                      'local_release_progress.CANARY': {'private': ['LAYER_3_DEVOPS_C80/LAYER_2_RELEASE_C27/LAYER_2_LOCAL_RELEASE_C63/release_execution']},
                      'local_release_progress.COPY': {'private': ['LAYER_3_DEVOPS_C80/LAYER_2_RELEASE_C27/LAYER_2_LOCAL_RELEASE_C63/release_execution']},
                      'local_release_progress.IMAGE': {'private': ['LAYER_3_DEVOPS_C80/LAYER_2_RELEASE_C27/LAYER_2_LOCAL_RELEASE_C63/release_execution']},
                      'local_release_progress.IMAGE_TEST': {'private': ['LAYER_3_DEVOPS_C80/LAYER_2_RELEASE_C27/LAYER_2_LOCAL_RELEASE_C63/release_execution']},
                      'local_release_progress.STATIC': {'private': ['LAYER_3_DEVOPS_C80/LAYER_2_RELEASE_C27/LAYER_2_LOCAL_RELEASE_C63/release_execution']},
                      'local_release_progress.ReleaseProgress': {'private': ['LAYER_3_DEVOPS_C80/LAYER_2_RELEASE_C27/LAYER_2_LOCAL_RELEASE_C63/release_execution']},
                      'local_release_state.Journal': {'private': ['LAYER_3_DEVOPS_C80/LAYER_2_RELEASE_C27/LAYER_2_LOCAL_RELEASE_C63/release_execution']},
                      'release_support._build_predecessor': {'private': ['LAYER_3_DEVOPS_C80/LAYER_2_RELEASE_C27/LAYER_2_LOCAL_RELEASE_C63/release_execution']},
                      'local_release_gates.run_gate': {'private': ['LAYER_3_DEVOPS_C80/LAYER_2_RELEASE_C27/LAYER_2_LOCAL_RELEASE_C63/release_execution']},
                      'local_release_state.failure_evidence': {'private': ['LAYER_3_DEVOPS_C80/LAYER_2_RELEASE_C27/LAYER_2_LOCAL_RELEASE_C63/release_execution']},
                      'local_release_state.release_evidence': {'private': ['LAYER_3_DEVOPS_C80/LAYER_2_RELEASE_C27/LAYER_2_LOCAL_RELEASE_C63/release_execution']},
                      'local_release_previous.previous_container': {'private': ['LAYER_3_DEVOPS_C80/LAYER_2_RELEASE_C27/LAYER_2_LOCAL_RELEASE_C63/release_execution']},
                      'local_release_reports': {'private': ['LAYER_3_DEVOPS_C80/LAYER_2_RELEASE_C27/LAYER_2_LOCAL_RELEASE_C63/release_execution']},
                      'release_support._DEFAULT_PRODUCT': {'private': ['LAYER_3_DEVOPS_C80/LAYER_2_RELEASE_C27/LAYER_2_LOCAL_RELEASE_C63/release_execution']},
                      'release_support._launcher_image': {'private': ['LAYER_3_DEVOPS_C80/LAYER_2_RELEASE_C27/LAYER_2_LOCAL_RELEASE_C63/release_execution']},
                      'release_support._failed_test_output': {'private': ['LAYER_3_DEVOPS_C80/LAYER_2_RELEASE_C27/LAYER_2_LOCAL_RELEASE_C63/release_execution']},
                      'LAYER_2_LOCAL_RELEASE_C63__tests.cleanup.test_release_cleanup': {'private': ['LAYER_3_DEVOPS_C80/LAYER_2_RELEASE_C27/LAYER_2_LOCAL_RELEASE_C63/LAYER_2_LOCAL_RELEASE_C63__tests/cleanup/image']},
                      'LAYER_2_LOCAL_RELEASE_C63__tests.simple.test_simple_local_release': {'private': ['LAYER_3_DEVOPS_C80/LAYER_2_RELEASE_C27/LAYER_2_LOCAL_RELEASE_C63/LAYER_2_LOCAL_RELEASE_C63__tests/cleanup/image',
                                                                                                        'LAYER_3_DEVOPS_C80/LAYER_2_RELEASE_C27/LAYER_2_LOCAL_RELEASE_C63/LAYER_2_LOCAL_RELEASE_C63__tests/cleanup',
                                                                                                        'LAYER_3_DEVOPS_C80/LAYER_2_RELEASE_C27/LAYER_2_LOCAL_RELEASE_C63/LAYER_2_LOCAL_RELEASE_C63__tests/preparation',
                                                                                                        'LAYER_3_DEVOPS_C80/LAYER_2_RELEASE_C27/LAYER_2_LOCAL_RELEASE_C63/LAYER_2_LOCAL_RELEASE_C63__tests']},
                      'LAYER_2_LOCAL_RELEASE_C63__tests.LAYER_2_LOCAL_RELEASE_C63__tests__shared.SimpleReleaseFixture': {'private': ['LAYER_3_DEVOPS_C80/LAYER_2_RELEASE_C27/LAYER_2_LOCAL_RELEASE_C63/LAYER_2_LOCAL_RELEASE_C63__tests/cleanup',
                                                                                                                                     'LAYER_3_DEVOPS_C80/LAYER_2_RELEASE_C27/LAYER_2_LOCAL_RELEASE_C63/LAYER_2_LOCAL_RELEASE_C63__tests/lifecycle']},
                      'LAYER_2_LOCAL_RELEASE_C63__tests.LAYER_2_LOCAL_RELEASE_C63__tests__shared': {'private': ['LAYER_3_DEVOPS_C80/LAYER_2_RELEASE_C27/LAYER_2_LOCAL_RELEASE_C63/LAYER_2_LOCAL_RELEASE_C63__tests/lifecycle',
                                                                                                                'LAYER_3_DEVOPS_C80/LAYER_2_RELEASE_C27/LAYER_2_LOCAL_RELEASE_C63/LAYER_2_LOCAL_RELEASE_C63__tests/simple',
                                                                                                                'LAYER_3_DEVOPS_C80/LAYER_2_RELEASE_C27/LAYER_2_LOCAL_RELEASE_C63/LAYER_2_LOCAL_RELEASE_C63__tests/snapshot']},
                      'LAYER_2_LOCAL_RELEASE_C63__tests._prepare_local_fixture': {'private': ['LAYER_3_DEVOPS_C80/LAYER_2_RELEASE_C27/LAYER_2_LOCAL_RELEASE_C63/LAYER_2_LOCAL_RELEASE_C63__tests/preparation']},
                      'LAYER_2_LOCAL_RELEASE_C63__tests.simple.first._simple_release_cases_1': {'private': ['LAYER_3_DEVOPS_C80/LAYER_2_RELEASE_C27/LAYER_2_LOCAL_RELEASE_C63/LAYER_2_LOCAL_RELEASE_C63__tests/simple']},
                      'LAYER_2_LOCAL_RELEASE_C63__tests.simple.first._simple_release_cases_2': {'private': ['LAYER_3_DEVOPS_C80/LAYER_2_RELEASE_C27/LAYER_2_LOCAL_RELEASE_C63/LAYER_2_LOCAL_RELEASE_C63__tests/simple']},
                      'LAYER_2_LOCAL_RELEASE_C63__tests.simple.first._simple_release_cases_3': {'private': ['LAYER_3_DEVOPS_C80/LAYER_2_RELEASE_C27/LAYER_2_LOCAL_RELEASE_C63/LAYER_2_LOCAL_RELEASE_C63__tests/simple']},
                      'LAYER_2_LOCAL_RELEASE_C63__tests.simple.second._simple_release_two_cases_1': {'private': ['LAYER_3_DEVOPS_C80/LAYER_2_RELEASE_C27/LAYER_2_LOCAL_RELEASE_C63/LAYER_2_LOCAL_RELEASE_C63__tests/simple']},
                      'LAYER_2_LOCAL_RELEASE_C63__tests.simple.second._simple_release_two_cases_2': {'private': ['LAYER_3_DEVOPS_C80/LAYER_2_RELEASE_C27/LAYER_2_LOCAL_RELEASE_C63/LAYER_2_LOCAL_RELEASE_C63__tests/simple']},
                      'LAYER_2_LOCAL_RELEASE_C63__tests.simple.second._simple_release_two_cases_3': {'private': ['LAYER_3_DEVOPS_C80/LAYER_2_RELEASE_C27/LAYER_2_LOCAL_RELEASE_C63/LAYER_2_LOCAL_RELEASE_C63__tests/simple']},
                      'LAYER_2_LOCAL_RELEASE_C63__tests.simple.third._simple_release_three_cases_1': {'private': ['LAYER_3_DEVOPS_C80/LAYER_2_RELEASE_C27/LAYER_2_LOCAL_RELEASE_C63/LAYER_2_LOCAL_RELEASE_C63__tests/simple']},
                      'LAYER_2_LOCAL_RELEASE_C63__tests.simple.third._simple_release_three_cases_2': {'private': ['LAYER_3_DEVOPS_C80/LAYER_2_RELEASE_C27/LAYER_2_LOCAL_RELEASE_C63/LAYER_2_LOCAL_RELEASE_C63__tests/simple']},
                      'LAYER_2_LOCAL_RELEASE_C63__tests.simple.fourth._simple_release_four_cases_1': {'private': ['LAYER_3_DEVOPS_C80/LAYER_2_RELEASE_C27/LAYER_2_LOCAL_RELEASE_C63/LAYER_2_LOCAL_RELEASE_C63__tests/simple']},
                      'LAYER_2_LOCAL_RELEASE_C63__tests.simple.fourth._simple_release_four_cases_2': {'private': ['LAYER_3_DEVOPS_C80/LAYER_2_RELEASE_C27/LAYER_2_LOCAL_RELEASE_C63/LAYER_2_LOCAL_RELEASE_C63__tests/simple']}}},
 'io': {'server': {'test_packaged_image_identity': {'transport': 'cli',
                                                    'runner': 'uv',
                                                    'module': 'LAYER_2_LOCAL_RELEASE_C63.LAYER_2_LOCAL_RELEASE_C63__tests.packaged_image_fixture',
                                                    'arguments': ['<fixture-root>']},
                   'local_release': {'transport': 'cli',
                                     'runner': 'uv',
                                     'path': 'LAYER_3_DEVOPS_C80/LAYER_2_RELEASE_C27/release.py',
                                     'command': 'local'}},
        'client': [{'component': 'C19', 'interface': 'test_suite'}]},
 'state': {'reads': ['Project Manifest literals',
                     'Checked-in registry',
                     'Active sources',
                     'Project checkout'],
           'writes': ['Project checkout',
                      'Local Framework installation',
                      'Project MCP runtime',
                      'Local Release receipts']}}
```

## Component Contract

### Run Local Release from the command line

#### Guarantee

Use the host command in AN-S-3288. Checkpoint Git only for a direct release.
A fresh direct release bumps the candidate version. Package Active source Atoms.

Use the single C19 Test Suite entry in AN-S-3055. Run Static source
analysis and analyzer tests, then the configured required host
Functional cases in the locked development environment. Build the
exact isolated production candidate. Run End-to-End checks and then
the Canary on that immutable candidate before installation. Install
only after all required checks pass. A failed or incomplete required
check stops release before the next step. Apply AN-S-4731 to image
liveness and deadlines.

Before long gates,
launch pinned Chromium, load pinned DuckPGQ, and check locked frontend
dependencies. Use installed dependencies. Report failed prerequisites with
cache paths or setup steps.

`--test-module` keeps both host gates. Record separate image suite and MCP
canary results and logs for `local`. If an older exact source exposes only the
combined image phase, use it whenever either check must run. Accept its joint
result only when both checks pass.

Use `prepare-local` with an exact base commit, literal changed paths, and an
isolated loopback port. Report the private checkout revision for Local Release.

`verify-image` builds the canary package and exact image at the source version.
Run the combined image suite and MCP canary. End with verification results
and retained evidence.

A split run needs a clean checkout at the full source SHA and a managed target.
Use the source version and read-only Git histories. Run host gates on the
source. Test the exact target-owned candidate image. Run its MCP canary in a
disposable target context.

After all gates pass, install the package and its `ane` Skill. Preserve
target authoring inputs, Manifest settings, configuration, and Project data.
Start on the target Manifest port. Tag production after MCP is ready. Apply
AN-S-4733 and report incomplete cleanup separately from promotion failure.

Stop and report each failure. The Operator can fix the inputs and explicitly
continue the same run any number of times. Keep the Run ID, Project bindings,
and allocated version. Before delivery starts, record the current exact source
revision and accept a corrected split SHA from the same source checkout.

Save progress atomically. Continue at the earliest incomplete or invalidated
phase. Reuse a pass only when the phase inputs and required evidence match.
Keep the source revision, input digests, and log path for each retained pass.
Protect the artifacts of open runs.

For a canary-only fix, reuse the exact image and matching image suite result.
Rerun Static when it reads changed verifier source. A runtime input fix
requires a new image and both image checks. Shared input changes invalidate
each phase that uses them.

Freeze the accepted revision, package, and image at the delivery claim.
Reconcile installed files and runtime identity before repeating a delivery
effect. Report unverifiable state. After verified promotion, resume pending
cleanup alone.

Pin the accepted source revision, image build revision, exact image ID and
fingerprint, target Project identity, and verified container readiness in the
result and receipt. Keep receipts under
`.anechoic_runtime/simple_local_release/` and Run ID test logs under `.anechoic_tmp/simple_local_release/`.

Keep an attempt record with the failed step, revision, and available logs.
Report observed effects. If initial selection fails, report
`validate_project_selection` with no effects. After failed production startup,
capture bounded container state and recent logs before cleanup. Report the
affected Docker port or resource. Apply cleanup ownership checks.

#### References

AN-S-3055 and AN-S-4731.
