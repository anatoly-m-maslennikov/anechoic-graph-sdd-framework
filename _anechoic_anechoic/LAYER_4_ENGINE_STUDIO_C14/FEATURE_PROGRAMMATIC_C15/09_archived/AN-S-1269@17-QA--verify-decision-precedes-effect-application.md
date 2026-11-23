---
atom_family: SPEC
atom_id: AN-S-1269
container:
  component: C15
tier: 3
context:
  lens: QA
state:
  status: archived
  version: 17
  updated_at: 2026-10-24 01:28:26 +0400
---
## Summary

Verify decision precedes effect application

# Verify decision precedes effect application

## Claim checked

one PROGRAMMATIC effect is applied **only** **after** a deterministic decision supplies
its target, ordering, **and** expected outcome.

## Applicable conditions

apply **when** a component combines a decision with an external effect,
asynchronous work, **or** lifecycle transition.

## Test case

evaluate one effect request by observing its decision result **before** allowing
the declared effect owner **to** apply it.

## Acceptance criteria

pass **only** **when** the decision result **contains** the target, ordering, **and** expected
outcome, **and** the effect owner reports completion facts **without** adding,
reordering, **or** suppressing a decision.

## Failure disposition

stop the operation **and** return the missing decision boundary **to** its owner.

## Sources

- [CA-M-425 — Separate deterministic transformations from effects and lifecycle](../05_method/CA-M-425-PROGRAMMATIC-STANDARD-ENG_POLICY--separate-deterministic-transformations-from-effects-and-lifecycle.md)
