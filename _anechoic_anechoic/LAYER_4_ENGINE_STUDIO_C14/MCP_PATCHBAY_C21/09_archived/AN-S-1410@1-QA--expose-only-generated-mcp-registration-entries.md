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
  version: 1
  updated_at: 2026-11-09 07:45:15 +0400
---

## Summary


Expose only generated MCP registration entries

## Claim

### Prose Claim

Verify that MCP registration loads only installed code-owned provider and selected-route entries from the generated registration asset. Helper modules and native Atom, Scope Unit or Tool folders do not select exposure.

## Details

Load a generated asset containing an enabled provider, a disabled configured entry and an unlisted helper. Only the enabled configured entry is exposed; the other dispositions are explicit. Missing or malformed registration configuration is reported without falling back to native source discovery.
