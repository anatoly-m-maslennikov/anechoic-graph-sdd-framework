---
atom_family: SPEC
atom_id: AN-S-1324
container:
  component: C15
tier: 1
context:
  lens: QA
state:
  status: archived
  version: 7
  updated_at: 2026-10-24 12:35:51 +0400
---
## Summary

Require observable evidence for behavioral acceptance

# Summary

Require observable evidence for behavioral acceptance

## Scope

The foundational evidence boundary for behavioral software Evaluation of PROGRAMMATIC components.

## Claim

Given the applicable Spec and declared failure predicates, behavioral software Evaluation **may** support acceptance **only when** **every** predicate is covered by **`>=1`** reproducible check. No check **may** make acceptance depend solely on replaceable private Implementation structure **when** a semantic **or** public behavior boundary can expose the predicate.

## Details

These necessary evidence conditions do not select a portfolio, cost ranking or fixed test-scope ratio.

## Sources

- [CA-E-389@11 — historical extraction basis](archive/CA-E-389-PROGRAMMATIC-CORE-EVAL_APPROACH--combine-complementary-software-behavior-evidence@11.md)
