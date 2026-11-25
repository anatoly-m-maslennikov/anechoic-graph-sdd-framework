---
atom_family: SPEC
atom_id: AN-S-1045
container:
  component: C9
tier: 3
context:
  lens: DevOps
state:
  status: "archived"
  version: 24
  updated_at: "2026-11-25T22:39:57.222101+00:00"
---
## Summary

Serialize Generated Data Stage Prefixes and Formats

## Claim

### Prose Claim


Journal input and generated Projection Carriers.


Journal input **and** generated Projection Carriers **must** use these ordered stage prefixes: canonical Journal input `src`, deterministic lossless staging Projection `stg`, consumer-ready semantic Projection `mrt`, **and** aggregated metrics Projection `biz`. `src` **must** use canonical NDJSON Journal input; `stg` **must** use TOON. these prefixes classify Journal inputs **and** generated Projections **only**. unregistered stage prefixes remain available for later governed Extension.
