---
atom_family: SPEC
atom_id: AN-S-2777
container:
  component: C9
tier: 1
context:
  lens: DevOps
state:
  status: archived
  version: 2
  updated_at: 2026-10-29 09:57:57 +0400
---
## Summary

Represent Occurrent information through Continuant records

## Claim scope

representation of an Occurrent's recorded information.

## Claim

An Occurrent is not carried or stored as the occurrence itself. When
information about an Occurrent is retained, a Continuant record represents
that information; the Carrier binds the Continuant record, not the Occurrent.
An Event Record in a Journal is one such record.

This reusable Policy governs Occurrent representation. It creates no new
Carrier, per-occurrence binding, Journal record, or relation type.

## Semantics

The Event remains the actual occurrence. Its Event Record is a distinct
Continuant that may have a Carrier. CARRIES and its derived IS_CARRIED_BY view
therefore apply to the represented non-ephemeral record rather than directly
to the Occurrent.

## Details

This Policy reuses CA-R-1958, CA-R-1968, CA-R-1972, and CA-R-1993. It fills
the missing reusable D Policy boundary without changing their definitions or
introducing a direct Occurrent-to-Carrier fact.
