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
  version: 2
  updated_at: 2026-10-10 05:17:00 +0400
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

### Candidate context and adoption

Binding the context reads the declared target controls and actual package evidence; it is not installation permission. `bootstrap` requires no active native or legacy runtime or installed ca. `adopt` can prepare a context beside existing state; before any replacement, the publisher must independently reopen that exact selected state and its migration/quiescence proof. Adoption never treats arbitrary existing files as an admitted runtime.

The shared installation lock owns an immutable writer for `contexts/<digest>.toml`. The writer validates the closed canonical schema, recomputes the self-excluding digest, reopens the exact settings, structure and registry bytes, and writes only the exact digest-named carrier. Existing identical bytes can be reused; conflicting or aliased carriers refuse. A retained prospective context alone does not activate a generation, overwrite configuration or authorize deletion. The same physical context reader is used before staging and after installation.

