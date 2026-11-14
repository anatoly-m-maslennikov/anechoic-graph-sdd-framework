---
atom_id: CA-R-1117
ref_id: CA-R-1117@24-draft
container:
  scope_unit: CA-SU-21
role: Requirement
form: Rule
topics:
  main_subject: PROJECT STRUCTURE//CAPRMEDIO <+ Aspects <+ Engineering <+ Operation
    <+ Execution Control <+ Resource Limits
tier: 1
status: draft
version: 24
updated_at: '2026-11-14T08:28:16.789841+00:00'
llm_session_ids:
- codex:01a01cb6-4ee4-7553-b68d-0823dda35094
- codex:01a02650-eff7-7453-8c37-0699b36773c6
author: Anatoly Maslennikov
current_scope_unit: MCP
carrier_destination:
  file:
    name: CA-R-1117@24-draft-MCP-RULE--bound-and-control-mcp-requests.md
    path: .caprmedio_caprmedio/CA-SU-14_LAYER_2_FRAMEWORK_ENGINE/CA-SU-15_FEATURE_PROGRAMMATIC/CA-SU-21_FEATURE_MCP/04_requirement/000_draft
relations:
  IS_REPLACEMENT_FOR:
  - CA-R-1117
  - CA-M-179
---
## Summary

Bound and control MCP requests

## Claim

### Prose Claim

Before Tool dispatch, validate every admitted MCP message against its schema and set declared time and resource bounds.
MCP supports cancellation and reports progress only for admitted long-running operations.
Each request has an explicit admission and completion boundary.

## Details

- Reject invalid or expired requests before dispatch.
- End invalid, expired, canceled, or resource-exhausted requests with a structured outcome.
  Preserve Tool and Project state and stop ungoverned background work.
