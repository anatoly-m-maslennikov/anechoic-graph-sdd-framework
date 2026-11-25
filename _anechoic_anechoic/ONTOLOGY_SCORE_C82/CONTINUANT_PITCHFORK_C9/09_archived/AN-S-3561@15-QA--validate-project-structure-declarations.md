---
atom_family: SPEC
atom_id: AN-S-3561
container:
  component: C9
tier: 2
context:
  lens: QA
state:
  status: archived
  version: 15
  updated_at: 2026-10-23 23:33:48 +0400
---
## Summary

Validate Project Structure declarations

# Summary

Validate Project Structure declarations

## Scope

Project Structure declarations.

## Claim

the Evaluation **must** reject Project Structure **if**

- its registered Carrier schema is invalid,
- a Scope Unit Name is duplicated **or** invalid,
- a parent is unresolved **or** self-referential,
- parentage **contains** a cycle,
- a parent refers **to** another Project,
  - a retained ancestry/path representation disagrees with the declared parent chain,
- **or** a declaration assigns an invalid Type, Label, order, navigation value, Authority Mode, **or** Carrier binding.

- Ordered siblings **must not** share structural Local Order; Navigational Order Number duplicates alone **must not** fail validation.
- an Unordered unit **must not** carry structural Local Order.
- Label **must not** determine Type.
- retained readable fields **must** agree with governing source fields **and** admitted Carrier exceptions.
- lexical **and** resolved-path collisions, traversal outside the authorized repository boundary, **and** ambiguous unit lookup **must** fail.
- the Evaluation **must** test a valid declaration **and** a falsifying example for **every** applicable condition, with explicit failures for unknown fields **or** unsupported schema versions.

## Details
