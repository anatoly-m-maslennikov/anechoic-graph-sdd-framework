---
atom_family: SPEC
atom_id: AN-S-4273
container:
  component: C16
tier: 3
context:
  lens: DevOps
state:
  status: archived
  version: 15
  updated_at: 2026-11-05 13:04:02 +0400
---
## Summary

Encode DISCOVER_TOOLS Tool binding

# Summary

Encode DISCOVER_TOOLS Tool binding

## Scope

the DISCOVER_TOOLS capability for Tool/DISCOVER_TOOLS/Carrier.

## Claim

the DISCOVER_TOOLS Tool binding **must** be carried **in** the following TOML table **in** this Atom's Details, with JSON request **and** response Carriers.

## Details

accept a query, Scope Unit and availability filters, offset, and result limit; return compact matches, total matches, next offset, catalog fingerprint, and coverage diagnostics.

```toml
[tool_binding]
name = "DISCOVER_TOOLS"
entrypoint = "LAYER_2_FRAMEWORK_ENGINE/FEATURE_PROGRAMMATIC/FEATURE_TOOLS/TOOL_DISCOVER_TOOLS/discover_tools.py"
action_ids = ["CA-O-112"]
mcp_name = "discover_tools"
```

- the MCP boundary exposes the Implementation's strict input schema. unknown fields **and** invalid selectors are explicit errors.
- return repository-relative source paths **and** SHA-256 bindings. full content is loaded **only** **when** requested.
- observation cursors bind the Run ID, saved Event frontier **and** saved status fingerprint; a cursor from another Run is invalid.

## Root MCP catalog

An empty `request` returns the generated root catalog carried by CA-D-678. It contains `root`, `groups` and `updated_at`, and uses the actual released MCP names, descriptions, schemas and annotations. The root entry is `discover_tools`; groups are Queries, Worksheets and Service. Missing or invalid generated data is an explicit error. The existing explicit query, Scope Unit, availability, offset and limit selectors retain their source-binding search contract. Native descriptors do not acquire invented source paths, SHA-256 bindings or executable status from folder names.
