---
atom_family: SPEC
atom_id: AN-S-3309
container:
  component: C24
tier: 0
context:
  template: component_contract
  lens: DES
relations:
  ANSWERS:
  - AN-S-3049
state:
  status: "archived"
  version: 2
  updated_at: "2026-11-26T15:09:50.962477+00:00"
---
## Summary

Query the frozen review Entity index

## Guarantee

Given a frozen review context and a query, return the matching Entity
records as JSON, with their source bindings and admission status. Match
the query against Entity names and indexed bodies. Return exact name
matches first. Query only the supplied context. Treat retrieved records
as candidates for review.

## References

AN-S-3049 and AN-T-2947.
