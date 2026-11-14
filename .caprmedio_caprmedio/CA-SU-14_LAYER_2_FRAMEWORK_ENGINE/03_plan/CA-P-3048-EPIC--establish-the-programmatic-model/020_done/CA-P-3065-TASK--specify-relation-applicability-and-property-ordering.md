---
identity:
  atom_id: CA-P-3065
  ref_id: CA-P-3065
context:
  role: plan
  form: Plan
  label: Task
  tier: 3
  container:
    atom: CA-P-3048
  topics:
    main_subject: CAPRMEDIO_STRUCTURE <+ Scope Unit//MODEL
state:
  version: 1
  status: done
  updated_at: '2026-11-13T19:13:24.513298+00:00'
destination:
  file:
    name: CA-P-3065-TASK--specify-relation-applicability-and-property-ordering.md
    path: .caprmedio_caprmedio/CA-SU-14_LAYER_2_FRAMEWORK_ENGINE/03_plan/CA-P-3048-EPIC--establish-the-programmatic-model/020_done
---
## Summary

Specify Relation applicability and Property ordering

## Work

Review and adopt the RMEDO Drafts for Relation applicability and sibling ordering. Use both Model entities and instances as the default applicability. Use explicit endpoint levels for exceptions such as INSTANCE_OF. Declare IS_ORDERED_RIGHT_AFTER for instance Properties with the same immediate bearer. Derive the canonical sibling order from the predecessor pairs declared for Header and Content. Skip absent Properties when deriving an instance's order. Retain the inverse alias and reject cycles or multiple immediate predecessors or successors.

## Specification

CA-R-2247, CA-R-2965, CA-R-2967, CA-R-2476, CA-R-2473, CA-R-2719, CA-R-2498.

## Progress

CA-R-2247@15 establishes the default. Active CA-R-2965@3 limits ordering to instance Properties with the same immediate bearer and skips absent Properties. Active CA-R-2967@2 places remaining sibling Properties after the declared chain.
