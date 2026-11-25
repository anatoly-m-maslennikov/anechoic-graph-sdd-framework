---
atom_family: SPEC
atom_id: AN-S-2952
container:
  component: C9
tier: 3
context:
  lens: DES
state:
  status: draft
  version: 1
  updated_at: 2026-11-06 20:09:50 +0400
---
## Summary

Declare the CFEL fallback operator

## Claim

### Prose Claim

`x ?== y` returns `y` when `x` is empty; otherwise it returns `x`. Empty means `null`, an empty string, or an undefined value. An omitted value is undefined. Zero, false, whitespace and empty collections are not empty under this operator.

Evaluate a chain from left to right by applying the same binary rule. Evaluate `y` only when `x` is empty. If every operand is empty, the chain returns its final operand. The operator assigns neither operand and does not write the Model or a Carrier.
