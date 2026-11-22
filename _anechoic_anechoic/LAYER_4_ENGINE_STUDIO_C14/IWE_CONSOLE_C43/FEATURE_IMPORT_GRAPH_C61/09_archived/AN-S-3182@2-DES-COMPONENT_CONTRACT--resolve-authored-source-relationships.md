---
atom_family: SPEC
atom_id: AN-S-3182
container:
  component: C61
tier: 1
context:
  template: component_contract
  lens: DES
state:
  status: "archived"
  version: 2
  updated_at: "2026-11-22T13:27:15.910591+00:00"
---

## Summary

Resolve authored source relationships

## Guarantee

Given a Project root and its Python import roots, capture and resolve static
Python imports without executing the analyzed Modules. Each import occurrence
records its source location and either its resolved target or its resolution
status.

Link a direct `<package>__tests` directory to the named owner when that owner
resolves in the Project.

The Graph build CLI returns the resolved rows and read issues as JSON.
Kernel owns publication of the accepted graph.

## References

AN-S-3082 and AN-T-2947.
