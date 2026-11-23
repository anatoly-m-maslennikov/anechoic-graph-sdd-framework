---
atom_family: SPEC
atom_id: AN-S-1934
container:
  component: C21
tier: 4
context:
  lens: QA
state:
  status: "archived"
  version: 5
  updated_at: "2026-11-23T01:48:06.183139+00:00"
---
## Summary

Verify code-owned MCP registration without Atom discovery

## Claim

### Prose Claim

Generate the MCP registration asset from installed provider code and code-owned inventory; unchanged inputs produce identical bytes, while provider add/remove/descriptor changes are reflected and unlisted helpers are not exposed.

Start MCP against a Project root without a native Atom tree while making Atom-catalog and selected-source registration reads fail if called: tools/list and a code-only Tool call still work, unrelated Atom edits do not change exposure, and operation validation still rejects missing business prerequisites. Cover malformed/missing config, duplicate public names, configured exclusions, unavailable/changed provider code, source-only descriptors, typed request/result rejection, and Workbench native tools; no registration test bypasses an operation boundary.

Verify refresh mode generates before package identity and stops on generation failure. Verify existing mode carries the checkout registry bytes unchanged. Verify package and image identity in both modes. Compare tools/list after global blacklist and Project exclusions. Compare unprofiled startup time/memory with the prior same-source image without inferring permanent RSS savings from estimates.

Equivalent MCP/web requests delegate to the same backend and preserve response/error semantics; the wrapper may translate protocol data but adds no business implementation or internal HTTP transport. Cover single/shared Project parity, binding rejection, cancellation lease release, normal/partial-save/query-error/health meanings, and shared HTTP Workbench calls reaching the native backend without constructing MCP request/result envelopes. Add/modify a code-only provider through inventory/generation without gateway edits; verify descriptors/calls, blacklist omission and direct-call refusal, Project exclusions, and absence of retired discovery/route/orchestrator adapters.
