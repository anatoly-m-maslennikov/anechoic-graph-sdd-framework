---
atom_family: SPEC
atom_id: AN-S-1768
container:
  component: C9
tier: 3
context:
  lens: DevOps
state:
  status: archived
  version: 13
  updated_at: 2026-10-23 03:06:32 +0400
---
## Summary

Serialize Concern Type Tokens

# Summary

Serialize Concern Type Tokens

## Scope

the serialization of Concern Type tokens in a Concern Atom File Carrier filename.

## Claim

a Concern Atom File Carrier **must** serialize the following Type components within the Atom filename grammar governed by CA-D-283 **and** CA-D-284:

- Question: `QUESTION`.
- Problem: `PROBLEM`.
- Risk: `RISK`.
- Opportunity: `OPPORTUNITY`.

these mappings govern filename representation; they do **not** rename a Type, admit a new Type, **or** prescribe a YAML Type value.

## Details
