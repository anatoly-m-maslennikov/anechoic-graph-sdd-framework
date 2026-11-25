---
atom_family: SPEC
atom_id: AN-S-446
container:
  component: C9
tier: 3
context:
  lens: DevOps
state:
  status: archived
  version: 19
  updated_at: 2026-10-24 01:37:42 +0400
---
## Summary

Serialize Proof Frontier References

# Summary

Serialize Proof Frontier References

## Scope

proof Carrier dependency-frontier serialization.

## Claim

**every** proof Carrier **must** serialize its machine-readable dependency frontier as a YAML `proof_frontier_refs` list of exact versioned **or** digest-bound references. prose **must** be reserved for additional invalidation conditions that cannot be encoded **without** loss.

## Details
