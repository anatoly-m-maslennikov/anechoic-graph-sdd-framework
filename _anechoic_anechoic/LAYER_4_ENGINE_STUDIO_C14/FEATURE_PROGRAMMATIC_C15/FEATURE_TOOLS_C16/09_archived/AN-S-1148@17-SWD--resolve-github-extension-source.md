---
atom_family: SPEC
atom_id: AN-S-1148
container:
  component: C16
tier: 3
context:
  lens: SWD
state:
  status: archived
  version: 17
  updated_at: 2026-10-26 00:46:35 +0400
---
## Summary

Resolve GitHub Extension source

# Resolve GitHub Extension source

## Applicable when

use this Method **when** determining the declared GitHub source boundary for one Extension package.

## Procedure

1. resolve the declared GitHub repository for one Extension **and** determine whether its package root is the complete repository **or** one declared directory.
2. normalize the repository identity **and** optional declared directory **without** inventing an implicit subdirectory **or** alternate source provider.
3. retrieve the source boundary **and** report the declared repository **and** package-root path as attributable source metadata.
4. reject a missing repository, undeclared subdirectory, **or** source boundary that cannot be mapped **to** the Extension package.
5. return source-resolution facts **only**; do **not** choose an installed version **or** change installed Extension state.

## Outcome

one Extension has an exact attributable GitHub repository source boundary **and** either its complete repository **or** one declared package-root directory.

## Failure or stop

stop on an ambiguous repository, undeclared package root, missing source boundary, **or** an attempt **to** manage installed state.
