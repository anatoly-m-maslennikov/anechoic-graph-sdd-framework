---
atom_family: SPEC
atom_id: AN-S-2767
container:
  component: C9
tier: 3
context:
  lens: DevOps
state:
  status: archived
  version: 27
  updated_at: 2026-10-29 07:45:29 +0400
---
## Summary

Derive Direct Containment from the Nearest Directory Carrier

## Claim scope

Artifact Revisions whose canonical Carriers are nested below Directory Carriers.

## Claim

an Artifact Revision whose canonical Carrier is nested below a Directory Carrier **must** derive **`=1`** direct `IS_CONTAINED_BY` connection to the Structural Entity Revision carried by its nearest ancestor Directory Carrier **and** the reverse `CONTAINS` view from that connection.

## Details

For this Carrier-derived view, canonical nesting supplies the fact; the view does not create a second authored relation declaration. IS_CONTAINED_BY is the child-to-parent direction, and CONTAINS is its derived inverse. Reading or refreshing the inverse view does not edit the containing entity's carrier; when that entity is an Atom, it does not create a new Version for it. Physical nesting does not silently replace the logical parent declared by Project Structure under CA-R-1660. Existing Revision/Structural Entity wording is retained for the separate content migration.
