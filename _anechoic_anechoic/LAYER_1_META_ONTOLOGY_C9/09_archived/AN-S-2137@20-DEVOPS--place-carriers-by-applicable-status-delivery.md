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
  version: 20
  updated_at: 2026-10-29 07:45:30 +0400
---
## Summary

Place Carriers by Applicable Status Delivery

## Claim scope

Carrier placement where an applicable qualified Artifact Status model exists or does not exist.

## Claim

**when** an applicable qualified Artifact Status model exists **and** an Artifact has **`=1`** valid current Status, its Carrier placement **must** follow the most specific applicable Delivery rule for that Artifact Type; **only when** no more-specific mapping exists, Active uses the canonical current directory **and** another Status uses its lowercase Status subdirectory. **when** no applicable qualified Status model exists, Carrier placement **must not** derive a Status directory from absent Status.

## Details
