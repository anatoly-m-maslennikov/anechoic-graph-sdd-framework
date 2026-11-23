---
atom_family: SPEC
atom_id: AN-S-1086
container:
  component: C16
tier: 3
context:
  lens: QA
state:
  status: archived
  version: 17
  updated_at: 2026-10-25 17:32:27 +0400
---
## Summary

Derive one structural CRMED draft set from an Inventory

# Derive one structural CRMED draft set from an Inventory

## Claim checked

structural CRMED drafts derived from one Inventory remain reviewable candidates **without** acquiring active authority.

## Test case

derive candidates from one Inventory containing a folder **and** file hierarchy.

## Acceptance criteria

**every** resulting carrier is a draft, retains its observed source boundary, **and** does **not** create an active Scope Unit **or** requirement.

## Failure disposition

stop adoption reconciliation **and** report the first authority **or** source-boundary invention.
