---
atom_family: SPEC
atom_id: AN-S-1784
container:
  component: C9
tier: 3
context:
  lens: DevOps
state:
  status: archived
  version: 18
  updated_at: 2026-10-29 07:45:30 +0400
---
## Summary

Centralize Project Journal Carriers

## Claim scope

persistent File Carriers of a Project's shared Work Journal and other project-control Journals.

## Claim

**all** persistent project-control Journal File Carriers of a Project **must** reside under **`=1`** Directory Carrier: `.anechoic_<project_name>/_journal/`.

## Details

- Journal segments use this root **or** its subdirectories.
- Artifact Change Log **and** Workflow Execution Log views **are** Projections, **not** separate authoritative Journals.
- Runtime locks, receipts, **and** pending-recording state remain runtime state, **not** canonical Journal Carriers.

Technical and business runtime logs are Journals too, but their configured local database, remote database, or logging sink Carriers are not required to reside in this Directory Carrier. Journal classification does not impose one physical storage technology.
