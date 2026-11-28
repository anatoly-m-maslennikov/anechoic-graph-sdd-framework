---
atom_family: SPEC
atom_id: AN-S-5191
container:
  component: C67
tier: 1
context:
  lens: SWD/INTERNAL_API/IPC
state:
  status: active
  version: 2
  updated_at: "2026-11-28T15:16:37.698017+00:00"
---

## Summary

Return the accepted Model or Structure to a private peer

## Claim

For a request bound to the Kernel's Project instance, serve the accepted Model or Structure
bytes with their generation ID. Before admission, report that no generation
is available. Reject a request for another instance.
