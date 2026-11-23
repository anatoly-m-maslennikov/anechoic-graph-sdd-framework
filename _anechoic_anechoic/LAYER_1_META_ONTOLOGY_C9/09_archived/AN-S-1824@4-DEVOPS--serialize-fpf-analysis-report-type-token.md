---
atom_family: SPEC
atom_id: AN-S-1824
container:
  component: C9
tier: 3
context:
  lens: DevOps
state:
  status: archived
  version: 4
  updated_at: 2026-10-24 00:38:25 +0400
---
## Summary

Serialize FPF Analysis Report Type Token

# Summary

Serialize FPF Analysis Report Type Token

## Scope

the filename Type component of a project-owned FPF Analysis Report Markdown Carrier.

## Claim

a project-owned Analysis Atom with `type: FPF Analysis Report` **must** serialize its Type filename component as `FPF_ANALYSIS_REPORT` within the filename grammar governed by CA-D-283 and CA-D-284.

## Details

This mapping adds the representation of the Type admitted by CA-R-1888. It does not rename another Type, change its filename token or replace the common Analysis body layout. Carrier placement follows the applicable Delivery mapping under CA-D-466 and the canonical Analysis content-role directory under CA-D-324.
