---
atom_id: CA-D-513
ref_id: CA-D-513
container:
  scope_unit: CA-SU-16
role: Delivery
form: Eng Decision
topics:
  main_subject: Subject/ANECHOIC/Graph/Node/Aspect/Engineering/Development/Architecture/Communication
  dependencies:
  - Subject/ANECHOIC/Graph/Node/Aspect/Engineering/Operation/Data Handling/Serialization
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
    name: CA-D-513@14-DISCOVER_OPERATIONS-ENG_DECISION--encode-discover-operations-tool-binding.md
    path: .anechoic_anechoic/CA-SU-14_LAYER_2_FRAMEWORK_ENGINE/CA-SU-15_FEATURE_PROGRAMMATIC/CA-SU-16_FEATURE_TOOLS/07_delivery/archive/retired_scope/CA-SU-4_TOOL_DISCOVER_OPERATIONS
current_scope_unit: TOOLS
author: Anatoly Maslennikov
---
# Summary

Encode DISCOVER_OPERATIONS Tool binding

## Scope

the DISCOVER_OPERATIONS capability for Tool/DISCOVER_OPERATIONS/Carrier.

## Claim

the DISCOVER_OPERATIONS Tool binding **must** be carried **in** the following TOML table **in** this Atom's Details, with JSON request **and** response Carriers.

## Details

accept a query, Workflow or Action kind, Scope Unit and execution-kind filters, offset, and result limit; return summaries, definition bindings, and implementation availability.

```toml
[tool_binding]
name = "DISCOVER_OPERATIONS"
entrypoint = "LAYER_2_FRAMEWORK_ENGINE/FEATURE_PROGRAMMATIC/FEATURE_TOOLS/TOOL_DISCOVER_OPERATIONS/discover_operations.py"
action_ids = ["CA-O-113"]
mcp_name = "discover_operations"
```

- the MCP boundary exposes the Implementation's strict input schema. unknown fields **and** invalid selectors are explicit errors.
- return repository-relative source paths **and** SHA-256 bindings. full content is loaded **only** **when** requested.
- observation cursors bind the Run ID, saved Event frontier **and** saved status fingerprint; a cursor from another Run is invalid.
