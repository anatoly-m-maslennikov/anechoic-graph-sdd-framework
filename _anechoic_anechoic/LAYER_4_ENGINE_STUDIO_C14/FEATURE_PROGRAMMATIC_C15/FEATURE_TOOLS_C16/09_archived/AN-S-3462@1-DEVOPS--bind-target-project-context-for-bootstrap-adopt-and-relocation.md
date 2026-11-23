---
atom_family: SPEC
atom_id: AN-S-3462
container:
  component: C16
tier: 3
context:
  lens: DevOps
state:
  status: archived
  version: 1
  updated_at: 2026-10-09 16:24:06 +0400
---
## Summary

Bind target-Project context for bootstrap, adopt and relocation

# Summary

Bind target-Project context for bootstrap, adopt and relocation

## Scope

One declared target Project identity and its admissible control inputs.

## Claim

the INSTALL_TOOLS facade **must** retain a content-addressed target context for every bootstrap, adoption or relocation and **must not** invent an Operator, target root, control child, settings, Project Structure or registry.

## Details

`.anechoic_runtime/installation/contexts/<target_project_context_sha256>.toml` has `schema_version = 1`, `mode`, `target_project_identity`, `control_child_relpath`, `settings_sha256`, `project_structure_sha256`, `registry_sha256`, `repository_identity`, `root_locator` and optional `relocates_context_sha256`. `mode` is exactly `bootstrap` or `adopt`; a non-git Project records `repository_identity = false`, while a repository may hold two contexts only when their target identities and control children are distinct.

The digest is calculated from canonical UTF-8 TOML bytes excluding its own digest field. Relocation creates a new context linked to the prior context after validating the same declared Project identity and current controls; it does not reuse an absolute checkout path as identity. Missing, ambiguous, changed or non-Project inputs refuse before runtime state is written.
