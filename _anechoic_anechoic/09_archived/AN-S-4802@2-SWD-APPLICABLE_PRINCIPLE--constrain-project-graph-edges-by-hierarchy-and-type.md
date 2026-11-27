---
atom_family: SPEC
atom_id: AN-S-4802
container:
  component: C00
tier: 1
context:
  lens: SWD
  template: applicable_principle
state:
  status: "archived"
  version: 2
  updated_at: "2026-11-27T13:01:00.100769+00:00"
relations:
  APPLIES:
  - AN-S-1432
---

**P35**

## Summary

Constrain Project graph edges by hierarchy and type

## Claim

### Prose Claim

Prefer a hierarchical Project graph with typed nodes and relations. Minimize the number of allowed edges while keeping those the Project needs. Use endpoint types and scope to limit which edges are allowed.

## Details

For n nodes, one directed relation type without self-loops has n(n−1) candidate edges. The value n! counts possible node orderings. Hierarchy and endpoint rules reduce the edges that are allowed.

### Examples

In the current code, Packages use the defining Package's `__shared` Module and declared import and export rules to limit cross-Package dependencies.
