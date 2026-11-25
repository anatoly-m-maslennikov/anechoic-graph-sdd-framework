---
atom_family: SPEC
atom_id: AN-S-2850
container:
  component: C9
tier: 3
context:
  lens: DES
state:
  status: archived
  version: 20
  updated_at: 2026-10-27 06:04:45 +0400
---
## Summary

Define Restricted CCE Canonical Signature

# Summary
Define Restricted CCE Canonical Signature

## Scope
parenthesized restricted Boolean expression occurrences **in** Atom Claims.

## Claim

a Canonical Signature **means** **`=1`** derived non-authoritative comparison value for **`=1`** parenthesized restricted Boolean expression occurrence **in** one Atom Claim, **where** the following constraints apply:

- the grammar is:
  - `group ::= (operand **and** operand [**and** operand ...]) | (operand **or** operand [**or** operand ...])`;
  - `operand ::= atomic predicate | nested group with the same Boolean Operator`;
  - `atomic predicate ::= subject path: value`.
- canonicalization:
  - flattens nested same-operator groups;
  - removes duplicate atomic predicates;
  - sorts the remaining atomic predicates;
  - preserves the root Boolean Operator.
- canonicalization excludes:
  - mixed Boolean Operators;
  - **every** other CCE Operator;
  - unrecognized bold token;
  - unbalanced parentheses;
  - unparseable prose.

## Details
