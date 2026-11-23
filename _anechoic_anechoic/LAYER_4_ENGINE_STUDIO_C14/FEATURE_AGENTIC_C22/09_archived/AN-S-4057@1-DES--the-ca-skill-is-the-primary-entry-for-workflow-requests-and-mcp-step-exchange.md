---
atom_family: SPEC
atom_id: AN-S-4057
container:
  component: C22
tier: 3
context:
  lens: DES
state:
  status: archived
  version: 1
  updated_at: 2026-10-29 23:57:07 +0400
---
## Summary

The ca Skill is the primary entry for Workflow requests and MCP Step exchange

## Claim scope

requests submitted by Operators and AI Agents through the ANECHOIC Main Skill `ca` for methodology-defined Workflow execution and MCP Step instructions and results.

## Claim

FRAMEWORK_ENGINE **must** provide `ca` as the primary Skill entry point through which Operators **and** AI Agents:

- submit requests **to** methodology-defined Workflow execution; **and**
- exchange current Step instructions **and** results through MCP.
