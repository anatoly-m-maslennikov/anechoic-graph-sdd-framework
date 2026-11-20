---
subjects:
  governs: 'Subject/ANECHOIC/Graph/Node/Project Model/Atom/Content Role: Operations/Type'
  depends_on:
  - 'Subject/ANECHOIC/Graph/Node/Project Model/Atom/Content Role: Operations/Type'
  - 'Subject/ANECHOIC/Graph/Node/Project Model/Atom/Content Role: Operations/Type: Action'
  - 'Subject/ANECHOIC/Graph/Node/Project Model/Atom/Content Role: Operations/Type: Workflow'
  - 'Subject/ANECHOIC/Graph/Node/Project Model/Atom/Content Role: Operations/Type: Step'
  - Subject/ANECHOIC/Carrier
version: 22
updated_at: 2026-10-27 19:59:25 +0400
relations: {}
atom_id: CA-D-457@22
content_role: Delivery
current_scope_unit: CORE_META_MODEL
claim_target_scope_unit: CORE_META_MODEL
status: Archived
author: Anatoly Maslennikov
tier: 3
type: Eng Decision
---
# Summary

Serialize Operations Atom Type tokens

## Scope

Operations Atom File Carriers and their Type filename tokens.

## Claim

an Operations Atom File Carrier **must** serialize its Type using this filename-token mapping:

| Operations Atom Type | Filename token |
|---|---|
| Action | `ACTION` |
| Workflow | `WORKFLOW` |
| Step | `STEP` |

## Details
