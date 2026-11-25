---
atom_family: SPEC
atom_id: AN-S-2000
container:
  component: C9
tier: 3
context:
  lens: DES
state:
  status: archived
  version: 16
  updated_at: 2026-11-04 05:21:15 +0400
---
## Summary

Define Project.Framework Settings.Artifact Timestamp Timezone

## Claim

### Prose Claim


the Artifact timestamp timezone setting in Framework Settings.


The value supplies the timezone used when emitting Artifact timestamps.


### Formal Claim

```CFEL
# model
Project.Settings.Artifact Timestamp Timezone:: [string]{::0..1};

Project.Settings.Artifact Timestamp Timezone.*[]{::0}
```

## Details

Evidence: CA-D-390 supplies the timezone interpretation and its concrete encoding. Candidate #6 keeps Settings attached to Project and keeps concrete ANECHOIC mechanisms in Project Configuration. This definition adds no format, allowed value or default; those remain separate Delivery rules.
