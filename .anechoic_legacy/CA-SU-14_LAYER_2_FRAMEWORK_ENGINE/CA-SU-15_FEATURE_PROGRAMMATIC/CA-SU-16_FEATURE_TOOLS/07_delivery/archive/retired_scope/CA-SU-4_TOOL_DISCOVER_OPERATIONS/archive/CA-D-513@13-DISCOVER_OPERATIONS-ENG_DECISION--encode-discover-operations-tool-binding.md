---
atom_id: CA-D-513@13
content_role: Delivery
current_scope_unit: DISCOVER_OPERATIONS
status: Archived
author: Anatoly Maslennikov
version: 13
updated_at: 2026-10-27 19:59:26 +0400
subjects:
  governs: Subject/ANECHOIC/Graph/Node/Aspect/Engineering/Architecture/Communication
  depends_on:
  - Subject/ANECHOIC/Graph/Node/Aspect/Engineering/Data Handling/Serialization
  - 'Subject/ANECHOIC/Graph/Node/Project Model/Atom/Content Role: Operations/Type: Action'
  - 'Subject/ANECHOIC/Graph/Node/Project Model/Atom/Content Role: Operations/Type: Workflow'
  - Subject/ANECHOIC/Graph/Node/Project Model/Atom
  - Subject/ANECHOIC/Graph/Node/Project Model/Scope Unit
  - Subject/ANECHOIC/Graph/Node/Project Model/Execution/Workflow Run
  - Subject/ANECHOIC/Graph/Node/Project Model/History/Journal
relations: {}
type: Eng Decision
tier: 3
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
entrypoint = "102_FRAMEWORK_ENGINE/201_PROGRAMMATIC/201_TOOLS/DISCOVER_OPERATIONS/discover_operations.py"
action_ids = ["CA-O-113"]
mcp_name = "discover_operations"
```

- the MCP boundary exposes the Implementation's strict input schema. unknown fields **and** invalid selectors are explicit errors.
- return repository-relative source paths **and** SHA-256 bindings. full content is loaded **only** **when** requested.
- observation cursors bind the Run ID, saved Event frontier **and** saved status fingerprint; a cursor from another Run is invalid.
