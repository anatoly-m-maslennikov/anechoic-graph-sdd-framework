---
atom_family: SPEC
atom_id: AN-S-3494
container:
  component: C16
tier: 3
context:
  lens: DES
state:
  status: archived
  version: 2
  updated_at: 2026-10-14 20:53:35 +0400
---
## Summary

Require a complete reusable Framework package

# Summary

Require a complete reusable Framework package

## Scope

the package content reusable by isolated target-Project installations.

## Claim

the INSTALL_TOOLS facade **must** admit **=1** package containing the complete Engine, exact dependency and version carriers, admitted defaults, `ca`, active Methodology source catalog and declared support **before** installation.

## Details

The complete Engine is the whole `102_FRAMEWORK_ENGINE/` package row set, not a selected runtime subset. `pyproject.toml`, `uv.lock` and `version.toml` are sealed rows; the manifest binds both `framework_version` and `version_toml_sha256`. Core is required; optional available extensions and configuration are catalogued with immutable admission but are **not** autoloaded, including private entries. Missing, extra, checkout-derived, secret-shaped, mutable or mode-mismatched members refuse admission.
