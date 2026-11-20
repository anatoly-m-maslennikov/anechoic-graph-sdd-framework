---
identity:
  atom_id: AN-S-2850
context:
  container:
    component: C00
  tier: 3
  lens: DES
state:
  status: draft
  version: 28
  updated_at: 2026-11-02 18:35:20 +0400
---
## Summary
Define Restricted CCE Canonical Signature

## Claim scope
parenthesized restricted Boolean expression occurrences **in** Atom Claims.

## Claim

Where a Canonical Signature is interpreted for a parenthesized restricted Boolean expression occurrence in one Atom Claim, the interpretation **must** produce **`=1`** derived non-authoritative comparison value, subject to the following constraints:

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
