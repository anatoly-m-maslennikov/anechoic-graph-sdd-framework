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
  status: "in_queue"
  version: 4
  updated_at: "2026-11-22T11:41:29.946439+00:00"
---
## Summary

Evaluate a parallel Beta Backend, Kernel, and Workers stack

## Prerequisite

Complete the MCP bridge under AN-T-2944. MCP maps the Backend JSON Tool catalog, forwards calls, and returns responses.

## Work

- Build Kernel, Orchestrator, Workers, and Backend alongside the current
  stack. Name each Beta Component `<component name>_beta_<new component ID>`.
- Use one `stack` setting in the framework checkout's `project.toml`.
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

The first Current and Beta images built through Local Release from the
two values of the same selector. Each image returned the same SQL value
through MCP and the Web API on equivalent Project fixtures. Beta also
returned distinct rows for two separately admitted Projects on a shared
host.

Beta's first catalog has one Tool and its query results omit paging and
column type metadata. The paired Model and Structure build, live
refresh, invalid-build recovery, and comparison against the applicable
Contracts remain part of this task.
