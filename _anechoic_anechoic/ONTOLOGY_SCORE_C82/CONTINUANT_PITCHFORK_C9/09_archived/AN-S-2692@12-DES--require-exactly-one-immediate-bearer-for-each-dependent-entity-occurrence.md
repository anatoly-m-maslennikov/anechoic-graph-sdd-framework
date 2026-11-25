---
atom_family: SPEC
atom_id: AN-S-2692
container:
  component: C9
tier: 1
context:
  lens: DES
state:
  status: archived
  version: 12
  updated_at: 2026-10-29 09:30:11 +0400
---
## Summary

Require exactly one immediate bearer for each dependent Entity occurrence

## Claim scope

Declared dependent Entity occurrences and their direct IS_BORNE_BY connections.

## Claim

Every declared dependent Entity occurrence must have exactly one immediate bearer, identified by one outgoing direct IS_BORNE_BY connection to that bearer. A source establishes dependence independently of whether the edge is present, so a missing edge fails this requirement. The named Selection “Dependent Entity Occurrences” selects those declared occurrences; it does not infer dependence from edges or create a bearer connection.

## Semantics

Primary and dependent describe bearer dependence, not separate taxonomy branches. The dependent occurrence has identity qualified by its immediate bearer; the Property definition supplies its value format and direct-value cardinality. The bearer relation count is distinct from the number of values a Property allows.
