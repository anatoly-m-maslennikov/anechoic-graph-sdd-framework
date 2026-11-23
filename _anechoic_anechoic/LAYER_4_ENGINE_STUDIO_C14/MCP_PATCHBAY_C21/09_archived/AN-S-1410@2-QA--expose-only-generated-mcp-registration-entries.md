---
atom_family: SPEC
atom_id: AN-S-1410
container:
  component: C21
tier: 3
context:
  lens: QA
state:
  status: archived
  version: 2
  updated_at: 2026-11-09 21:15:45 +0400
---

## Summary

Expose only generated MCP registration entries

## Claim

### Prose Claim

Verify that MCP registration loads only installed code-owned provider entries from the generated registration asset. Helper modules and native Atom, Scope Unit or Tool folders do not select exposure.

## Details

Load a generated asset containing an enabled provider, a disabled configured entry and an unlisted helper. Only the enabled configured entry is exposed; the other dispositions are explicit. Missing or malformed registration configuration is reported without falling back to native source discovery.

Cover an installed registered Tool on the explicit global `mcp_blacklist`: its descriptor is absent from tools/list and direct invocation is rejected before provider dispatch. A Project setting cannot re-enable it. Repeat with a newly added provider to prove admission follows the generated configuration rather than a hardcoded gateway allowlist.
