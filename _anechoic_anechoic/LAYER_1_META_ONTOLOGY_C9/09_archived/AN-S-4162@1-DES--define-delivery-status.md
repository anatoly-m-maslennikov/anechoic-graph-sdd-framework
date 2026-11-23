---
atom_family: SPEC
atom_id: AN-S-4162
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

Define Delivery Status

## Claim scope

Lifecycle status of a Delivery Atom.

## Claim

Delivery Status is the one-string lifecycle classification of a Delivery Atom; it inherits Draft, Active and Archived under the applicable status model, and the Core Delivery Status model admits exactly those three values.

### Formal claim

```text
Entity/Object/Continuant/Governing Objects/Atom/Content Role: Delivery.Status[string]{1}
```

## Details

Source meaning: CA-R-1989, CA-R-655, CA-R-1399. Scope-specific constraints remain in their governing Rs.
