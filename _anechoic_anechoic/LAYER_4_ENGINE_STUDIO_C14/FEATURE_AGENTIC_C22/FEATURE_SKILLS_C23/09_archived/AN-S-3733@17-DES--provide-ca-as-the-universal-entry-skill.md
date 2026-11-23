---
atom_family: SPEC
atom_id: AN-S-3733
container:
  component: C23
tier: 3
context:
  lens: DES
state:
  status: archived
  version: 17
  updated_at: 2026-10-26 00:46:35 +0400
---
## Summary

Provide CA as the universal entry skill

# Summary

Provide CA as the universal entry skill

## Scope

requests submitted by Operators and AI Agents through the ANECHOIC Main Skill `ca` for methodology-defined Workflow execution and MCP Step instructions and results.

## Claim

FRAMEWORK_ENGINE **must** provide `ca` as the primary Skill entry point through which Operators **and** AI Agents submit requests **to** methodology-defined Workflow execution **and** exchange current Step instructions **and** results through MCP.

the Skill remains within the thin-wrapper boundary of CA-R-1626-SKILLS-RULE--keep-ca-and-specialist-skills-thin; WORKFLOW_ORCHESTRATOR retains coordination under CA-R-1522-WORKFLOW_ORCHESTRATOR-RULE--provide-workflow-orchestration-from-methodology rather than transferring route selection **or** Step sequencing into the Skill.

## Details
