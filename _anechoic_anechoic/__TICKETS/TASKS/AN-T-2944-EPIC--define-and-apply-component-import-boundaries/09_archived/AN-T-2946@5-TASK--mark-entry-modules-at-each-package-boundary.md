---
atom_family: TKT
atom_id: AN-T-2946
container:
  atom: AN-T-2944
priority: 2
context:
  template: task
state:
  status: "archived"
  version: 5
  updated_at: "2026-11-22T14:39:10.365382+00:00"
---

## Summary

Mark entry Modules at each Package boundary

## Work

Give every Package with direct authored code exactly one direct
`__shared` entry Module. Apply the rule to Component Packages,
Component Seeds, ordinary nested Packages, and Test Packages.

Every import from another Package must target that entry and satisfy
the caller and provider Code Access rules. Keep implementation Modules
Package-local. Declare public or named exports on the same entry when
the Package Contract requires those callers.

Use the Realization Graph to verify entry counts and inbound imports
for each Package. Keep the existing module and function size checks.

## Verification

All 12 Beta implementation and Test Packages pass the entry and Code
Access checks. The Python audit found 50 of 79 Packages with one
shared entry and no inbound imports to other Modules. It found
2154 inbound sites to convert. Continue with the remaining
Python and frontend Packages. Verify their declared Code Access.
