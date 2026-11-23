---
atom_family: SPEC
atom_id: AN-S-1396
container:
  component: C21
tier: 3
context:
  lens: QA
state:
  status: archived
  version: 16
  updated_at: 2026-10-27 06:04:45 +0400
---
## Summary

Reject one incomplete Tool invocation contract

# Reject one incomplete Tool invocation contract

## Claim checked

MCP exposes **only** a complete coherent canonical descriptor with `schema_version: 1`.

## Test case

Validate one Tool descriptor missing a required CA-D-621 field beside one complete Tool descriptor. Repeat with a handwritten duplicate input schema, an unresolved callable entrypoint, and a missing Action binding.

## Acceptance criteria

The defective Tool returns a field-level unavailable diagnostic and produces no eligible projection. The independent complete Tool remains eligible. The harness proves models are imported from canonical symbols and that validation never invokes or applies either Tool.

## Failure disposition

Stop exposure of the affected descriptor **until** its contract is complete, canonical-model-derived, **and** unambiguous.
