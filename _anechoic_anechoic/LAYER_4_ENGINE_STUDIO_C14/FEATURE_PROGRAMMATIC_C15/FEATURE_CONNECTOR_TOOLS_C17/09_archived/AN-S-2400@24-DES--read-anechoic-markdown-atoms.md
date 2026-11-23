---
atom_family: SPEC
atom_id: AN-S-2400
container:
  component: C17
tier: 3
context:
  lens: DES
state:
  status: archived
  version: 24
  updated_at: 2026-10-26 00:46:35 +0400
---
## Summary

Read ANECHOIC Markdown Atoms

# Summary

Read ANECHOIC Markdown Atoms

## Scope

Explicit logical source reads by the ATOM_READ connector, including its Markdown storage binding.

## Claim

The ATOM_READ connector **must** execute `read` for one explicit logical target through CA-R-1936-CONNECTOR_TOOLS-RULE--use-one-coherent-connector-interface and CA-D-625-CONNECTOR_TOOLS-CORE-DELIVERY--deliver-coherent-connector-interface, independently of Find or Modify. Return the complete admitted logical source data and its actual identity, exact Version where applicable, and current source-state token or pin. Explicit admitted projection views may narrow returned data without inventing a different source or lifecycle.

Read by explicit logical ID **must not** require a caller-known Version. The caller may supply exact expected state for a pinned or historical Read; then the connector must enforce an exact match. The target and supplied context determine the current original or explicitly requested historical source view. Missing or ambiguous view/target resolution, stale supplied expectations, malformed source data or missing applicable read permission must return a structured refusal rather than silently selecting another version or lifecycle.

The connector resolves storage and serialization internally and returns the admitted source representation; it does not allocate identity, change Version, select lifecycle policy or produce a write. Do not expose a path, filename, database table or query language as the logical target contract.

## Details

CA-O-047, CA-E-302 and CA-D-423 govern this primitive's Action, checks and data representation. The physical code binding under `102_FRAMEWORK_ENGINE/201_PROGRAMMATIC/201_TOOLS/ATOM_READ/` is unchanged. This required interface does not claim runtime implementation or connected-MCP acceptance.
