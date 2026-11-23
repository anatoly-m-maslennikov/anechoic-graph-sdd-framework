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
  version: 1
  updated_at: 2026-10-04 19:29:30 +0000
---
## Summary

Report partial Scope Unit cutover and authorized rollback

# Summary

Report partial Scope Unit cutover and authorized rollback

## Scope

An injected post-declaration failure inside one authorized recoverable cutover.

## Claim

The Evaluation **must** prove partial effects and rollback are reported precisely and no unapproved content is erased.

## Details

- Cause a reference-repair or explicitly included Carrier update to fail after a known declaration effect.
- Assert `partial` lists applied/unapplied effects, preservation/breakage, and only the pre-authorized recovery boundary; assert no completion claim.
- Exercise the authorized rollback and assert `rolled_back` identifies restored and still-broken members, retains required history/evidence, and never resets or overwrites concurrent work.
