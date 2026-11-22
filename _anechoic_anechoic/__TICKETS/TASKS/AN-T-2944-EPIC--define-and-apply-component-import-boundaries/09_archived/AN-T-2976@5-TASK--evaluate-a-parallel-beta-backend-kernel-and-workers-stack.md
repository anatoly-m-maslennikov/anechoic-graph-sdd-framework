---
atom_family: TKT
atom_id: AN-T-2976
container:
  atom: AN-T-2944
priority: 2
context:
  template: task
  label: Task
state:
  status: "archived"
  version: 5
  updated_at: "2026-11-22T12:18:52.195852+00:00"
---
## Summary

Evaluate a parallel Beta Backend, Kernel, and Workers stack

## Prerequisite

Complete the MCP bridge under AN-T-2944. MCP maps the Backend JSON Tool catalog, forwards calls, and returns responses.

## Work

- Build Kernel, Orchestrator, Workers, and Backend alongside the current
  stack. Name each Beta Component `<component name>_beta_<new component ID>`.
- Use one `stack` setting in the `LAYER_5_FRAMEWORK_DELIVERY/project.toml`.
  Its value selects `current` or `beta` as a set. Build each selection
  as a distinct image.
- Confirm child Components and Component Seeds with the proposed map in
  AN-T-2958. Use `__shared` and `__pub` entry Modules for cross-Package
  imports. Give each Seed one Manifest, an ID such as `CS123`, and an
  exact Spec Binding in its implementation Package.
- Inspect existing behavior and adopt the pieces that satisfy Beta's
  Contracts, state ownership, and interfaces.
- Start the comparison with a real Project query backed by Worker-built
  Model and Structure artifacts. Refresh those artifacts after a file
  change. Use identical fixtures and acceptance checks for both images.
- Record discrepancies in either image and evaluate each against the
  applicable Specs and Contracts.

## Outcome

Use the two-image evidence to decide whether to continue with Beta and what corrections each stack needs.

## Verification

Local Release built separate Current and Beta images from the same
selector. Both answered an inline query through MCP and the Web API.
Beta served distinct rows from two Projects on a shared host.

Fresh images ran against identical copies of a Project with a Tier 4
Component Manifest. Both published its initial Structure, added a valid
revision, recorded a failed build for an invalid revision, and recovered
on the next valid edit.

During the failed build, Beta kept both artifacts and the accepted query
row. Current kept both artifacts and exposed the invalid row through its
separate projection path. The two query schemas use different Summary
column names. Beta exposes one Tool and omits paging and type metadata.

The comparison of remaining Tool behavior and Contracts continues.
