---
atom_id: CA-R-1625@21
content_role: Requirement
current_scope_unit: SKILLS
claim_target_scope_unit: SKILLS
author: Anatoly Maslennikov
status: Archived
subjects:
  governs: Subject/ANECHOIC/Graph/Node/Aspect/UX/Entry
  depends_on:
  - 'Subject/ANECHOIC/Graph/Node/Project Model/Actor/Type: AI Agent'
  - 'Subject/ANECHOIC/Graph/Node/Project Model/Atom/Content Role: Operations/Type: Action'
  - 'Subject/ANECHOIC/Graph/Node/Project Model/Actor/Type: Operator'
  - Subject/ANECHOIC/Graph/Node/Aspect/Engineering/Architecture/Communication
  - Subject/ANECHOIC/Graph/Node/Project Model/Execution/Step Run
  - 'Subject/ANECHOIC/Graph/Node/Project Model/Atom/Content Role: Operations/Type: Workflow'
version: 21
updated_at: 2026-10-29 22:26:57 +0400
relations:
  child_of:
  - ANECHOIC-METHODOLOGY-REQU-508
tier: 3
type: Rule
---
## Summary

Provide CA as the universal entry skill

## Claim scope

requests submitted by Operators and AI Agents through the ANECHOIC Main Skill `ca` for methodology-defined Workflow execution and MCP Step instructions and results.

## Claim

FRAMEWORK_ENGINE **must** provide `ca` as the primary Skill entry point through which Operators **and** AI Agents submit requests **to** methodology-defined Workflow execution **and** exchange current Step instructions **and** results through MCP.

the Skill remains within the thin-wrapper boundary of CA-R-1626-SKILLS-RULE--keep-ca-and-specialist-skills-thin; WORKFLOW_ORCHESTRATOR retains coordination under CA-R-1522-WORKFLOW_ORCHESTRATOR-RULE--provide-workflow-orchestration-from-methodology rather than transferring route selection **or** Step sequencing into the Skill.

