---
atom_family: SPEC
atom_id: AN-S-1997
container:
  component: C9
tier: 3
context:
  lens: DES
state:
  status: archived
  version: 13
  updated_at: 2026-11-11 16:04:42 +0400
---
## Summary

Define Entity/Carrier/Directory Carrier

## Claim

### Prose Claim

A Directory Carrier uses a directory to represent its carried Object; containing files alone does not make it a Directory Carrier.
### Formal Claim

```CFEL
# model
Carrier/Directory ((NARROWER_THAN)) Carrier;
```

