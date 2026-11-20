---
atom_family: SPEC
atom_id: AN-S-1565
structure:
  container:
    component: C24
  tier: 3
context:
  lens: DES
state:
  status: active
  version: 12
  updated_at: 2026-11-10 20:47:54 +0400
---
## Summary

Separate implementation prompt input authority

## Claim scope

the admitted input packet passed to one current Implementation Workflow prompt.

## Claim

### Prose Claim

the Implementation **must** carry selected active R/D targets as what to implement, one verified complete active-M projection as how to implement, and applicable E atoms as separate checks, each with identity, revision, path, digest, and full required content.

## Details

The M projection is a derived Run input, sorted repeatably and retained downstream; membership does not establish applicability. Missing, stale, conflicting, unauthorized, or incomplete inputs return the source Step's blocked result.
