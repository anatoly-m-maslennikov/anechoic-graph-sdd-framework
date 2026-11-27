---
atom_family: SPEC
atom_id: AN-S-2
container:
  component: C16
tier: 5
context:
  lens: DevOps
state:
  status: active
  version: 14
  updated_at: "2026-11-27T17:35:01.150345+00:00"
---
# Summary

Bind REVERT_CHANGES delivery boundaries

## Scope

The delivery boundary between REVERT_CHANGES, governed reversal capabilities, and shared Run/Journal support.

## Claim

Deliver admitted reversal under AN-S-147 and AN-S-37. Preserve the shared Journal serialization ownership.

## Details

Implementation belongs at the CA-D-536 entrypoint with functional mocks under the same Tool package. It calls supported governed effect capabilities only after admission/currentness checks; it never replaces CA-O-131's semantics, deletes history, performs a Git reset, or implements an internal failure rollback. It passes exact Run/Step/Action identity and evidence references to existing shared Run support and retains actual Run observations and logging diagnostics. Plain Journal append/read is independent observation, not a permission or source-effect completion gate; no durable/pending receipt, logging retry or recovery channel is required or exposed. Actual Run-start failure blocks before effects, and actual Run-terminal failure preserves observed effects and reports its error without claiming terminal persistence. Logging failure does not downgrade an independently completed reversal or authorize effect replay.

Apply AN-S-5178 to the real MCP acceptance boundary. This RMED carrier authorizes no code before independent RMED review and no runtime-success claim.
