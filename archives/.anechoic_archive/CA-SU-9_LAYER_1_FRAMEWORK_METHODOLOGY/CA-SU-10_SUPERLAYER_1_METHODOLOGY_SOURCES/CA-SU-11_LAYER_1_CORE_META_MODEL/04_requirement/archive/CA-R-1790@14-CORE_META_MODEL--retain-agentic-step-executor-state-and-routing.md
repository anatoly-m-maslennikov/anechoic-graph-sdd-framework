---
subjects:
  governs: Subject/ANECHOIC/Graph/Node/Project Model/Execution/Step Run
  depends_on:
  - Subject/ANECHOIC/Graph/Node/Project Model/Execution/Step Run
  - Subject/ANECHOIC/Graph/Node/Project Model/Execution/Workflow Run
  - 'Subject/ANECHOIC/Graph/Node/Project Model/Atom/Content Role: Operations/Type: Step'
  - 'Subject/ANECHOIC/Graph/Node/Project Model/Atom/Content Role: Operations/Type: Action'
  - 'Subject/ANECHOIC/Graph/Node/Project Model/Atom/Content Role: Operations/Type: Action/Execution Kind'
  - Subject/ANECHOIC/Graph/Node/Project Model/Execution/Step Run.Execution Context
  - Subject/ANECHOIC/Graph/Node/Project Model/Atom
  - 'Subject/ANECHOIC/Graph/Node/Project Model/Actor/Type: Operator'
  - Subject/ANECHOIC/Graph/Node/Project Model/History/Journal
version: 14
updated_at: 2026-10-27 20:00:03 +0400
relations: {}
atom_id: CA-R-1790@14
content_role: Requirement
current_scope_unit: CORE_META_MODEL
claim_target_scope_unit: CORE_META_MODEL
status: Archived
author: Anatoly Maslennikov
tier: 2
type: Rule
---
# Summary

Retain Agentic Step executor state **and** routing

## Scope

execution coordination during dispatch **or** resumption of an Agentic Step, involving the executor together with the participating session **or** separate Agent context.

## Claim

the executor **must** retain execution state **and** select subsequent Steps from the Workflow's declared transitions. the participating session **or** separate Agent context performs the requested Action; it need **not** reconstruct **or** remember what the Workflow will do next.

## Details
