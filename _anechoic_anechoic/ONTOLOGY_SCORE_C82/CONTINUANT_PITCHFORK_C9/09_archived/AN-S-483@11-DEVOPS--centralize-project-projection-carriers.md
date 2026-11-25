---
atom_family: SPEC
atom_id: AN-S-483
container:
  component: C9
tier: 3
context:
  lens: DevOps
state:
  status: archived
  version: 11
  updated_at: 2026-10-24 00:51:05 +0400
---
## Summary

Centralize Project Projection Carriers

# Summary

Centralize Project Projection Carriers

## Scope

persistent non-authoritative view Projection Carriers belonging to a Project.

## Claim

**all** persistent view Projection Carriers of a Project **must** reside under **`=1`** Directory Carrier: `.anechoic_<project_name>/_projection/`, **except** Applicable Methodology, whose Carrier Root **must** remain `.anechoic_<project_name>/000_ANECHOIC_framework/00_APPLICABLE_METHODOLOGY/`.

## Details

- Graphs **and** derived Journal views use `_projection/` **or** named subdirectories beneath it.
- Applicable Methodology uses its separate Carrier Root; its Methodology Sources retain the `000_APPLICABLE_MTHD_sources/` subdirectory.
- Authoritative Atoms, Methodology Sources, Project Settings, and Project Structure retain their own authoritative locations.
- Temporary build stages **and** intermediate reports remain ephemeral; publication places the delivered view Projection under its declared Carrier Root.
- The derivation RMED → using O → I does not relocate native Implementation into _projection: native I uses its governed Delivery place and may supply actual-state source facts. Views subsequently generated from I use _projection.
