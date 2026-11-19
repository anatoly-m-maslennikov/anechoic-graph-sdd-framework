---
subjects:
  governs: 'Subject/ANECHOIC/Graph/Node/Project Model/Actor/Type: AI Agent'
  depends_on:
  - 'Subject/ANECHOIC/Graph/Node/Project Model/Actor/Type: AI Agent'
  - 'Subject/ANECHOIC/Graph/Node/Project Model/Atom/Content Role: Concern'
  - Subject/ANECHOIC/Graph/Node/Project Model/Atom
  - 'Subject/ANECHOIC/Graph/Node/Project Model/Actor/Type: Operator'
  - Subject/ANECHOIC/Graph/Node/Project Model/Atom/Content Role
  - Subject/ANECHOIC/Graph/Node/Aspect/Engineering/Execution Control/Effect Authorization
  - Subject/ANECHOIC/Graph/Node/Aspect/Engineering/Execution Control/Decision Confidence
version: 22
updated_at: 2026-10-27 19:59:57 +0400
relations:
  child_of:
  - CA-R-846
  - CA-R-2158
atom_id: CA-R-1561@22
content_role: Requirement
current_scope_unit: CORE_META_MODEL
claim_target_scope_unit: CORE_META_MODEL
status: Archived
author: Anatoly Maslennikov
tier: 2
type: Rule
---
# Summary

Let AI Agents resolve Concerns under bounded authority

## Scope

AI Agent resolution of Concerns under active delegated authority.

## Claim

an identified AI Agent **may** resolve a Concern from active Atoms **when** its active Operator delegation permits **every** required action **and** resolution confidence meets the configured semantic-resolution threshold; the resolution **may** create **or** change Atoms **in** other Content Roles **only** within that same delegated authority.

## Details
