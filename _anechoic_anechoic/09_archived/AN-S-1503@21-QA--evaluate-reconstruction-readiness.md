---
atom_family: SPEC
atom_id: AN-S-1503
container:
  component: C00
tier: 3
context:
  lens: QA
state:
  status: archived
  version: 21
  updated_at: 2026-10-29 07:17:15 +0400
---
## Summary

Evaluate reconstruction readiness

# Evaluate reconstruction readiness

the reconstruction readiness Evaluation **must** return `fail` **if** rebuilding required behavior **or** evaluating the rebuilt result needs authority recovered from the previous Implementation **or** specification work **before** reconstruction; **if** a language change is selected, **then** evaluate readiness against the current RMED **after** its affected Method **and** Delivery updates. absence of a prebuilt alternative **must not** by itself cause failure.

the Evaluation **must not** report runtime equivalence **if** equal complete runtime inputs under unchanged RMED produce different outputs, relevant starting state **or** configuration **or** time **or** randomness **or** external-service responses are omitted from the comparison, applicable Method **or** Delivery constraints are violated, **or** an authorized RMED change is hidden inside the unchanged baseline. source-code differences alone **must not** cause failure. a fixed task order **or** readiness review **without** runtime evidence **must not** be reported as proof of equivalent reconstruction.
