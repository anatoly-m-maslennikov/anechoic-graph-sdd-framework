---
identity:
  atom_id: AN-S-2342
context:
  container:
    component: C9
  tier: 3
  lens: DES
state:
  status: active
  version: 33
  updated_at: 2026-11-02 19:44:26 +0400
---
## Summary

Register generated-data stages

## Claim

### Prose Claim


the ordered generated-data pipeline stages.


the following ordered generated-data pipeline stages **must** be registered, referenced by their Carrier prefixes governed by CA-D-388-PROJECT_CONFIGURATION-ENG_DECISION--serialize-generated-data-stage-prefixes-and-formats:

| Stage reference | Stage meaning |
| --- | --- |
| `src` | canonical Journal input; authority comes from the Journal, **not** the prefix. |
| `stg` | deterministic, lossless Projection of a bounded `src` frontier. |
| `mrt` | consumer-ready semantic Projection, including Requirement groupings by scope **and** tier **or** Mermaid relation maps. |
| `biz` | aggregated ANECHOIC artifact **and** implementation metrics, including point-in-time snapshots **and** historical trends. |

dependencies **must** move forward through `src → stg → mrt → biz`; a stage **may** depend on **any** earlier registered stage but **must not** depend on a later stage.
