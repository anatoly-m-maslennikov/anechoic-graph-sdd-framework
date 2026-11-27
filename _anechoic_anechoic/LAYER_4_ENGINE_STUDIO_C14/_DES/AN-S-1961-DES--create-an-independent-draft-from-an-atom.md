---
atom_family: SPEC
atom_id: AN-S-1961
container:
  component: C14
tier: 3
context:
  lens: DES
state:
  status: active
  version: 3
  updated_at: "2026-11-27T15:50:51.353081+00:00"
---
## Summary

Create an independent Draft from an Atom

## Claim

### Prose Claim

Create Draft lets the caller choose to copy an existing Atom into a new independent Draft. The source may be Current, Archived or another Draft. Resolve the source using AN-S-3160.

Give the copy a new Atom ID and Version 1 at creation. Copy the source and its authored Relations, then apply only the supplied changes. Validate the Relations for the new Atom under the admitted Model. Do not add a replacement relation to the source just because it was copied. Leave the source unchanged. The copy does not supersede it.

The existing successor option retains its identity and Version rules.
