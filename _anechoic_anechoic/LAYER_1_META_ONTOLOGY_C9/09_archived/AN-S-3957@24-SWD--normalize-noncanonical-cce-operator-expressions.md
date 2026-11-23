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
  version: 24
  updated_at: 2026-11-02 18:35:20 +0400
---
## Summary

Normalize Noncanonical CCE Operator Expressions

## Claim

### Prose Claim


noncanonical CCE Operator Expressions.


**to** normalize one noncanonical CCE Operator Expression, the Author **must** apply **all** applicable rewrites:

- `each` **to** **every**.
- `equals` **to** **`=`**.
- `does not equal` **to** **`!=`**.
- `both <A> and <B>` **to** `(<A>` **and** `<B>)`.
- `either <A> or <B>` **to** `(<A>` **or** `<B>)`.
- `neither <A> nor <B>` **to** **not** `(<A>` **or** `<B>)`.
