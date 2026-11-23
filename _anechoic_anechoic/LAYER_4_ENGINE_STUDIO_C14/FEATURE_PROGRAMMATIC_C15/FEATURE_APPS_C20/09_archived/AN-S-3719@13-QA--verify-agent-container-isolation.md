---
atom_family: SPEC
atom_id: AN-S-3719
container:
  component: C20
tier: 6
context:
  lens: QA
state:
  status: archived
  version: 13
  updated_at: 2026-11-09 07:45:14 +0400
---

## Summary

verify Agent container isolation

## Claim

### Prose Claim

This retained contract applies only when AI-Agent execution is separately admitted. It does not enable that execution or claim that its runtime implementation is present.

the Evaluation **must** verify that an isolated Agent can return proposals but cannot access host Project Carriers **or** runtime-control capabilities.

## Details

### Scope

the Docker Agent service's admission **and** filesystem boundaries.

- inspect the resolved configuration: Agent has no Project, host-home **or** Docker socket mount, no published port, no privileged mode **and** no added capabilities.
- test rejected unknown fields, invalid phases, oversized requests, concurrent dispatch **and** invalid structured output.
- verify denied Project write probes **and** absence of credential files from image layers **and** public outputs.
- verify missing credentials produce an explicit readiness failure **without** starting a real Workflow.
