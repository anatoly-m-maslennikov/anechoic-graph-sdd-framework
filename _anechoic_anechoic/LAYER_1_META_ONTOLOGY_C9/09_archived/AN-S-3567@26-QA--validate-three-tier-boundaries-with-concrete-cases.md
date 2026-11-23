---
atom_family: SPEC
atom_id: AN-S-3567
container:
  component: C9
tier: 3
context:
  lens: QA
state:
  status: archived
  version: 26
  updated_at: 2026-10-24 00:51:05 +0400
---
## Summary

Validate three-tier boundaries with concrete cases

# Summary

Validate three-tier boundaries with concrete cases

## Scope

three-tier classification, structural, scope, and representation fixtures.

## Claim

This Evaluation **must** reject a tier fixture that derives authority from a legacy label, role/type shortcut, filename, or structural depth instead of the complete Claim, owner Scope Unit, and applicable numeric definition.

### Numeric fixtures

- classify Project ordinary Atoms at Tier `0` or higher, non-Project Atoms at Tier `1` or higher, and a Project-owned Goal at exactly `-1`; use the initial display names Principle, Core, General, and Standard only as labels for `0`, `1`, `2`, and `3`.
- preserve each Atom's numeric Tier through Projection, filename, and other delivery representations; omission of the Standard display token does not erase the internal Tier and no representation token is a Tier source.
- admit a governing stored relation only when its source is a Current RMED Atom and its registered target is Current: a same-Scope target must have a strictly lower Tier; a strict-ancestor target is accepted without Tier comparison; descendant and sibling targets fail; derived inverses do not qualify.
- accept qualifying Evaluation and Operations targets under the registered Evaluation relation without inventing a role/type-to-Tier restriction; unresolved endpoint, membership, owner, or ancestry evidence remains unresolved rather than passing.
- preserve Project ownership and Scope ancestry independently from numeric Tier, keep siblings distinct, and reject cycles, stale legacy tier fields, or a Project Goal with any value other than `-1`.
- source replacement and concrete serialization changes do not authorize a new tier, while active source-authorized additions retain their exact variation point and carrier identity.

### Failure disposition

identify the exact source Revision, fixture, expected result, and observed counterexample; restore the invalid fixture's governed source, owner, binding, classification evidence, relation, or representation and rerun that fixture. A repair must not rewrite frozen historical evidence, invent authority, transfer source ownership, or report an unexecuted operational case as passed.

