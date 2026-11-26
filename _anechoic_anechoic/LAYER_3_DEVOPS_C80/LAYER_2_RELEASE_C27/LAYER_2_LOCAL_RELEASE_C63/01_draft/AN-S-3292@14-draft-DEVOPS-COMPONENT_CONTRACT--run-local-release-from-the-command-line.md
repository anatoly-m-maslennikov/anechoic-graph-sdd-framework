---
atom_family: SPEC
atom_id: AN-S-3292
container:
  component: C63
tier: 0
context:
  template: component_contract
  lens: DevOps
state:
  status: draft
  version: 14
  updated_at: '2026-11-25T09:38:50.837904+00:00'
relations:
  ANSWERS:
  - AN-S-3290

---

## Summary

Run Local Release from the command line

## Guarantee

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

## Claim

### Prose Claim

`exact_candidate` requires passing end-to-end and canary checks on the image
built for this release and installed by this release. The workflow uses the same
symbolic image reference for build, verification, and installation.
Both completion outcomes require the candidate image and a healthy MCP
endpoint confirmed for that release.

### Formal Claim

```python cli
declare_cli_contract(
    interface='local_release',
    action='run_local_release',
    runner='uv',
    path='LAYER_3_DEVOPS_C80/LAYER_2_RELEASE_C27/release.py',
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
    output='completed',
    must_effect=(('C81.image', 'built'), ('C81.mcp_endpoint', 'healthy'), ('project_runtime', 'promoted'), ('production_image_display_tag', 'updated'), ('eligible_cleanup', 'completed')),
    must_precede=((('C81.image', 'built'), ('C81.mcp_endpoint', 'healthy')), (('C81.mcp_endpoint', 'healthy'), ('project_runtime', 'promoted')), (('project_runtime', 'promoted'), ('production_image_display_tag', 'updated')), (('production_image_display_tag', 'updated'), ('eligible_cleanup', 'completed'))),
)
```
