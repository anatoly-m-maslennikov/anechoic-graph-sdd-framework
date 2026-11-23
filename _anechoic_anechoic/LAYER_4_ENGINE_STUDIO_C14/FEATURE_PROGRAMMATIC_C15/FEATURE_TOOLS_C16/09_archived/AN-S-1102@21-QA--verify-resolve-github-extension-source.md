---
atom_family: SPEC
atom_id: AN-S-1102
container:
  component: C16
tier: 4
context:
  lens: QA
state:
  status: archived
  version: 21
  updated_at: 2026-10-27 19:59:33 +0400
---
## Summary

Verify resolve GitHub Extension source

# Verify resolve GitHub Extension source

## Claim checked

CA-M-218 resolves the declared GitHub repository **and** package-root boundary for one Extension **without** choosing an installed state.

## Applicable when

apply whenever GitHub Extension source-boundary resolution changes.

## Test case

resolve one Extension whose package root is a declared repository subdirectory, **then** resolve another whose package root is the complete repository. repeat with an undeclared subdirectory.

## Acceptance criteria

**every** valid case reports the declared GitHub repository **and** its exact complete-repository **or** declared-directory package root. the undeclared-subdirectory case produces an explicit failure **and** no alternative source boundary.

## Failure disposition

reject the realization **and** preserve source declarations, resolved boundaries, undeclared-subdirectory finding, **and** proof that installed Extension state was unchanged.
