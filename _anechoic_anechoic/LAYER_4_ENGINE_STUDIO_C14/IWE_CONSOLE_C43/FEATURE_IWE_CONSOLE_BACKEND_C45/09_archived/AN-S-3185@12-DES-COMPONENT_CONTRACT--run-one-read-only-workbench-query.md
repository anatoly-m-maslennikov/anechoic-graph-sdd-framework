---
atom_family: SPEC
atom_id: AN-S-3185
container:
  component: C45
tier: 0
context:
  template: component_contract
  lens: DES
relations:
  ANSWERS:
  - AN-S-3059
state:
  status: "archived"
  version: 12
  updated_at: "2026-11-26T15:54:01.282167+00:00"
---

## Summary

Run one read-only Workbench query

## Guarantee

Given a complete SQL string and valid result options, execute one read-only
query against the selected Project's Workbench data. Treat the optional
cursor position as editor metadata.

Return result metadata with an inline page or a result file according to
the requested delivery mode and result format. Omit the SQL text from
the result. Reject invalid inputs and report query execution failures.

## Tool API

Publish the enabled Tool names, descriptions, and schemas for an admitted
Project. Use the same registry to validate and dispatch named calls.
Return the Tool result or a failure for a stale registry, disabled Tool,
or invalid request.

For `POST /tools`, return HTTP 200 with the result when the operation succeeds.
Return HTTP 400 with a typed error for invalid request input. Return HTTP 500
with a typed, sanitized error for an internal fault that prevents handling the
request. An accepted input can still fail during operation. Do not classify
other failures as HTTP 400.

### Formal Claim

This small claim checks only the three Tool API transport cases and the result
or typed-error response kind. It does not model message sanitization or the
complete response schema.

```lean
namespace WorkbenchToolApi

inductive Classification where
  | acceptedOperation
  | invalidRequestInput
  | internalFault
  deriving DecidableEq

inductive ResponseKind where
  | result
  | typedError
  deriving DecidableEq

def accepts (code : Nat) (classification : Classification)
    (kind : ResponseKind) : Bool :=
  match code, classification, kind with
  | 200, .acceptedOperation, .result => true
  | 400, .invalidRequestInput, .typedError => true
  | 500, .internalFault, .typedError => true
  | _, _, _ => false

example : accepts 200 .acceptedOperation .result = true := by decide
example : accepts 400 .invalidRequestInput .typedError = true := by decide
example : accepts 500 .internalFault .typedError = true := by decide
example : accepts 200 .acceptedOperation .typedError = false := by decide
example : accepts 400 .invalidRequestInput .result = false := by decide
example : accepts 400 .internalFault .typedError = false := by decide

end WorkbenchToolApi
```

## Process boundary

Resolve the requested Project and return its Manifest pin and verified
host binding without opening DuckDB. Return its normalized Tool blacklist and
release workflow enablement.

Serve one admitted Project per Backend process over a private Unix
socket. Check the Project Manifest revision and instance identity before
readiness. Validate named Workbench operations in the Backend and call
the Project's Kernel to execute queries and publish lifecycle updates.
When release workflows are enabled, revalidate the Project Manifest pin and
return the host command for the declared local or public Release entrypoint.

Use the Project Manifest's storage settings first, then the host
defaults. The caller owns the process lifetime and closes it when the
Project leaves the pool or the caller exits.

## Shared host

The Backend coordinator reads the host settings, resolves explicit Project
roots, and publishes the compatible Tool catalog. It routes a named call
only to its selected Project. It holds a bounded pool of Project Backend
processes and closes them on eviction or shutdown.

MCP uses the private Unix socket for status, selection, catalog, and calls.
The configured host settings must remain current for Project calls.

## References

AN-S-1456, AN-S-2566, AN-S-3059, and AN-T-2947.
