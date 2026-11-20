---
identity:
  atom_id: AN-T-1152
context:
  container:
    component: C00
  tier: 3
  template: Spec Proposal
state:
  status: active
  version: 2
  updated_at: 2026-11-02 15:49:28 +0400
---
# Summary

Declare contained kinds only at their structural location

## Decision

Remove the /@(Step) reference beneath Operations. Show Operations with Type Action and Type Workflow; Workflow >{1..} Step >{0..} Substep. A Step exists only inside a Workflow; Substep is distinct and exists inside a Step. The counts describe parts per whole: a Workflow has at least one Step; a Step may have zero or more Substeps. Each contained part still has exactly one immediate whole.

Remove duplicate Continuant classification references for Asset, Code Unit, Documentation, Event Record, Module, Package, Prompt, Resources, Step and Substep. Keep their structural declarations. This does not replace containment with specialization or infer inherited Atom properties for Step through its containing Workflow. Other explicit references, such as recursive Package and Scope Unit containment, remain.

## State

Update Draft model and affected Definition Drafts. No Current promotion, runtime change or new general inheritance rule is adopted by this cleanup.
