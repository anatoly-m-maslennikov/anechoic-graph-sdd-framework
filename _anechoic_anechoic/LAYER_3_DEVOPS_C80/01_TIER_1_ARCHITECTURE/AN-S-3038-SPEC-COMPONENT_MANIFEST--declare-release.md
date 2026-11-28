---
atom_family: SPEC
atom_id: AN-S-3038
container:
  component: C80
tier: 1
context:
  template: component_manifest
  lens: SPEC
state:
  status: "active"
  version: 13
  updated_at: "2026-11-28T14:01:00+00:00"
---

## Summary

Declare Release

## Component Identity

```python
from anechoic.model import ComponentManifest

ComponentManifest(
    component_id='C27',
    name='Release',
    layer=2,
    lens_whitelist=['DevOps'],
)
```

## Component Boundaries

```python
{'code': {'imports': {'only': ['C27',
                               'C81',
                               'C63',
                               'C64',
                               'image_builder.image_builder__shared',
                               'image_container.image_container__shared',
                               'image_identity.image_identity__shared',
                               'input_selection.input_selection__shared',
                               'image_container.image_container__shared.find_release_container',
                               'image_container.image_container__shared.reconcile_release_container',
                               'image_container.image_container__shared.start_container',
                               'image_container.image_container__shared.verify_release_container',
                               'image_builder.image_builder__shared.ImageManager',
                               'image_builder.image_builder__shared.ready_predecessor',
                               'image_identity.image_identity__shared.LICENSE_INPUTS',
                               'image_identity.image_identity__shared.ENGINE',
                               'image_identity.image_identity__shared.DOCKERFILE',
                               'image_identity.image_identity__shared.DOCKERIGNORE',
                               'image_identity.image_identity__shared.RETIRED_ASSETS',
                               'image_identity.image_identity__shared.TOOL_REGISTRY',
                               'image_identity.image_identity__shared._EXCLUDED',
                               'image_identity.image_identity__shared._SECRETS',
                               'image_identity.image_identity__shared._REQUIRED',
                               'image_identity.image_identity__shared._excluded',
                               'image_identity.image_identity__shared.ImageIdentity',
                               'image_identity.image_identity__shared.ImageInputIdentity',
                               'input_selection.input_selection__shared.read_release_selection',
                               'input_selection.input_selection__shared.read_atom_header',
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
          'exports': {'LAYER_2_RELEASE_C27__shared': {'private': ['LAYER_3_DEVOPS_C80/LAYER_2_RELEASE_C27/LAYER_2_RELEASE_C27__tests']}}},
 'io': {'server': {'release': {'transport': 'cli',
                               'runner': 'uv',
                               'path': 'LAYER_3_DEVOPS_C80/LAYER_2_RELEASE_C27/release.py',
                               'subcommands': {'local': 'C63',
                                               'public': 'C64',
                                               'build-image': 'C81',
                                               'run-image': 'C81'}}}}}
```

## Component Contract

### Dispatch Release and Runtime Image commands

#### Guarantee

The Release CLI has one host entry point. Run this command from the Framework checkout root in the `release` environment.

```sh
UV_PROJECT_ENVIRONMENT="$PWD/LAYER_3_DEVOPS_C80/LAYER_2_RELEASE_C27/.venv-release" \
  uv run --project "$PWD/LAYER_3_DEVOPS_C80/LAYER_1_ENVIRONMENTS_C72/release" --locked --no-env-file \
    python -B "$PWD/LAYER_3_DEVOPS_C80/LAYER_2_RELEASE_C27/release.py" --help
```

Use `local --project-root <root> --run-id <id>` for a same-Project release.
For an explicit target, use
`local --project-root <source> --source-revision <full SHA> --target-project-root <target> --run-id <id>`.
Continue with `--resume`, the same Run ID, and the same Project bindings.
For a split run, pass the current exact source revision. After delivery starts,
pass the revision recorded at the delivery claim.

Use `verify-image --project-root <source> --run-id <id>` for the image
gate. C63 handles these commands under AN-S-3292.

Use `public --project-root <root> --run-id <id>` for Public Release
through C64 under AN-S-3293. Use `build-image --project-root <root>
--run-id <id>` to build an image through C81 under AN-S-4732.
`run-image` delegates launch to the Engine shared MCP launcher.

Release code imports no Project code outside the Release subtree.

The command writes one JSON result to stdout and sends progress to stderr. Exit 0 means completed. Exit 1 means another reported outcome. Exit 2 means invalid CLI usage. Exit 130 means interruption. `--help` lists the commands and exits 0.
