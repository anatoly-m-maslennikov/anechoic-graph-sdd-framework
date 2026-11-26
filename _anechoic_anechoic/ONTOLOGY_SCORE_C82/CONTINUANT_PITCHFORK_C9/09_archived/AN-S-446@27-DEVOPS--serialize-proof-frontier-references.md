---
atom_family: SPEC
atom_id: AN-S-446
container:
  component: C9
tier: 3
context:
  lens: DevOps
state:
  status: "archived"
  version: 27
  updated_at: "2026-11-25T23:20:51.419318+00:00"
---
## Summary

Serialize Proof Frontier References

## Claim

### Prose Claim


proof Carrier dependency-frontier serialization.


**every** proof Carrier **must** serialize its machine-readable dependency frontier as a YAML `proof_frontier_refs` list of exact versioned **or** digest-bound references. prose **must** be reserved for additional invalidation conditions that cannot be encoded **without** loss.
