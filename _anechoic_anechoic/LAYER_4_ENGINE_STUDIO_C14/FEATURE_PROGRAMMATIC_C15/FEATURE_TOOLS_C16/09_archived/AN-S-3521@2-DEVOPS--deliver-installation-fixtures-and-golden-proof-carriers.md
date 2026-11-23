---
atom_family: SPEC
atom_id: AN-S-3521
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

Deliver installation fixtures and golden proof carriers

# Summary

Deliver installation fixtures and golden proof carriers

## Scope

The reproducible fixture and golden carrier set for package, target and migration acceptance.

## Claim

the INSTALL_TOOLS facade **must** deliver fixtures and goldens that bind exact package, selector, context, generation and migration bytes, and **must not** substitute a synthetic pass field for existing Full Gate evidence.

## Details

Fixtures cover a non-git Project, two Projects in one repository, bootstrap, adoption, relocation, unchanged package execution, unknown revision refusal, concurrent installation, owned-process migration, unsafe quiescence and cleanup refusal. Each fixture has an expected manifest, catalog, packagecurrent selector, target context, installation selector, command/generation records and retained migration carriers where applicable.

Golden full-gate evidence identifies the existing declared suite receipt, all package-row test modules and the exact three Docker E2E modules. A golden rejects a changed `version.toml`, `pyproject.toml`, `uv.lock`, image input, source catalog or package tree after sealing. Fixture result JSON can describe observations, but is not an admission flag.
