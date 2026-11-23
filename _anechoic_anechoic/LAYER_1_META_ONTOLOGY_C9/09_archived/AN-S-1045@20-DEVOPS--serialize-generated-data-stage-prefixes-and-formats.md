---
atom_family: SPEC
atom_id: AN-S-1045
container:
  component: C9
tier: 3
context:
  lens: DevOps
state:
  status: archived
  version: 20
  updated_at: 2026-10-29 10:13:51 +0400
---
## Summary

Serialize Generated Data Stage Prefixes and Formats

## Claim scope

Journal input and generated Projection Carriers.

## Claim

Journal input **and** generated Projection Carriers **must** use these ordered stage prefixes: canonical Journal input `src`, deterministic lossless staging Projection `stg`, consumer-ready semantic Projection `mrt`, **and** aggregated metrics Projection `biz`. `src` **must** use canonical NDJSON Journal input; `stg` **must** use TOON. these prefixes classify Journal inputs **and** generated Projections **only**. unregistered stage prefixes remain available for later governed Extension.
