---
atom_family: TKT
atom_id: AN-T-1782
container:
  component: C00
priority: 2
context:
  template: task
state:
  status: archived
  version: 1
  updated_at: 2026-11-03 18:01:24 +0400
---
## Summary

Simplify MODEL and STRUCTURE Subject roots

## Objective

Mechanically replace ANECHOIC <+ MODEL with ANECHOIC_MODEL and ANECHOIC <+ STRUCTURE with ANECHOIC_STRUCTURE in selected canonical live Subjects.

## Scope

Change only frontmatter subjects.active and subjects.passive string prefixes. Preserve every other source byte, including Claims, IDs, versions, timestamps and relation fields. Use the prior canonical frontier plus actual direct-role Drafts. Preserve historical, delivery, installed, staging and projection snapshots.

## Steps

1. Freeze the exact canonical file list and hashes.
2. Review the simple scalar-preserving script and candidate differences.
3. Apply in place, with no Draft-promotion cycle for this mechanical change.
4. Independently verify the same Subject-only differences and idempotence.

## Definition of Done

Every selected old prefix is replaced; other bytes match the saved preimage; the script is idempotent. Record exact counts and hashes. Keep subsequent Header/Claim/alias Epic work separate.

## Evidence

The root-subject-migration-20261103 packet contains the script, tests, explicit source frontier, application receipt and verification.
