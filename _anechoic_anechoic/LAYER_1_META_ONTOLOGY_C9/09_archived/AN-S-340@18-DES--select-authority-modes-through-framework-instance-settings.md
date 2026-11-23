---
atom_family: SPEC
atom_id: AN-S-340
container:
  component: C9
tier: 2
context:
  lens: DES
state:
  status: archived
  version: 18
  updated_at: 2026-10-24 10:48:25 +0400
---
## Summary

Select Authority Modes through Framework Instance Settings

# Summary

Select Authority Modes through Framework Instance Settings

## Scope

the selection **and** overrides of Authority Modes through Framework Instance Settings.

## Claim

Framework Instance Settings **must** select the Project Authority Mode **and** default Scope Unit Authority Mode. a Scope Unit's explicit Authority Mode override **must** be owned **only** by its Project Structure declaration; an omitted override uses the effective Framework Instance setting **without** becoming an authored per-unit value. permitted values are `strict` **and** `casual`; neither changes the authority of active Atoms.

## Details
