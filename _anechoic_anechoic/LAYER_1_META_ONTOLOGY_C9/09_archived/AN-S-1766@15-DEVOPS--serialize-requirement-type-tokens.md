---
atom_family: SPEC
atom_id: AN-S-1766
container:
  component: C9
tier: 3
context:
  lens: DevOps
state:
  status: archived
  version: 15
  updated_at: 2026-10-24 00:38:25 +0400
---
## Summary

Serialize Requirement Type Tokens

# Summary

Serialize Requirement Type Tokens

## Scope

the serialization of Requirement Type tokens in a Requirement Atom File Carrier filename.

## Claim

a Requirement Atom File Carrier **must** serialize the following Type components within the Atom filename grammar governed by CA-D-283 **and** CA-D-284:

- Constraint: `CONSTRAINT`.
- Boundary: `BOUNDARY`.

these mappings govern filename representation; they do **not** rename a Type, admit a new Type, **or** prescribe a YAML Type value.

## Details
