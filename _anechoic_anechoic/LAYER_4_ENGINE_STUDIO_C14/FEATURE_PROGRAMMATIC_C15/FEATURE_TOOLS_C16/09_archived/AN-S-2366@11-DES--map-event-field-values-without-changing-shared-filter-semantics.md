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
  version: 11
  updated_at: "2026-11-27T16:16:01.404965+00:00"
---
## Summary

Map Event field values without changing shared filter semantics

## Scope

The Journal-specific selector value extraction.

## Claim

### Prose Claim

FIND_AND_FETCH_JOURNAL_EVENTS **must** pass each selected canonical Event field's exact value state to CA-R-1850 without coercion, normalization, or inferred filename value.

## Details

The Tool marks absent selectors as absent and explicit null as null. Arrays and
objects are passed as parsed RFC8259 structural values, including nested fields
resolved by RFC6901 pointers, without stringification or flattening. It delegates
all comparison and invalid-literal decisions to CA-R-1850.
