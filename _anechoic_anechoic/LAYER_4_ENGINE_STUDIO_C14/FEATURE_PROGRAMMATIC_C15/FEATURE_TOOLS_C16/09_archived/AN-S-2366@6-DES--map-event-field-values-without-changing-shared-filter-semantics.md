---
atom_family: SPEC
atom_id: AN-S-2366
container:
  component: C16
tier: 3
context:
  lens: DES
state:
  status: archived
  version: 6
  updated_at: 2026-10-24 13:39:34 +0400
---
## Summary

Map Event field values without changing shared filter semantics

# Summary

Map Event field values without changing shared filter semantics

## Scope

The Journal-specific selector value extraction.

## Claim

FIND_AND_FETCH_JOURNAL_EVENTS **must** pass each selected canonical Event field's exact value state to CA-R-1850 without coercion, normalization, or inferred filename value.

## Details

The Tool marks absent selectors as absent and explicit null as null. Arrays and
objects are passed as parsed RFC8259 structural values, including nested fields
resolved by RFC6901 pointers, without stringification or flattening. It delegates
all comparison and invalid-literal decisions to CA-R-1850.
