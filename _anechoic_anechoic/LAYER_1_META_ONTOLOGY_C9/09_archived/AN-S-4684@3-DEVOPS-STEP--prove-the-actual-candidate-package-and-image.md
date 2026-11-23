---
atom_family: SPEC
atom_id: AN-S-4684
container:
  component: C9
tier: 3
context:
  template: step
  lens: DevOps
state:
  status: archived
  version: 3
  updated_at: 2026-10-05 21:41:23 +0000
---
## Summary

Prove the actual candidate package and image

# Summary

Prove the actual candidate package and image

## Step

This Step invokes CA-O-168 once with phase `prove_candidate`, binding CA-O-176's exact candidate image digest and the staged complete package, Methodology, hook-free Skill and actual release verification contract.

## Details

The result must prove the actual candidate image and staged complete package, not only source files, a manifest or build success. The Step never recurses into CA-O-164, changes N/N+1 bindings, selects runtime/Skill, removes images or uses an unbound external/paid CLI. Missing or unsafe proof stops truthfully.
