---
atom_family: SPEC
atom_id: AN-S-1767
container:
  component: C9
tier: 3
context:
  lens: DevOps
state:
  status: archived
  version: 16
  updated_at: 2026-10-24 01:37:42 +0400
---
## Summary

Serialize Evaluation Type Tokens

# Summary

Serialize Evaluation Type Tokens

## Scope

the serialization of Evaluation Type tokens in an Evaluation Atom File Carrier filename.

## Claim

an Evaluation Atom File Carrier **must** serialize the following Type components within the Atom filename grammar governed by CA-D-283 **and** CA-D-284:

- QA Case: `QA_CASE`.
- Evaluation Control: `EVALUATION_CONTROL`.
- Evaluation Approach: `EVALUATION_APPROACH`.

these mappings govern filename representation; they do **not** rename a Type, admit a new Type, **or** prescribe a YAML Type value.

## Details
