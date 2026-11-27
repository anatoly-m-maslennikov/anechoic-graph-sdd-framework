---
atom_family: SPEC
atom_id: AN-S-1252
container:
  component: C15
tier: 2
context:
  lens: SWD
state:
  status: "active"
  version: 18
  updated_at: "2026-11-27T15:10:44.706424+00:00"
---

## Summary

Make failures observable without disabling healthy runtime

## Claim

### Prose Claim

Classify each observed failure by its actual impact. Expose it through the affected operation's output or runtime failure boundary, and keep a healthy runtime available. Reserve blocking runtime failure and technical ERROR for a genuine failure that prevents the affected runtime component from safely operating.

## Details

Apply to new or changed PROGRAMMATIC implementations, including Tools, Apps, MCP adapters, and their public operation boundaries. The shared boundary also covers PROGRAMMATIC public operation and process execution boundaries, including all first-party Tools, Workflows, Apps, MCP adapters, service entrypoints, and background executors shipped in a delivered Docker image. It is not limited to AtomSearch, MCP-mediated invocation, or a running container.

Derive coverage from image entrypoints, executable modes, and actual dispatch owners. Cover direct, worker, and service execution; reuse existing package inventories and do not create a competing registry or modify third-party internals.

Do not swallow exceptions or diagnostic errors, turn failure into empty success, or continue without an observable failure. Report a failed diagnostic through a still-usable output without hiding the primary outcome. An unexpected failure remains visible. A verified process-startup or runtime failure may terminate the affected process; a failed request or business Workflow does not itself establish a broken runtime.

Treat invalid requests and malformed, missing, stale, ambiguous, or otherwise unusable Project artifacts or bindings as operation-local failures. Emit a sanitized WARNING and return an attributable caller-visible error, including for an all-invalid result. Never use ERROR for those conditions or classify them from a `RuntimeError` name, another exception base class, or arbitrary message text. Use the applicable contract's structured type, code, and state. Explanatory text such as “restart required” does not establish unavailable state or another failure class.

Return a stable error code, safe explanation, and affected logical target or safe Project-relative path when known. Logs alone are not the error answer. Validate invalid arguments before effects and preserve the prior observable state on rejection. Refuse unsafe or unauthorized effects at their boundary. Continue only independently safe, authorized work; do not substitute a Project, repair input, bypass a guard, or implicitly retry. This policy does not bypass validation, authorization, source binding, or effect safety.

Reuse one transport-neutral failure-handling owner at each relevant public execution boundary, through a decorator or equivalent shared wrapper, not around every helper. The owner classifies known failures, emits diagnostics under CA-M-396/CA-M-399, and uses the caller's declared result/error adapter. Do not invent a competing domain model or undocumented universal envelope. Keep transport encoding in its adapter, business lifecycle recording with the Workflow executor, and use established logging and execution/validation owners.

Support synchronous and asynchronous operations while preserving callable signatures, metadata, await behavior, and cancellation. Do not turn cancellation, shutdown, or interrupt into success. Apply the boundary once at its execution owner. Registration and discovery remain effect-free. Generic handling does not start Workflows, append Journals, retry, repair, roll back, or replay business work.

Under CA-M-405, the operation owner supplies verified completed data, effects, and error context. Preserve completed data under the applicable public result contract. Pass structured partial or failed outcomes through without erasing data, duplicating diagnostics, or reclassifying Project artifact problems as runtime failure. Request error and technical log severity are separate; a failed or partial request may be WARNING while runtime remains healthy.
