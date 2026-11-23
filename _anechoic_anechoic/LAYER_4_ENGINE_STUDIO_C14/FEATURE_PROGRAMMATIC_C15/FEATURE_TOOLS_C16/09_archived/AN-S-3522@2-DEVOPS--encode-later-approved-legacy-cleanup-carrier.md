---
atom_family: SPEC
atom_id: AN-S-3522
container:
  component: C16
tier: 3
context:
  lens: DevOps
state:
  status: archived
  version: 2
  updated_at: 2026-10-14 20:53:35 +0400
---
## Summary

Encode later approved legacy cleanup carrier

# Summary

Encode later approved legacy cleanup carrier

## Scope

One separately authorized post-migration cleanup of an exact retained legacy inventory.

## Claim

the INSTALL_TOOLS facade **must** admit legacy cleanup **only** from a later exact Operator-approved cleanup carrier, and **must not** couple cleanup to installation, migration or selector activation.

## Details

`.anechoic_runtime/installation/migrations/<migration_id>/cleanup-approval.toml` contains `schema_version = 1`, migration ID, inventory SHA-256, target context SHA-256, exact ordered removable relative paths, approval reference and approval digest. It is valid only after a completed and reopened CA-D-606 switch plus retained CA-D-607 history; it never authorizes broad-root, glob or inferred-path deletion.

`cleanup-result.toml` records every pre-delete revalidation, actual removed path and terminal outcome. Changed inventory, active or uncertain owned process, missing approval, mismatched context, unresolved migration or unavailable terminal recording refuses without deletion. Historical migration and retained package evidence remain intact.
