---
atom_family: SPEC
atom_id: AN-S-4158
container:
  component: C9
tier: 1
context:
  lens: DES
state:
  status: archived
  version: 1
  updated_at: 2026-10-29 17:09:47 +0400
---
## Summary

Define Concern Priority

## Claim scope

Handling priority carried by a Concern Atom.

## Claim

Concern Priority is exactly one handling-priority value—High, Medium or Low—for a Concern. Selection and conflict handling remain separate governed policy; the Delivery carrier stores lowercase high, medium or low and never virtual highest.

### Formal claim

```text
Entity/Object/Continuant/Governing Objects/Atom/Content Role: Concern.Priority[string]{1}
Entity/Object/Continuant/Governing Objects/Atom/Content Role: Concern.Priority: High
Entity/Object/Continuant/Governing Objects/Atom/Content Role: Concern.Priority: Medium
Entity/Object/Continuant/Governing Objects/Atom/Content Role: Concern.Priority: Low
```

## Details

Source meaning: CA-R-1336, CA-R-1629, CA-E-623, CA-D-386. Scope-specific constraints remain in their governing Rs.
