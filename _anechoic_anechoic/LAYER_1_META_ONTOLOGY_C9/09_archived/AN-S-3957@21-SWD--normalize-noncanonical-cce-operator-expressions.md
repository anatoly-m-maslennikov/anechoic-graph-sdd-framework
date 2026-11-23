---
atom_family: SPEC
atom_id: AN-S-3957
container:
  component: C9
tier: 3
context:
  lens: SWD
state:
  status: archived
  version: 21
  updated_at: 2026-10-29 10:13:50 +0400
---
## Summary

Normalize Noncanonical CCE Operator Expressions

## Claim scope

noncanonical CCE Operator Expressions.

## Claim

**to** normalize one noncanonical CCE Operator Expression, the Author **must** apply **all** applicable rewrites:

- `each` **to** **every**.
- `equals` **to** **`=`**.
- `does not equal` **to** **`!=`**.
- `both <A> and <B>` **to** `(<A>` **and** `<B>)`.
- `either <A> or <B>` **to** `(<A>` **or** `<B>)`.
- `neither <A> nor <B>` **to** **not** `(<A>` **or** `<B>)`.
