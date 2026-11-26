---
atom_family: SPEC
atom_id: AN-S-2040
container:
  component: C9
tier: 3
context:
  lens: DES
state:
  status: archived
  version: 3
  updated_at: 2026-11-04 09:36:36 +0400
---

## Summary

Define Necessary Information Threshold

## Claim

### Prose Claim


A present threshold value is an integer-percentage override. An absent override uses the governed default.

### Formal Claim

```CFEL
# model
Project.Settings.Confidence.Necessary Information Threshold:: {::0..1};

Project.Settings.Confidence.Necessary Information Threshold.*[]{::0}
```

