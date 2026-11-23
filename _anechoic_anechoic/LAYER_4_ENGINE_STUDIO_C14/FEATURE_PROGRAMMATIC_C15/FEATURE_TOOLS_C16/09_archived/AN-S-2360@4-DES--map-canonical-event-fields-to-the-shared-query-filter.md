---
atom_family: SPEC
atom_id: AN-S-2360
container:
  component: C16
tier: 3
context:
  lens: DES
state:
  status: archived
  version: 4
  updated_at: 2026-10-24 00:38:25 +0400
---
## Summary

Map canonical Event fields to the shared query filter

# Summary

Map canonical Event fields to the shared query filter

## Scope

The Journal-specific selector namespace for QUERY_FILTER.

## Claim

FIND_AND_FETCH_JOURNAL_EVENTS **must** expose every canonical Event field as a valid selector to CA-R-1850's shared QUERY_FILTER contract.

## Details

The namespace is `event:/<RFC6901-pointer>`: `event:/` addresses the complete
Event only for full-Event query, and every other selector is an RFC6901 pointer
from the Event root, including escaped object keys and array indices. A selector
is a JSON string under CA-R-1850's RFC8259 literal grammar. This mapping exposes
scalar, null, array, and object values without dot traversal or coercion; all
comparison semantics remain exactly CA-R-1850.
