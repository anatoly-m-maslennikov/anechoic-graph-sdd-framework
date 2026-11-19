---
subjects:
  governs: 'Subject/ANECHOIC/Graph/Node/Project Model/Atom/Content Role: Plan.Autonomous Confidence Threshold'
  depends_on:
  - 'Subject/ANECHOIC/Graph/Node/Project Model/Atom/Content Role: Plan/Type: Plan'
  - Subject/ANECHOIC/Graph/Node/Aspect/Engineering/Execution Control/Decision Confidence
  - 'Subject/ANECHOIC/Graph/Node/Project Model/Actor/Type: Operator'
  - Subject/ANECHOIC/Graph/Node/Project Model/Project.Framework Settings
version: 18
updated_at: 2026-10-27 19:59:58 +0400
relations: {}
atom_id: CA-R-1587@18
content_role: Requirement
current_scope_unit: CORE_META_MODEL
claim_target_scope_unit: CORE_META_MODEL
status: Archived
author: Anatoly Maslennikov
tier: 1
type: Rule
---
# Summary

Require an effective confidence threshold for Plan execution

## Scope

autonomous Plan execution decisions.

## Claim

**every** autonomous Plan execution decision **must** resolve **=1** effective Autonomous Confidence Threshold from its applicable explicit **or** inherited source under CA-M-271.

## Details
