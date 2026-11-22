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
  version: 3
  updated_at: "2026-11-22T14:22:43.973630+00:00"
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
When it receives the attested Structure, it can resolve Test Packages
to the declared Components they exercise.
Kernel owns publication of the accepted graph.

## References

AN-S-3082 and AN-T-2947.
