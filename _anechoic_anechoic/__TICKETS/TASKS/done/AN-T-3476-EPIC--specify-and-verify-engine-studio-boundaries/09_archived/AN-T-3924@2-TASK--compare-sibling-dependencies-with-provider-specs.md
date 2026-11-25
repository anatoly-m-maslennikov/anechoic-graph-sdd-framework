---
atom_family: TKT
atom_id: AN-T-3924
container:
  atom: AN-T-3476
priority: 2
context:
  template: task
  label: Task
relations:
  IS_REFERENCE:
  - AN-T-3489
  - AN-S-3380@6-draft
  - AN-S-4732@1
state:
  status: archived
  version: 2
  updated_at: '2026-11-25T13:23:25+00:00'
---
## Summary

Compare sibling dependencies with provider Specs

## Work

Use declared dependencies between sibling Components. Compare the
caller's formal Solution with the provider's Manifest, Contract,
and primary Solution. Check the interface, inputs, guarantees,
outputs, and effects that the caller relies on.

Start with Local Release's dependency on Runtime Images for image
build and launch. Pin both Components' declarations and show which
calling details each source establishes.

## Acceptance

Report a separate verdict against each provider Spec with exact
source links. Distinguish missing call bindings from contradictory
bindings and keep unmodeled guarantees unresolved.

## Findings

The inspected Solution pins include seven sibling edges with
Component-target effects. Their call bindings remain unresolved
against the three provider Specs.

For C63 → C81, the provider Contract specifies starting the selected
Project image on the supplied loopback port and returning a
health-checked MCP endpoint. The C63 effects identify the build and
start owner and candidate image. The exact Project-scoped operation
binding remains open.
