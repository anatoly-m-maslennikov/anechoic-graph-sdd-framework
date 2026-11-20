---
atom_id: CA-R-1117
ref_id: CA-R-1117@23-draft
container:
  scope_unit: CA-SU-21
role: Requirement
form: Rule
topics:
  main_subject: PROJECT STRUCTURE//ANECHOIC <+ Aspects <+ Engineering <+ Operation
    <+ Execution Control <+ Resource Limits
tier: 1
status: draft
version: 23
updated_at: '2026-11-14T08:20:17.954130+00:00'
llm_session_ids:
- codex:01a01cb6-4ee4-7553-b68d-0823dda35094
- codex:01a02650-eff7-7453-8c37-0699b36773c6
author: Anatoly Maslennikov
current_scope_unit: MCP
carrier_destination:
  file:
    name: CA-R-1117@23-draft-MCP-RULE--bound-and-control-mcp-requests.md
    path: .anechoic_anechoic/CA-SU-14_LAYER_2_FRAMEWORK_ENGINE/CA-SU-15_FEATURE_PROGRAMMATIC/CA-SU-21_FEATURE_MCP/04_requirement/000_draft
relations:
  IS_REPLACEMENT_FOR:
  - CA-R-1117
  - CA-M-179
---
## Summary

Bound and control MCP requests

## Claim

### Prose Claim

MCP must validate each request before dispatch, apply declared time and resource
bounds, and report progress only for admitted long-running work. Invalid, expired,
canceled, and exhausted requests end with a structured outcome.

## Details

- Reject invalid or expired requests before dispatch. Validate messages
  against the admitted protocol schema.
- Support cancellation. Preserve Tool and Project state on termination
  and leave no ungoverned background work.

### Sources

- [MCP base protocol](https://modelcontextprotocol.io/specification/2025-06-18/basic/index)
  and [MCP tasks](https://modelcontextprotocol.io/specification/2025-11-25/basic/utilities/tasks).
- [CA-A-057](../../../02_analysis_and_advisory/CA-A-057-PROGRAMMATIC-ANALYSIS_RPRT--reconcile-programmatic-specialization-authority.md).
