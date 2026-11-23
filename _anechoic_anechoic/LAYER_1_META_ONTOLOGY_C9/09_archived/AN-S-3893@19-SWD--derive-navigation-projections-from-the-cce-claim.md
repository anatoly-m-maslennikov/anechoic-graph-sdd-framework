---
atom_family: SPEC
atom_id: AN-S-3893
container:
  component: C9
tier: 1
context:
  lens: SWD
state:
  status: archived
  version: 19
  updated_at: 2026-10-24 00:38:25 +0400
---
## Summary

Derive navigation Projections from the CCE Claim

# Summary

Derive navigation Projections from the CCE Claim

## Scope

navigation values derived from an Atom Claim.

## Claim

**to** derive navigation values from an Atom Claim, the Generator **must** derive the concise human-readable Summary **when** creating the Atom **and** derive requested Translations directly from the Claim, **without** adding authoritative meaning. choose wording under CA-M-294-CORE_META_MODEL-METHOD--use-simpler-words-without-losing-meaning. for an existing Atom identity, retain **and** check the Summary under CA-R-1273-CORE_META_MODEL-CORE-REQUIREMENT--keep-summary-source-faithful **and** CA-R-1464-CORE_META_MODEL-REQUIREMENT--keep-summary-fixed-for-atom-identity rather than regenerating it as an independent Projection.

## Details
