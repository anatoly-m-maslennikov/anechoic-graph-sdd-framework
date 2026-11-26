---
atom_family: SPEC
atom_id: AN-S-2851
container:
  component: C9
tier: 3
context:
  lens: SWD
state:
  status: archived
  version: 15
  updated_at: 2026-10-24 01:18:03 +0400
---
## Summary

Derive Restricted CCE Canonical Signatures **without** Source Rewrite

# Summary

Derive Restricted CCE Canonical Signatures **without** Source Rewrite

## Scope

derivation of Canonical Signatures from one selected Atom Carrier folder.

## Claim

**to** derive Canonical Signatures from one selected Atom Carrier folder, the Tool **must** inspect **only** active single-statement Atom Claims, identify **every** outermost parenthesized expression that **contains** the **and** Operator **or** the **or** Operator, derive a Canonical Signature **only** **if** the expression satisfies the Restricted Boolean Expression grammar, emit source-identity evidence **and** **every** exclusion diagnostic, **and** make no source-Carrier rewrite, lifecycle change, Claim merge, **or** authority decision.

## Details
