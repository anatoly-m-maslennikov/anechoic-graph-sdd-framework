---
atom_family: SPEC
atom_id: AN-S-4271
container:
  component: C16
tier: 3
context:
  lens: DES
state:
  status: archived
  version: 13
  updated_at: 2026-11-05 14:23:38 +0400
---
## Summary

Find Tools by capability

# Summary

Find Tools by capability

## Scope

the DISCOVER_TOOLS capability for Tool/DISCOVER_TOOLS.

## Claim

For a non-empty request, the DISCOVER_TOOLS Tool **must** return a ranked, bounded selection of Tools matching the requested capability and filters, with exact source references and observed availability.

## Details

- implement the methodology Action CA-O-112-PROJECT_CONFIGURATION-ACTION--find-tools-by-capability.
- accept a query, Scope Unit and availability filters, offset, and result limit; return compact matches, total matches, next offset, catalog fingerprint, and coverage diagnostics.
- preserve the Operator's choice of what **to** execute; discovery, context retrieval, **and** observation provide capabilities.
- bounded **or** unavailable evidence **must** remain explicit **rather than** establish a successful assessment.

An empty request returns the generated released-MCP root catalog with root tools, Queries, Views and Service groups and actual MCP descriptors. Non-empty requests retain the ranked, bounded source-binding search with its existing filters and result fields. These are distinct result contracts; do not invent source references for native descriptors.
