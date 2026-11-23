---
atom_family: SPEC
atom_id: AN-S-3719
container:
  component: C20
tier: 3
context:
  lens: QA
state:
  status: archived
  version: 5
  updated_at: 2026-10-24 00:51:05 +0400
---
## Summary

verify Agent container isolation

# Summary

verify Agent container isolation

## Scope

the Docker Agent service's admission **and** filesystem boundaries.

## Claim

the Evaluation **must** verify that an isolated Agent can return proposals but cannot access host Project Carriers **or** runtime-control capabilities.

## Details

- inspect the resolved configuration: Agent has no Project, host-home **or** Docker socket mount, no published port, no privileged mode **and** no added capabilities.
- test rejected unknown fields, invalid phases, oversized requests, concurrent dispatch **and** invalid structured output.
- verify denied Project write probes **and** absence of credential files from image layers **and** public outputs.
- verify missing credentials produce an explicit readiness failure **without** starting a real Workflow.
