---
atom_family: SPEC
atom_id: AN-S-2141
container:
  component: C9
tier: 3
context:
  lens: DES
state:
  status: archived
  version: 2
  updated_at: 2026-11-02 00:18:22 +0400
---

## Summary

Declare MODEL

## Claim

### Prose Claim



- A local MODEL inherits ANECHOIC's MODEL.
- MODEL inheritance is distinct from Node narrowing.
- Local overrides replace matching inherited rules in the local MODEL.
- Local overrides preserve the base MODEL's rules.
- Unmodified inherited Declarations are reused.

### Formal Claim

```CFEL
# model
MODEL {::0}((IS_PROPERTY_OF));

MODEL >| (Container == yes);

MODEL ((NARROWER_THAN)) Node
```

## Semantics

MODEL declares Node kinds, Relations, Properties, and rules.
