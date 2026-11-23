---
atom_family: SPEC
atom_id: AN-S-4268
container:
  component: C21
tier: 2
context:
  lens: SWD
state:
  status: archived
  version: 1
  updated_at: 2026-11-09 07:45:15 +0400
---

## Summary


Load the generated MCP registration asset

## Claim

### Prose Claim

#### Applicable when

MCP starts or explicitly loads a rebuilt installed implementation.

#### Procedure

Read the generated registration asset carried by that installed package. Resolve only its code-owned provider and selected-route entries, then apply the bound Project's configured exclusions. Do not scan native Atoms, Scope Unit graphs or Tool folders for exposure.

#### Outcome

MCP exposes the enabled installed code/configuration surface through its existing backend adapters.

#### Failure or stop

Report missing or malformed registration configuration explicitly. Do not fall back to Atom discovery or expose unlisted helpers.
