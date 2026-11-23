---
atom_family: SPEC
atom_id: AN-S-1580
container:
  component: C24
tier: 3
context:
  lens: DevOps
state:
  status: archived
  version: 3
  updated_at: 2026-10-24 00:38:25 +0400
---
## Summary

Deliver the implementation prompt input packet

# Summary

Deliver the implementation prompt input packet

## Scope

the invocation packet passed to one current Implementation Workflow prompt.

## Claim

the packet **must** carry current Workflow/Step/Action pins, P/DoD and owned paths, R/D targets, the verified active-M file, E checks, authority, permissions, confidence, retry accounting, assigned context, retained evidence, and Step-specific input.

## Details

Preparation may begin from a bounded request plus admitted authority, but it must produce or verify the M file before delegated work. A missing field produces the Step's blocked result.
