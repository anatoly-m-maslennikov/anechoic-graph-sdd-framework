---
atom_family: SPEC
atom_id: AN-S-1934
container:
  component: C21
tier: 4
context:
  lens: QA
state:
  status: archived
  version: 1
  updated_at: 2026-11-07 13:08:03 +0400
---

## Summary

Verify code-owned MCP registration without Atom discovery

## Claim

### Prose Claim

Generate the MCP registration asset from installed provider code and code-owned inventory. Repeat with unchanged inputs and compare bytes. A provider addition, removal or descriptor/code change is reflected after generation; unlisted helper modules do not become exposed tools.

Start MCP against a Project root without a native Atom tree while making Atom catalog and selected-source manifest registration reads fail if called. Tool listing and a code-only test Tool call still work. Editing or removing an unrelated Atom does not change exposure or cause a generic registration freshness scan. Actual operation-level validation still rejects a request whose business prerequisites are missing.

Cover missing/malformed config, duplicate public names, configured exclusions, unavailable/changed provider code, source-only descriptors, typed request/result rejection, Workbench native tools and preserved selected-route protocols. No registration test grants permission to bypass an operation boundary.

Verify local release generates the asset before package identity/image startup, includes its bytes in package verification and stops before startup on generator failure. Verify the Dockerfile regenerates it on rebuild. Keep post-readiness discovery output separate and accurate. Compare unprofiled startup time and process memory with the prior same-source image; do not infer a permanent RSS saving from allocation estimates.

Verify equivalent MCP and web requests delegate to the same existing backend operation and preserve its response/error semantics. The MCP registration wrapper may validate and translate protocol data but must not introduce a second business implementation or extra internal HTTP transport.

Cover single-Project and shared-Project HTTP/MCP backend parity. Shared HTTP Workbench calls must reach the same native backend without constructing MCP request/result envelopes. Missing, foreign, stale or disabled Project/tool bindings remain rejected; cancellation releases its owner lease; normal results, partial-save outcomes, query errors and health observations retain their existing meaning.
