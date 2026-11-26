---
atom_family: SPEC
atom_id: AN-S-2729
container:
  component: C9
tier: 1
context:
  lens: DES
state:
  status: "archived"
  version: 3
  updated_at: "2026-11-25T23:05:45.552546+00:00"
---
## Summary

CFEL Format constraint intersection

## Claim

### Prose Claim

A comma inside one square-bracket value Format annotation combines constraints by intersection. Each direct value must satisfy every listed constraint. Thus `[int, 0..100]` admits integer values from 0 through 100 inclusive. An empty or incompatible intersection admits no values. Existing curly-brace occurrence and value-cardinality annotations keep their current meanings and remain independent.

## Details

```text
p:: [int, 0..100]{:value count}
```
