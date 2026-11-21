---
atom_family: SPEC
atom_id: AN-S-1401
container:
  component: C21
tier: 3
context:
  lens: QA
state:
  status: active
  version: 20
  updated_at: 2026-11-10 20:47:54 +0400
---

## Summary

Rebuild one unchanged MCP registry identically

## Claim

### Prose Claim

Verify that rebuilding MCP registration from unchanged installed provider code, code-owned inventory and configuration yields the same callable identities and schemas. Volatile execution metadata does not change registration.

## Details

### Test case

Generate the registry twice from the same installed provider code, code-owned inventory and configuration.

### Acceptance criteria

the two registries have the same capability identities **and** schemas; volatile execution metadata does **not** change that result.

### Failure disposition

Stop publication **and** report the first nondeterministic configured entry or ordering defect.
