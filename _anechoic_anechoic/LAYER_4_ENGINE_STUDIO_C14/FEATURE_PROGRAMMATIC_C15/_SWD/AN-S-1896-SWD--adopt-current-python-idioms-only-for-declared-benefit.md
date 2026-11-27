---
atom_family: SPEC
atom_id: AN-S-1896
concern:
  subject: "Module/(.Language := python)"
  path: "Model/Graph/Node//Artifact//SSOT//Realization/Content"
  relation: "is_contained_by"
container:
  component: C15
tier: 4
context:
  lens: SWD
state:
  status: active
  version: 15
  updated_at: "2026-11-27T16:16:01.404965+00:00"
---

## Summary

Adopt current Python idioms only for declared benefit

## Claim



### Prose Claim
adopt a stable idiom available **in** the selected Python boundary **only** **when** it
improves a named project quality such as correctness, understandability,
safety, **or** measured performance. preserve the simpler supported idiom **when** a
newer construct adds no useful distinction.

## Details


### Applicable when

apply **when** new **or** materially changed PROGRAMMATIC Python source proposes a
runtime-specific language construct **or** concurrency model.

### Procedure

1. state the quality improved **and** the supported Python boundary that admits
   the idiom.
2. prefer the simplest current construct that expresses the required meaning.
3. use f-strings for immediate trusted string construction; use t-strings **only**
   **when** a processor needs structured interpolation data.
4. keep synchronous work synchronous **unless** related concurrent operations
   create a demonstrated need for structured concurrency.
5. record a compatibility exception **when** an admitted host boundary cannot use
   the selected idiom.

### Outcome

current Python capabilities improve the code for an explicit reason **without**
turning novelty into a requirement **or** obscuring the supported boundary.

### Failure or stop

stop adoption **when** the benefit is unnamed, the simpler idiom is equally clear,
**or** the construct exceeds the selected runtime **or** compatibility boundary.

### Sources

- [PEP 750 — Template Strings](https://peps.python.org/pep-0750/)
- [Python documentation: task groups](https://docs.python.org/3.14/library/asyncio-task.html#task-groups)
- [PEP 8 — Style Guide for Python Code](https://peps.python.org/pep-0008/)
- [CA-A-053 — Reconcile shared PROGRAMMATIC policy decisions](../02_analysis_and_advisory/CA-A-053-PROGRAMMATIC-ANALYSIS_RPRT--reconcile-shared-programmatic-policy-decisions.md)
