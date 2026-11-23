---
atom_family: SPEC
atom_id: AN-S-1565
container:
  component: C24
tier: 3
context:
  lens: DES
state:
  status: archived
  version: 4
  updated_at: 2026-10-24 01:50:12 +0400
---
## Summary

Separate implementation prompt input authority

# Summary

Separate implementation prompt input authority

## Scope

the admitted input packet passed to one current Implementation Workflow prompt.

## Claim

the Implementation **must** carry selected active R/D targets as what to implement, one verified complete active-M projection as how to implement, and applicable E atoms as separate checks, each with identity, revision, path, digest, and full required content.

## Details

The M projection is a derived Run input, sorted repeatably and retained downstream; membership does not establish applicability. Missing, stale, conflicting, unauthorized, or incomplete inputs return the source Step's blocked result.
