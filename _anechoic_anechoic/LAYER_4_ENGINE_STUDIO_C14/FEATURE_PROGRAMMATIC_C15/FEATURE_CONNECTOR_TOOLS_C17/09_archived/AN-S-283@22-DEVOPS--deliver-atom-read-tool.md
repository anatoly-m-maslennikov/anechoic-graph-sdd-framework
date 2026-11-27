---
atom_family: SPEC
atom_id: AN-S-283
container:
  component: C17
tier: 4
context:
  lens: DevOps
state:
  status: archived
  version: 22
  updated_at: "2026-11-27T17:35:01.150345+00:00"
---
## Summary

Deliver ATOM_READ Tool

# Deliver ATOM_READ Tool

the `ATOM_READ` Tool **must** deliver its canonical executable Carrier at `LAYER_2_FRAMEWORK_ENGINE/FEATURE_PROGRAMMATIC/FEATURE_TOOLS/ATOM_READ/atom_read.py`; that Carrier realizes `CA-R-864` through the Action `CA-O-047`.

## Required logical Read contract

Under CA-D-625, Read accepts one explicit full Atom ID in the source view fixed by target/context and returns the complete logical Atom state with its actual exact Version and bound source-state evidence. A pre-known Version is not required. If a Version or expected state is supplied for pinned or historical Read, verify it exactly rather than substituting another state. Missing, ambiguous, unavailable or stale bound state fails explicitly; no path or filename alias replaces logical identity. Read invokes neither Find nor Modify.

The existing executable location is the current file adapter binding. This required logical contract is not a claim of implementation, installation or an admitted MCP route; a replaceable backend preserves the same logical request/result boundary.

## Responsibility boundary

Apply the shared connector boundary in AN-S-2478.
