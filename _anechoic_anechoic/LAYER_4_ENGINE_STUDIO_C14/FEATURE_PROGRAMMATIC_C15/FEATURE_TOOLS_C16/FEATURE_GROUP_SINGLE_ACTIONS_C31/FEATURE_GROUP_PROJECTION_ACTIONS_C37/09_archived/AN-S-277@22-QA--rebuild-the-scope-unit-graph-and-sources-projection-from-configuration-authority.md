---
atom_family: SPEC
atom_id: AN-S-277
container:
  component: C37
tier: 2
context:
  lens: QA
state:
  status: archived
  version: 22
  updated_at: 2026-10-27 19:59:29 +0400
---
## Summary

Rebuild the Scope Unit Graph and Sources Projection from Configuration Authority

# Rebuild the Scope Unit Graph and Sources Projection from Configuration Authority

## Test case

use an isolated Project fixture with valid authoritative Project Structure, Project Settings, Framework Instance Settings, Project Atoms, **and** observed Scope Unit folders. include:

- a declared Scope Unit **without** an active Goal;
- a declared Scope Unit whose folder is absent;
- an observed folder **without** an accepted declaration;
- an observed path that conflicts with its accepted declaration.

remove previous generated Graph **and** Sources outputs. run the generator. **in** separate fixtures, remove **or** invalidate Project Structure.

## Acceptance criteria

- valid authoritative inputs produce deterministic views of the accepted declarations **and** their exact source revisions **without** reading previous generated views.
- Goal **and** materialization gaps remain visible. undeclared **or** mismatched folders remain observations **and** **must not** become accepted Scope Units **or** redefine bindings.
- missing **or** invalid Project Structure yields an explicit unresolved-authority diagnostic **without** claiming a complete accepted Project Structure.
- Project Structure **and** Settings remain byte-identical.

## Failure disposition

reject the generator **if** it promotes observations **or** generated outputs into authority, silently drops declared units, **or** modifies an authoritative input.
