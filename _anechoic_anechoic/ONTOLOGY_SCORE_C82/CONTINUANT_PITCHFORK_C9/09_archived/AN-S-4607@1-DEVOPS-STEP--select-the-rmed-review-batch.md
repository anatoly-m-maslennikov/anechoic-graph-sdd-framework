---
atom_family: SPEC
atom_id: AN-S-4607
container:
  component: C9
tier: 3
context:
  template: step
  lens: DevOps
state:
  status: archived
  version: 1
  updated_at: 2026-09-28 16:14:59 +0400
---
## Summary

Select the RMED review batch

# Summary

Select the RMED review batch

## Operation

RMED Review Selection Step **means** the Workflow node invoking **=1** Action, CA-O-105, **in** Integrated context.

- bind inputs from the request, source frontier, applicable authority, settings, effective permissions, budgets, **and** admitted temporary Run directory.
- use native file, command, **and** session capabilities; no MCP server is required. missing capability returns `blocked`, **not** a silent context substitution.
- pass the Action result **and** retained evidence **to** the caller for Workflow routing; do **not** independently copy its behavior.

## Details

the Step binding does **not** authorize mutations beyond the supplied Action permissions.
