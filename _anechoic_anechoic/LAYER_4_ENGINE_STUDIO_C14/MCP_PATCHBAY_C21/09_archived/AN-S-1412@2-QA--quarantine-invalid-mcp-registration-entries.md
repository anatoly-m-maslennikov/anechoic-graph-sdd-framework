---
atom_family: SPEC
atom_id: AN-S-1412
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

Quarantine invalid MCP registration entries

## Claim

### Prose Claim

Verify that an invalid descriptor is quarantined with an explicit diagnostic while independently valid descriptors publish. Unresolved generator integrity or the common activated descriptor frontier stops publication.

## Details

Introduce one invalid descriptor alongside an independent valid descriptor. Report and quarantine the invalid one and publish the valid one. Separately verify that a broken generator or unresolved common descriptor frontier prevents activation.
