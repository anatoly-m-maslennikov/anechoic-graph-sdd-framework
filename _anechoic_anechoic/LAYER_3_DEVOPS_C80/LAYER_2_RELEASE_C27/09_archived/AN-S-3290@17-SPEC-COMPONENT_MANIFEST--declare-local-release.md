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
  status: "archived"
  version: 17
  updated_at: "2026-11-27T14:45:10.285943+00:00"
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
{'code': {'imports': {'only': ['C63',
                               'C81',
                               'local_release_package_phases',
                               'local_release_runner',
                               'local_release_runner._launcher_image',
                               'local_release_test_process.run_logged_test_process',
                               'release_cleanup.cleanup_obsolete_images',
                               'release_cleanup.cleanup_stopped_containers',
                               'release_cleanup_images.record_ready_images',
                               'release_cleanup_tmp.prune_temporary_files']},
          'exports': {'LAYER_2_LOCAL_RELEASE_C63__shared.LocalReleaseRun': {'private': ['LAYER_3_DEVOPS_C80/LAYER_2_RELEASE_C27/LAYER_2_LOCAL_RELEASE_C63/LAYER_2_LOCAL_RELEASE_C63__tests']},
                      'LAYER_2_LOCAL_RELEASE_C63__shared.SnapshotReleaseRun': {'private': ['LAYER_3_DEVOPS_C80/LAYER_2_RELEASE_C27/LAYER_2_LOCAL_RELEASE_C63/LAYER_2_LOCAL_RELEASE_C63__tests']},
                      'LAYER_2_LOCAL_RELEASE_C63__shared.build_package': {'private': ['LAYER_3_DEVOPS_C80/LAYER_2_RELEASE_C27/LAYER_2_LOCAL_RELEASE_C63/LAYER_2_LOCAL_RELEASE_C63__tests']},
                      'LAYER_2_LOCAL_RELEASE_C63__shared.phase_inputs': {'private': ['LAYER_3_DEVOPS_C80/LAYER_2_RELEASE_C27/LAYER_2_LOCAL_RELEASE_C63/LAYER_2_LOCAL_RELEASE_C63__tests']},
                      'LAYER_2_LOCAL_RELEASE_C63__shared.test_environment': {'private': ['LAYER_3_DEVOPS_C80/LAYER_2_RELEASE_C27/LAYER_2_LOCAL_RELEASE_C63/LAYER_2_LOCAL_RELEASE_C63__tests']},
                      'LAYER_2_LOCAL_RELEASE_C63__shared.write_receipt': {'private': ['LAYER_3_DEVOPS_C80/LAYER_2_RELEASE_C27/LAYER_2_LOCAL_RELEASE_C63/LAYER_2_LOCAL_RELEASE_C63__tests']},
                      'LAYER_2_LOCAL_RELEASE_C63__shared.prepare_local': {'private': ['parent']},
                      'LAYER_2_LOCAL_RELEASE_C63__shared.run_snapshot_release': {'private': ['parent',
                                                                                             'LAYER_3_DEVOPS_C80/LAYER_2_RELEASE_C27/LAYER_2_LOCAL_RELEASE_C63/LAYER_2_LOCAL_RELEASE_C63__tests']},
                      'LAYER_2_LOCAL_RELEASE_C63__shared.verify_image': {'private': ['parent',
                                                                                     'LAYER_3_DEVOPS_C80/LAYER_2_RELEASE_C27/LAYER_2_LOCAL_RELEASE_C63/LAYER_2_LOCAL_RELEASE_C63__tests']},
                      'local_release_package_phases': {'private': ['LAYER_3_DEVOPS_C80/LAYER_2_RELEASE_C27/LAYER_2_LOCAL_RELEASE_C63/LAYER_2_LOCAL_RELEASE_C63__tests']},
                      'local_release_runner': {'private': ['LAYER_3_DEVOPS_C80/LAYER_2_RELEASE_C27/LAYER_2_LOCAL_RELEASE_C63/LAYER_2_LOCAL_RELEASE_C63__tests']},
                      'local_release_runner._launcher_image': {'private': ['LAYER_3_DEVOPS_C80/LAYER_2_RELEASE_C27/LAYER_2_LOCAL_RELEASE_C63/LAYER_2_LOCAL_RELEASE_C63__tests']},
                      'local_release_test_process.run_logged_test_process': {'private': ['LAYER_3_DEVOPS_C80/LAYER_2_RELEASE_C27/LAYER_2_LOCAL_RELEASE_C63/LAYER_2_LOCAL_RELEASE_C63__tests']},
                      'release_cleanup.cleanup_obsolete_images': {'private': ['LAYER_3_DEVOPS_C80/LAYER_2_RELEASE_C27/LAYER_2_LOCAL_RELEASE_C63/LAYER_2_LOCAL_RELEASE_C63__tests']},
                      'release_cleanup.cleanup_stopped_containers': {'private': ['LAYER_3_DEVOPS_C80/LAYER_2_RELEASE_C27/LAYER_2_LOCAL_RELEASE_C63/LAYER_2_LOCAL_RELEASE_C63__tests']},
                      'release_cleanup_images.record_ready_images': {'private': ['LAYER_3_DEVOPS_C80/LAYER_2_RELEASE_C27/LAYER_2_LOCAL_RELEASE_C63/LAYER_2_LOCAL_RELEASE_C63__tests']},
                      'release_cleanup_tmp.prune_temporary_files': {'private': ['LAYER_3_DEVOPS_C80/LAYER_2_RELEASE_C27/LAYER_2_LOCAL_RELEASE_C63/LAYER_2_LOCAL_RELEASE_C63__tests']},
                      'LAYER_2_LOCAL_RELEASE_C63__shared.run_local_release': {'private': ['parent',
                                                                                          'LAYER_3_DEVOPS_C80/LAYER_2_RELEASE_C27/LAYER_2_LOCAL_RELEASE_C63/LAYER_2_LOCAL_RELEASE_C63__tests']},
                      'LAYER_2_LOCAL_RELEASE_C63__shared.local_release': {'private': ['LAYER_3_DEVOPS_C80/LAYER_2_RELEASE_C27/LAYER_2_LOCAL_RELEASE_C63/LAYER_2_LOCAL_RELEASE_C63__tests']},
                      'LAYER_2_LOCAL_RELEASE_C63__shared._GENERATED_ASSETS': {'private': ['LAYER_3_DEVOPS_C80/LAYER_2_RELEASE_C27/LAYER_2_LOCAL_RELEASE_C63/LAYER_2_LOCAL_RELEASE_C63__tests']}}},
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
