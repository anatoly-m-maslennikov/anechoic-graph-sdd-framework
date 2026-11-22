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
  version: 1
  updated_at: "2026-11-22T11:07:39.394358+00:00"
---
## Summary

Evaluate a parallel Beta Backend, Kernel, and Workers stack

## Prerequisite

Complete the MCP bridge under AN-T-2944. MCP maps the Backend JSON Tool catalog, forwards calls, and returns responses.

## Work

- Build Beta Backend, Kernel, and Workers Components alongside the current stack. Add switches in `project.toml` so the two stacks can be selected independently for comparison.
- Design the boundaries from the start. Use `__shared` and `__public` entry modules for cross-package imports. Define child Components and Component Seeds. Give each Seed one Spec file and an ID such as `_CS123`.
- Inspect the current packages and modules for useful behavior. Adapt the selected code to Beta's contracts, state ownership, and interfaces.
- Build and test both images against the same fixtures and acceptance checks. Investigate every discrepancy against the current Specs and Contracts. Record defects in either image and resolve or document each difference.

## Outcome

Use the two-image evidence to decide whether to continue with Beta and what corrections each stack needs.
