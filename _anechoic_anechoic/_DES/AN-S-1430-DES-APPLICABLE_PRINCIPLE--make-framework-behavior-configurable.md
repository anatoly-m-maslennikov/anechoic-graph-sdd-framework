---
atom_family: SPEC
atom_id: AN-S-1430
container:
  component: C00
tier: 2
context:
  lens: DES
  template: applicable_principle
state:
  status: active
  version: 3
  updated_at: '2026-11-22T11:00:54.983176+00:00'
relations:
  CONTRIBUTES_TO:
  - AN-S-1438
---

## Summary

Make framework behavior configurable

## Claim

### Prose Claim

Let the Operator inspect and change the framework’s effective configuration. Supported behavior can be selected through explicit configuration without changing the implementation.

## Details

### Examples

An Operator enables the Realization Graph in the Project configuration and inspects the effective setting. The Project can use the graph without an implementation change.
