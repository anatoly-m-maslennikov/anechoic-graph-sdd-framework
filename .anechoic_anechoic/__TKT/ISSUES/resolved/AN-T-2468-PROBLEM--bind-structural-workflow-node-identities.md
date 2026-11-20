---
atom_family: TKT
atom_id: AN-T-2468
structure:
  container:
    component: C9
  priority: 2
context:
  template: problem
state:
  status: resolved
  version: 5
  updated_at: 2026-10-23 03:14:50 +0400
---
# Summary

Bind structural Workflow node identities

## Concern

O015's six aliases do not supply the exact Step Atom identities required by the current Workflow graph model.

## Evidences

Independent P1437 directly read O015v6 and R1509v6/R1513v4. The source binds select/prepare/assess-candidate/authorize/apply/assess-result to Action IDs but declares no corresponding Step Atom nodes. Existing structural approval/currentness/preservation behavior is otherwise reusable.

## Blast radius

### Disposition

Done P1445 supplies six actual Step identities O139–144. Independent P1455 and P1456 passed the graph endpoints and all six Step bindings, preserving thirteen transitions and structural authorization/effect guards. This missing-identity defect is resolved. Repeated Workflow-owned bindings are a distinct C425 repair and do not reopen or erase these Step identities; source-stage and runtime acceptance remain gated.

P1445 authors exactly six reusable Step bindings and updates O015's endpoints while preserving its behavior. Separate independent review precedes source-stage acceptance. Keep one parameterized Workflow for all four structural requests; no duplicate definitions or code acceptance.
