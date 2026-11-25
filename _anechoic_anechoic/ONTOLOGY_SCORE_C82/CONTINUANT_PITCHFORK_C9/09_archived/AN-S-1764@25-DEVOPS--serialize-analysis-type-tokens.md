---
atom_family: SPEC
atom_id: AN-S-1764
container:
  component: C9
tier: 3
context:
  lens: DevOps
state:
  status: archived
  version: 25
  updated_at: 2026-11-02 15:49:28 +0400
---
## Summary

Serialize Analysis Type Tokens

## Claim scope

the serialization of Analysis & Advisory Type tokens in an Analysis & Advisory Atom File Carrier filename.

## Claim

an Analysis & Advisory Atom File Carrier **must** serialize the following Type components within the Atom filename grammar governed by CA-D-283 **and** CA-D-284:

- Rationale: `RATIONALE`.
- External Analysis Report: `EXTERNAL_ANALYSIS_REPORT`.

these mappings govern filename representation; they do **not** rename a Type, admit a new Type, **or** prescribe a YAML Type value.
