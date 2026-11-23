---
atom_family: TKT
atom_id: AN-T-113
container:
  component: C00
priority: 2
context:
  template: spec_proposal
state:
  status: archived
  version: 2
  updated_at: 2026-10-29 21:51:04 +0400
---
## Summary

Allow Modules and Assets for runtime or tests

# Summary

Allow Modules and Assets for runtime or tests

## Decision

Modules and Asset files can be for runtime or for tests. Runtime versus tests describes usage, not another primary kind: executable Module versus non-executable Asset remains the structural distinction. Both uses stay inside Package.

Examples: application code and test code are Modules; a configuration file consumed by the runtime and fixture data consumed by tests are Assets. Documentation remains descriptive/reference content, separate from the required runtime/test inputs and from executable Prompts.

This resolves the runtime-versus-tests question left in CA-A-1266. It does not add Test Module or Test Asset Types, a mandatory usage property, or a closed purpose enumeration. The remaining Resources member definitions can now be reviewed under this distinction; this record does not silently migrate or retire them.

## State

The affected Definition Drafts and proposal are refined. Current Atoms, implementation files and runtime remain unchanged.
