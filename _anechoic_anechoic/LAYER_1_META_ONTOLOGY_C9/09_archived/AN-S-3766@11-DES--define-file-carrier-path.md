---
atom_family: SPEC
atom_id: AN-S-3766
container:
  component: C9
tier: 3
context:
  lens: DES
state:
  status: archived
  version: 11
  updated_at: 2026-10-29 09:34:45 +0400
---
## Summary

Define File Carrier.Path

## Claim scope

File Carrier filesystem locators.

## Claim

A File Carrier's Path **means** the locator of its file within a filesystem, absolute or relative to a stated base. It is a locator, **not** the Carrier's ID.

### Formal claim

```text
File.Path[string]{1}
```

## Details

The Operator distinguishes Carrier ID from path. CA-D-445 requires unambiguous bindings inside authorized path boundaries. Path is the filesystem representation of the locator, not a second independently maintained identity.

Active CA-R-1342 currently assigns Carrier definitions and classification to Delivery. That conflict remains for the later content migration; this draft does not change or supersede active rules.
