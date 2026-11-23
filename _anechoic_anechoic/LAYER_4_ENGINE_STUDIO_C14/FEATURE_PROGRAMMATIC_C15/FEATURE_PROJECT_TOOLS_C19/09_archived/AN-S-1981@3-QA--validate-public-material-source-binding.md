---
atom_family: SPEC
atom_id: AN-S-1981
container:
  component: C19
tier: 3
context:
  lens: QA
state:
  status: archived
  version: 3
  updated_at: 2026-10-14 12:27:48 +0000
---
## Summary

Validate public material source binding

# Summary

Validate public material source binding

## Scope

one selected public documentation closure.

## Claim

**the Operator** **must** verify that README, full PR body, Version History carrier and selected Version remain the exact prepared public material bindings and reject substituted carrier, Version, document bytes or PR identity.

## Details

The golden successful case contains distinct What's new and What's fixed PR sections. Adding only the actual matching PR URL to the already-generated concise Version History summary may change those metadata bytes while preserving the selected Version and all non-metadata source/material bindings. A substituted raw document byte, substantive summary rewrite, guessed or unrelated PR identity, or changed non-metadata binding is refused. This tests actual prepared material binding, not a retired CA-D-566 snapshot or a newly invented Source Proof serialization.
