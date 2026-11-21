---
atom_family: SPEC
atom_id: AN-S-1410
structure:
  container:
    component: C21
  tier: 3
context:
  lens: QA
state:
  status: active
  version: 3
  updated_at: 2026-11-10 20:47:54 +0400
---
## Summary

Expose only generated MCP registration entries

## Claim

### Prose Claim

Verify that MCP registration loads only installed code-owned provider entries from the generated registration asset. Helper modules and native Atom, Scope Unit or Tool folders do not select exposure.

## Details

Load an asset with an enabled provider, disabled configured entry and unlisted helper: only the enabled entry is exposed and the other dispositions are explicit. Missing or malformed configuration reports explicitly without native-source fallback. Verify that an installed registered Tool on the global exact-name `mcp_blacklist` is absent from tools/list and direct invocation rejects before provider dispatch; Project settings cannot re-enable it. Add a provider to prove admission follows generated configuration, not a gateway allowlist.
