---
atom_family: SPEC
atom_id: AN-S-462
container:
  component: C9
tier: 5
context:
  lens: DevOps
state:
  status: archived
  version: 30
  updated_at: 2026-11-03 23:25:51 +0400
---
## Summary

Bind Project Settings **to** its authoritative TOML Carrier

## Claim

### Prose Claim


the authoritative TOML File Carrier for Project Settings of a Project named `<project_name>`.


the Project Settings Artifact for a Project named `<project_name>` **must** use `anechoic_project_settings.toml` directly inside that selected Project's `.anechoic_<project_name>/` control root as its **`=1`** authoritative TOML File Carrier.
