---
atom_family: SPEC
atom_id: AN-S-3331
container:
  component: C00
tier: 4
context:
  lens: DES
relations:
  CONTRIBUTES_TO:
  - AN-S-3329
state:
  status: "archived"
  version: 2
  updated_at: "2026-11-25T20:09:39.484194+00:00"
---
## Summary

Bind each MCP operation to a selected Project

## Solution

Resolve the caller's repository selection and bind the operation to
that Project before reading or writing. Use that same Project binding
for queries, Workspaces, Views, and lifecycle operations. Return an
error when the binding is missing, ambiguous, or mismatched.

## References

AN-T-2932, AN-S-1242.
