---
atom_family: SPEC
atom_id: AN-S-4732
container:
  component: C81
tier: 0
context:
  template: component_contract
  lens: DevOps
relations:
  ANSWERS:
  - AN-S-4704
state:
  status: draft
  version: 2
  updated_at: '2026-11-25T00:00:00+00:00'
---

## Summary

Build and run runtime images

## Guarantee

Use the Release CLI. `build-image --project-root <root> --run-id <id>`
builds from the selected checkout. It returns the immutable image ID, input
fingerprint, and version. It performs no release or installation.

`run-image --image <sha256:id>` prepares the shared MCP launch for an exact
image. Use `--host-settings <path>` to select host settings. Without `--apply`,
it returns the launch plan with no container changes. The CLI JSON wire outcome is `completed` in dry-run mode; `launch_planned` is the logical outcome below.

With `--apply`, launch through Engine Studio and wait for readiness. The JSON
result identifies the image and readiness outcome. Use `--verify-mcp` with
`--apply` to add an MCP probe before success.

For Local Release, the same build owner receives the selected checkout and
returns its immutable image. Start uses the selected Project, the exact selected
image, and the supplied loopback port. It returns the health-checked MCP endpoint.
C81 uses `start_container` to launch Docker directly for this Project runtime. The separate shared-image apply path calls C21. These are logical call guarantees; they do not select a CLI or API transport.

## Claim

### Formal Claim

```python cli
declare_cli_contract(
    interface='runtime_images',
    action='build_and_run_runtime_images',
    runner='uv',
    path='LAYER_3_DEVOPS_C80/LAYER_2_RELEASE_C27/release.py',
    subcommands={'build-image': 'C81', 'run-image': 'C81'},
    output='launch_planned',
    must_effect=(('C81', 'launch_plan_prepared'),),
    forbid_effect=('C21', 'apply_shared_runtime_launch'),
)
```

```python trace
declare_trace_contract(
    action='apply_shared_runtime_launch', output='runtime_ready',
    must_effect=(('shared_runtime_launch', 'apply_selected'), ('C21', 'launch_requested'), ('C21', 'ready')),
    must_precede=((('shared_runtime_launch', 'apply_selected'), ('C21', 'launch_requested')), (('C21', 'launch_requested'), ('C21', 'ready'))),
    forbid_effect=('shared_runtime_mcp_probe', 'shared_runtime_mcp'),
)
```

```python trace
declare_trace_contract(
    action='apply_shared_runtime_launch', output='mcp_verified',
    must_effect=(('shared_runtime_launch', 'apply_selected'), ('C21', 'launch_requested'), ('C21', 'ready'), ('shared_runtime_mcp_probe', 'requested'), ('shared_runtime_mcp', 'verified')),
    must_precede=((('shared_runtime_launch', 'apply_selected'), ('C21', 'launch_requested')), (('C21', 'launch_requested'), ('C21', 'ready')), (('C21', 'ready'), ('shared_runtime_mcp_probe', 'requested')), (('shared_runtime_mcp_probe', 'requested'), ('shared_runtime_mcp', 'verified'))),
)
```

```python trace
declare_trace_contract(
    action='build_project_image',
    output='succeeded',
    must_effect=(('C81.image', 'built'),),
)
```

```python trace
declare_trace_contract(
    action='start_project_runtime',
    output='succeeded',
    must_effect=(('C81.project_container', 'launch_requested'), ('C81.mcp_endpoint', 'healthy')),
    must_precede=((('C81.project_container', 'launch_requested'), ('C81.mcp_endpoint', 'healthy')),),
)
```
