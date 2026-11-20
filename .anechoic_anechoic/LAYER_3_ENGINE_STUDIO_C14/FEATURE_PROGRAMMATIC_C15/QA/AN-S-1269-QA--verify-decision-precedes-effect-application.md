---
identity:
  atom_id: AN-S-1269
context:
  container:
    component: C15
  tier: 5
  lens: QA
state:
  status: active
  version: 26
  updated_at: 2026-11-10 20:47:54 +0400
---

## Summary

Verify decision precedes effect application

## Claim



### Prose Claim
one PROGRAMMATIC effect is applied **only** **after** a deterministic decision supplies
its target, ordering, **and** expected outcome.

## Details

### Applicable conditions

apply **when** a component combines a decision with an external effect,
asynchronous work, **or** lifecycle transition.

### Test case

evaluate one effect request by observing its decision result **before** allowing
the declared effect owner **to** apply it.

### Acceptance criteria


pass **only** **when** the decision result **contains** the target, ordering, **and** expected
outcome, **and** the effect owner reports completion facts **without** adding,
reordering, **or** suppressing a decision.

Verify that completion facts return to the decision boundary and actual execution recording remains with its declared executor. Generated output or a completion fact alone does not claim durable terminal completion.

### Failure disposition

stop the operation **and** return the missing decision boundary **to** its owner.

### Sources

- [CA-M-425 — Separate deterministic transformations from effects and lifecycle](../05_method/CA-M-425-PROGRAMMATIC-DIRECT_POLICY--separate-deterministic-transformations-from-effects-and-lifecycle.md)
