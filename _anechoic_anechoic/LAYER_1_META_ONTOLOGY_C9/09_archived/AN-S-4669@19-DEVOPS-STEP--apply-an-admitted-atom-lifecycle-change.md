---
atom_family: SPEC
atom_id: AN-S-4669
container:
  component: C9
tier: 3
context:
  template: step
  lens: DevOps
state:
  status: archived
  version: 19
  updated_at: 2026-10-27 19:59:46 +0400
---
## Summary

Apply an admitted Atom lifecycle change

# Summary

Apply an admitted Atom lifecycle change

## Operation

### Kind

Execution.

### Inputs

The requested lifecycle operation, selected Atom or new properties, supplied changes, applicable model and Project context. For Move bind one existing Atom, its source and destination scope; the Action derives the path and preserves identity and content meaning. For a containment cascade the caller supplies one selected target per invocation under CA-R-1521 and CA-D-461/CA-D-467.

### Fixed parameters

None.

### Runs

CA-O-128, Apply authorized Atom lifecycle changes.

### Outputs

The Action's result, including any request for additional input or explicit failure. This Step adds no semantic assessment, retry, rollback, recovery or repair.
