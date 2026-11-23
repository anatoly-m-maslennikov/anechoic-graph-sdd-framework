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
  version: 29
  updated_at: '2026-11-13T19:04:12.794939+00:00'
---
## Summary
Define Restricted CCE Canonical Signature

## Claim

### Prose Claim

parenthesized restricted Boolean expression occurrences **in** historical CCE Atom Claims. This definition applies only to historical CCE material and does not establish a prose profile or a canonical signature for ASD-STE100-aligned prose.


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
