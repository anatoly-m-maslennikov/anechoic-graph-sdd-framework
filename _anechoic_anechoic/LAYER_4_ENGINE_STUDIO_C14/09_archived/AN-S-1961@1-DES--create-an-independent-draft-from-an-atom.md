---
atom_family: SPEC
atom_id: AN-S-1961
container:
  component: C14
tier: 3
context:
  lens: DES
state:
  status: archived
  version: 1
  updated_at: '2026-11-12T12:37:36.532392+00:00'
---
## Summary

Create an independent Draft from an Atom

## Claim

### Prose Claim

Create Draft lets the caller choose to copy an existing Atom into a new independent Draft. The source may be Current, Archived or another Draft. If the caller supplies only an Atom ID, select Current. An explicit Version or Draft reference selects the exact requested source.

Give the copy a new Atom ID and Version 1 at creation. Copy the source and apply only the supplied changes. Leave the source unchanged. The copy does not supersede it.

The existing successor option retains its identity and Version rules.
