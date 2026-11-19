---
cce_version: cce_1
cce_form: obligation
subjects:
  governs: Entity/Object/Continuant/Structural Unit/Scope Unit.Scope
  depends_on:
  - Subject/ANECHOIC/Graph/Node/Project Model/Scope Unit
  - 'Subject/ANECHOIC/Graph/Node/Project Model/Projection/Type: Applicable Methodology'
  - Subject/ANECHOIC/Graph/Node/Project Model/Scope Unit//PROJECT_CONFIGURATION
  - Subject/ANECHOIC/Graph/Node/Project Model/Implementation/Code/Tool
  - Subject/ANECHOIC/Graph/Node/Aspect/Engineering/Architecture/Communication
  - Subject/ANECHOIC/Graph/Node/Aspect/Engineering/Delivery
version: 1
updated_at: 2026-10-29 20:32:25 +0400
relations: {}
llm_session_ids:
- codex:01a02650-eff7-7453-8c37-0699b36773c6
content_role: Requirement
current_scope_unit: CORE_EXTENSIONS
status: Draft
author: Anatoly Maslennikov
atom_id: CA-R-draft
type: Scope Definition
tier: 1
claim_target_scope_unit: FPF
---
## Summary

Provide an optional FPF Skill conforming to Project authority and using canonical Tools via MCP

## Claim scope

FPF

## Claim

FPF **must** provide an optional ANECHOIC Extension that installs one directly invokable project-local `fpf` Skill, conforms **to** the current Applicable Methodology **and** Project Configuration, **and** consumes canonical Tools through MCP **without** requiring a separate `ca` wrapper **or** modifying Core Meta-Model authority.
