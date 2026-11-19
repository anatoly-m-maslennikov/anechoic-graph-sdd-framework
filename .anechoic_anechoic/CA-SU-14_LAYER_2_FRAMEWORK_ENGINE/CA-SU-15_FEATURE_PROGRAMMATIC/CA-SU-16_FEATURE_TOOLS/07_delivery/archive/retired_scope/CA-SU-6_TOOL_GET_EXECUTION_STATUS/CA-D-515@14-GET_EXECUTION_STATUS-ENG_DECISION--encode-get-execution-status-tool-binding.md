---
atom_id: CA-D-515
ref_id: CA-D-515
container:
  scope_unit: CA-SU-16
role: Delivery
form: Eng Decision
topics:
  main_subject: Subject/ANECHOIC/Graph/Node/Aspect/Engineering/Operation/Data Handling/Serialization
  dependencies:
  - 'Subject/ANECHOIC/Graph/Node/Project Model/Atom/Content Role: Operations/Type:
    Action'
  - 'Subject/ANECHOIC/Graph/Node/Project Model/Atom/Content Role: Operations/Type:
    Workflow'
  - Subject/ANECHOIC/Graph/Node/Project Model/Atom
  - Subject/ANECHOIC/Graph/Node/Project Model/Scope Unit
  - Subject/ANECHOIC/Graph/Node/Project Model/Execution/Workflow Run
  - Subject/ANECHOIC/Graph/Node/Project Model/History/Journal
tier: 3
status: Archived
version: 14
updated_at: 2026-11-02 19:46:47 +0400
carrier_destination:
  file:
    name: CA-D-515@14-GET_EXECUTION_STATUS-ENG_DECISION--encode-get-execution-status-tool-binding.md
    path: .anechoic_anechoic/CA-SU-14_LAYER_2_FRAMEWORK_ENGINE/CA-SU-15_FEATURE_PROGRAMMATIC/CA-SU-16_FEATURE_TOOLS/07_delivery/archive/retired_scope/CA-SU-6_TOOL_GET_EXECUTION_STATUS
current_scope_unit: TOOLS
author: Anatoly Maslennikov
---
# Summary

Encode GET_EXECUTION_STATUS Tool binding

## Scope

the GET_EXECUTION_STATUS capability for Tool/GET_EXECUTION_STATUS/Carrier.

## Claim

the GET_EXECUTION_STATUS Tool binding **must** be carried **in** the following TOML table **in** this Atom's Details, with JSON request **and** response Carriers.

## Details

accept a supported Run ID, optional Action ID and selection ordinal, and whether full saved results are requested; return status, output, results, progress, recording blockers, and report references.

```toml
[tool_binding]
name = "GET_EXECUTION_STATUS"
entrypoint = "LAYER_2_FRAMEWORK_ENGINE/FEATURE_PROGRAMMATIC/FEATURE_TOOLS/TOOL_GET_EXECUTION_STATUS/get_execution_status.py"
action_ids = ["CA-O-115"]
mcp_name = "get_execution_status"
```

- the MCP boundary exposes the Implementation's strict input schema. unknown fields **and** invalid selectors are explicit errors.
- return repository-relative source paths **and** SHA-256 bindings. full content is loaded **only** **when** requested.
- observation cursors bind the Run ID, saved Event frontier **and** saved status fingerprint; a cursor from another Run is invalid.
