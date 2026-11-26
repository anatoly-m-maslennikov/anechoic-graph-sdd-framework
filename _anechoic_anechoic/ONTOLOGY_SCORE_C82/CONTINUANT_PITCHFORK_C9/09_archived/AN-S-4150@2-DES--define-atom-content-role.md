---
atom_family: SPEC
atom_id: AN-S-4150
container:
  component: C9
tier: 1
context:
  lens: DES
state:
  status: archived
  version: 2
  updated_at: 2026-10-30 17:32:18 +0400
---
## Summary

Define Atom Content Role

## Claim scope

The required role classification of an Atom.

## Claim

Atom Content Role is the required role classification of an Atom primary contribution; each Atom carries exactly one string Content Role, under which its applicable Type and content contract are resolved.

`Atom/(.Content Role: X)` identifies a narrower Atom kind qualified by that Atom Property and its admitted literal value X; it neither creates an intermediate Content Role Entity nor assigns X to an existing Atom instance.

### Formal claim

```text
Atom.Content Role[string]{1}
```

## Details

Source meaning: CA-R-655. Scope-specific constraints remain in their governing Rs.
