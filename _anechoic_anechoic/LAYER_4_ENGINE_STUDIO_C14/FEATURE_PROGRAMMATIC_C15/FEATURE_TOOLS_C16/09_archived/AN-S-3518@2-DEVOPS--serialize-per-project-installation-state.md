---
atom_family: SPEC
atom_id: AN-S-3518
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

Serialize per-Project installation state

# Summary

Serialize per-Project installation state

## Scope

The exclusive lock shared by all mutable target installation carriers.

## Claim

the INSTALL_TOOLS facade **must** use **=1** per-Project installation lock for selector, wrappers, Skill, projection and state publication, and **must not** treat a PID as lock ownership or process proof.

## Details

`.anechoic_runtime/installation/lock.toml` contains `schema_version = 1`, `target_project_context_sha256`, `owner_run_id`, `operation`, `lock_generation`, `acquired_at`, `command_sha256` and `lease_nonce`. It is acquired through a create-if-absent atomic filesystem operation, is reopened before every publish boundary and is released only by the matching owner generation after a terminal result. A stale or uncertain lock refuses publication until an explicit inspection/recovery path establishes ownership.

All installation, adoption, migration, selector publication, wrapper replacement, Skill publication, projection write and runtime-state write take this lock. A distinct package candidate lock or first-install lock is not a substitute. Lock records are project-contained, do not serialize unrelated Projects and do not make a cross-Project registry.
