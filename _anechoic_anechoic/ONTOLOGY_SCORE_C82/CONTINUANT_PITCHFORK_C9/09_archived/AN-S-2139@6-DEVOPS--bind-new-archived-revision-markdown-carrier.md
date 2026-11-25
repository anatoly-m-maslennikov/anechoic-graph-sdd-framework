---
atom_family: SPEC
atom_id: AN-S-2139
container:
  component: C9
tier: 3
context:
  lens: DevOps
state:
  status: archived
  version: 6
  updated_at: 2026-10-19 15:56:02 +0400
---
## Summary

Bind new archived Revision Markdown Carrier

# Summary

Bind new archived Revision Markdown Carrier

## Scope

The single Markdown Archive Carrier created for an Atom Revision newly placed in Archived status.

## Claim

**when** an Atom Revision newly attains its model-admitted `Archived` Status **and** no more-specific applicable Delivery mapping exists for its Artifact Type, its **`=1`** Markdown Archive Carrier **must** be classified as that Revision's Archive Carrier **and** be placed at `archived/<basename>@<version>.md`: `archived/` follows CA-D-466's Status fallback **and** `@<version>` follows CA-D-289.

## Details

This is a binding of the existing generic Status-placement and Archive-basename rules, not a universal placement override. A more-specific admitted Delivery mapping takes precedence. It neither relocates nor reclassifies an existing immutable legacy `archive/` Carrier, and it does not settle placement for a Revision without the stated newly archived Markdown Carrier.
