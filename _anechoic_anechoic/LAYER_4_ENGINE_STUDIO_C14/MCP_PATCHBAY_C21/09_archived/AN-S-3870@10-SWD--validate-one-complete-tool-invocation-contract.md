---
atom_family: SPEC
atom_id: AN-S-3870
container:
  component: C21
tier: 4
context:
  lens: SWD
state:
  status: archived
  version: 10
  updated_at: 2026-10-24 00:51:05 +0400
---
## Summary

Validate one complete Tool invocation contract

# Validate one complete Tool invocation contract

## Applicable when

Apply **before** MCP exposes one Tool descriptor.

## Procedure

1. Call the Tool's canonical `describe_tool()` implementation and validate it against `CA-D-621-TOOLS-DELIVERY--encode-uniform-tool-self-description`.
2. Resolve model symbols and the provider adapter only from trusted installed Engine code; derive schemas from the canonical models and validate every descriptor field against the same Tool identity.
3. Reject a handwritten duplicate schema, missing field, conflicting field, ambiguous binding, or unresolved callable entrypoint; return field-level diagnostics without repairing, reinterpreting, importing untrusted code, or invoking the Tool.

## Outcome

One complete canonical descriptor is eligible for MCP projection, or that descriptor is quarantined as unavailable.

## Failure or stop

Stop exposure of **that** descriptor **when** **any** contract field is missing, conflicting, ambiguous, handwritten as a second schema, or unresolved.
