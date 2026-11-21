---
atom_family: TKT
atom_id: AN-T-2923
container:
  component: C00
priority: 2
context:
  template: epic
state:
  status: archived
  version: 1
  updated_at: '2026-11-20T15:23:41.110589+00:00'
---
## Summary

Separate primary entity Manifests from Property declarations

## Objective

Make identity and Primary/Property classification explicit in the Model.
Declare Properties separately and compile them into the types and
validators used by implementation.

## Work

1. AN-T-2924 defines the ontology and whitelist.
2. AN-T-2925 updates Manifest Compiler and Model Host after the ontology is set.
3. AN-T-2926 applies the approved layout to the Project's Manifests.

## Reference

AN-T-2791, Manifest Runtime.
