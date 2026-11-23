---
atom_family: SPEC
atom_id: AN-S-3435
container:
  component: C16
tier: 3
context:
  lens: QA
state:
  status: archived
  version: 8
  updated_at: 2026-10-24 13:39:34 +0400
---
## Summary

Report partial Scope Unit cutover and authorized rollback

# Summary

Report partial Scope Unit cutover and authorized rollback

## Scope

An injected post-declaration failure inside one authorized recoverable cutover entered through CA-D-527's shared service interface.

## Claim

The Evaluation **must** prove partial effects and rollback are reported precisely, separately from service disposition/Run outcome, and no unapproved content is erased.

## Details

- Start the explicitly authorized D527 `execute`, then cause a reference-repair or explicitly included Carrier update to fail after a known declaration effect. Assert D527 carries the started service evidence while `structural_result.state = partial` lists applied/unapplied effects, preservation/breakage, and only the pre-authorized recovery boundary; assert no structural completion claim.
- Exercise the authorized rollback through the same shared contract and assert `structural_result.state = rolled_back` identifies restored and still-broken members. Retain required history/evidence, never reset or overwrite concurrent work, and do not treat a service terminal disposition as a structural success claim.
