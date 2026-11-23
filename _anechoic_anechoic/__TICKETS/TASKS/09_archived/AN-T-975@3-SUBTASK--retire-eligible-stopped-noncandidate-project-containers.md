---
atom_family: TKT
atom_id: AN-T-975
container:
  component: C15
priority: 2
context:
  template: task
  label: Subtask
state:
  status: archived
  version: 3
  updated_at: '2026-10-21T10:50:11Z'
---
## Summary

Retire eligible stopped noncandidate Project containers

# Summary

Retire eligible stopped noncandidate Project containers

## Objective

Implement the accepted Project-only candidate-retention contract.

## Details

Own release_cleanup.py and test_release_cleanup.py only, including its shared DockerFixture. Remove only positively identified stopped selected-Project MCP containers using noncandidate images, even with matching fingerprint; exact candidate and other running containers remain protected. Inspect positive runtime classification before removal; no force/retry. Give fixture-created owned images explicit ownership metadata, not arbitrary inserted orphans. Synthetic tests only, at most15 minutes own work; split before extending.

### Accepted implementation evidence

Worker focused9/9 and related24/24 checks passed. Root integrated10-module gate102/102 passed16.084s. Stopped selected-Project noncandidate containers lose the fingerprint-only exemption, with positive image inspection before removal; exact candidate, running/foreign/unknown-state resources remain protected. Shared synthetic fixture assigns ownership only to deliberately created Project images, not raw orphans. Owned files pass pinned Ruff/diff checks. No Docker/release execution. Import/call removal completed before root removed unused identity helpers.

### Container placement reconciliation

Parent P2527 is now Done; this already-Done child moves with its matching container hierarchy. Carrier-only relocation advances Version/time and retains exact predecessor; status and accepted implementation are unchanged.
