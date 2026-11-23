---
atom_family: SPEC
atom_id: AN-S-2137
container:
  component: C9
tier: 3
context:
  lens: DevOps
state:
  status: archived
  version: 9
  updated_at: 2026-10-24 00:38:25 +0400
---
## Summary

Place Carriers by Applicable Status Delivery

# Summary

Place Carriers by Applicable Status Delivery

## Scope

Carrier placement where Artifact Activity applies or does not apply.

## Claim

**when** Activity applies **and** an Artifact has **`=1`** valid current Revision Status, its Carrier placement **must** follow the most specific applicable Delivery rule for that Artifact Type; **only when** no more specific mapping exists, Active uses the canonical current directory **and** another Status uses its lowercase Status subdirectory. **when** Activity does **not** apply, Carrier placement **must not** derive a Status directory from absent Activity.

## Details
