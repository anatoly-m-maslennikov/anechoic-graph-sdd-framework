---
atom_family: SPEC
atom_id: AN-S-462
container:
  component: C9
tier: 3
context:
  lens: DevOps
state:
  status: archived
  version: 18
  updated_at: 2026-10-23 03:14:50 +0400
---
## Summary

Bind Project Settings **to** its authoritative TOML Carrier

# Summary

Bind Project Settings **to** its authoritative TOML Carrier

## Scope

the authoritative TOML File Carrier for Project Settings of a Project named `<project_name>`.

## Claim

the Project Settings Artifact for a Project named `<project_name>` **must** use `anechoic_project_settings.toml` directly inside that selected Project's `.anechoic_<project_name>/` control root as its **`=1`** authoritative TOML File Carrier.

## Details
