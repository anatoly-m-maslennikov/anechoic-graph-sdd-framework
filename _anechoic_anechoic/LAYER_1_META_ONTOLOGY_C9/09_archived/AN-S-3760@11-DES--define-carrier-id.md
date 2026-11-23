---
atom_family: SPEC
atom_id: AN-S-3760
container:
  component: C9
tier: 1
context:
  lens: DES
state:
  status: archived
  version: 11
  updated_at: 2026-10-29 17:09:47 +0400
---
## Summary

Define Carrier.ID

## Claim scope

Identifiers of individual Carriers.

## Claim

A Carrier ID identifies one Carrier. Its filename and path are **not** its ID.

### Formal claim

```text
Entity/Carrier.ID[string]{1}
```

## Details

The Operator explicitly distinguished Carrier ID from filename and path. CA-D-507 separates Entity identity from Carrier format but does not define Carrier ID. This draft introduces no ID syntax, allocator or registry.

Active CA-R-1342 currently assigns Carrier definitions and classification to Delivery. That conflict remains for the later content migration; this draft does not change or supersede active rules.
