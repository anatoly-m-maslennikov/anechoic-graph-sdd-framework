---
atom_family: SPEC
atom_id: AN-S-2126
container:
  component: C9
tier: 3
context:
  lens: DES
state:
  status: archived
  version: 2
  updated_at: 2026-11-04 05:21:15 +0400
---

## Summary

Declare Project.Settings.RMED Review.Context Headroom Fraction

## Claim

### Prose Claim


When present, the value is finite and strictly between zero and one.

### Formal Claim

```CFEL
# model
Project.Settings.RMED Review.Context Headroom Fraction:: [float]{::0..1};

Project.Settings.RMED Review.Context Headroom Fraction.*[]{::0}
```

