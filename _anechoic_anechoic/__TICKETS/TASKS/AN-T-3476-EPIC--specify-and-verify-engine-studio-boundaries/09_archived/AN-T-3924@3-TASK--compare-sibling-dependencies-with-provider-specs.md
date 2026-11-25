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
  - AN-S-3088@20
  - AN-S-3379@3-draft
  - AN-S-3315@4
  - AN-S-3316@3-draft
  - AN-S-3383@4-draft
state:
  status: archived
  version: 3
  updated_at: '2026-11-25T13:32:10+00:00'
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
Component-target effects. Six call bindings remain unresolved.

For C62 → C66, the `compiler_worker` interface, in-process transport,
and entry `ORCHESTRATOR_C66__shared.Orchestrator.run_worker` match
the provider Manifest, Contract, and Solution. A changed provider
Solution entry produces a conflict in that comparison.

The call arguments and returned fields remain unresolved. C66 records
Worker completion. C62 separately accepts the Model and Structure
artifacts.

For C63 → C81, the provider Contract specifies starting the selected
Project image on the supplied loopback port and returning a
health-checked MCP endpoint. The C63 effects identify the build and
start owner and candidate image. The exact Project-scoped operation
binding remains open.
