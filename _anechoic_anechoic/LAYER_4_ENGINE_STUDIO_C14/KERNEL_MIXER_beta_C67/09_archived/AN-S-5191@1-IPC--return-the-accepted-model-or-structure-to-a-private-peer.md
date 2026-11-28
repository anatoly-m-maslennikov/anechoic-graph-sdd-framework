---
atom_family: SPEC
atom_id: AN-S-5191
container:
  component: C67
tier: 1
context:
  lens: IO/API/IPC
state:
  status: archived
  version: 1
  updated_at: '2026-11-27T18:25:19.396090+00:00'
---

## Summary

Return the accepted Model or Structure to a private peer

## Claim

For a request bound to the Kernel's Project instance, serve the accepted Model or Structure
bytes with their generation ID. Before admission, report that no generation
is available. Reject a request for another instance.
