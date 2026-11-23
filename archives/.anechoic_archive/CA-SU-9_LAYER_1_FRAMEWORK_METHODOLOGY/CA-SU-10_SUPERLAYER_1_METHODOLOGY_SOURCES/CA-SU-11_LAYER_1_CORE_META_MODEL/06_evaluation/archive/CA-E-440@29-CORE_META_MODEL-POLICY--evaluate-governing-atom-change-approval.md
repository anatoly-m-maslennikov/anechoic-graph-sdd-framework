---
version: 29
updated_at: 2026-10-27 19:59:35 +0400
relations:
  child_of:
  - CA-E-001
  evaluation_for:
  - CA-R-1559
  - CA-R-1591
  - CA-R-1552
  - CA-R-1080
subjects:
  governs: 'Subject/ANECHOIC/Graph/Node/Project Model/Actor/Type: AI Agent'
  depends_on:
  - Subject/ANECHOIC/Graph/Node/Project Model/Atom.Author
  - 'Subject/ANECHOIC/Graph/Node/Project Model/Actor/Type: Operator'
  - 'Subject/ANECHOIC/Graph/Node/Project Model/Actor/Type: AI Agent'
  - Subject/ANECHOIC/Graph/Node/Aspect/Engineering/Execution Control/Decision Confidence
  - 'Subject/ANECHOIC/Graph/Node/Project Model/Atom/Content Role: Plan.Autonomous Confidence Threshold'
  - Subject/ANECHOIC/Graph/Node/Project Model/Atom
  - 'Subject/ANECHOIC/Graph/Node/Project Model/Atom/Content Role: Evaluation'
  - 'Subject/ANECHOIC/Graph/Node/Project Model/Atom/Content Role: Plan/Type: Plan'
  - 'Subject/ANECHOIC/Graph/Node/Project Model/Atom/Content Role: Requirement'
  - 'Subject/ANECHOIC/Graph/Node/Project Model/Atom/Content Role: Method'
  - 'Subject/ANECHOIC/Graph/Node/Project Model/Atom/Content Role: Delivery'
  - Subject/ANECHOIC/Graph/Node/Project Model/Project
atom_id: CA-E-440@29
content_role: Evaluation
current_scope_unit: CORE_META_MODEL
claim_target_scope_unit: CORE_META_MODEL
status: Archived
author: Anatoly Maslennikov
type: Policy
tier: 4
---
# Summary

Evaluate governing Atom change approval

## Scope

Governing Atom changes.

## Claim

the governing-Atom change Evaluation **must** return `fail` **if** an Operator-authored Atom changes **without** Operator approval, an AI-authored Atom changes autonomously below the Plan confidence threshold, a permission **or** additional Operator constraint is bypassed, the Author is changed **before** resolving the approval requirement, **or** an omitted **or** unresolved Author is assumed **to** be an AI Agent. it **must** also return `fail` **if** an authorized RMED change is reported against the old unchanged baseline **or** its affected work **and** Evaluations are **not** resolved again. AI authorship **and** sufficient confidence **must not** override an explicit prohibition.

## Details
