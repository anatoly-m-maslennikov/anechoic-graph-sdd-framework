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
  version: 12
  updated_at: 2026-10-19 15:55:41 +0400
---
## Summary

Serialize Analysis Type Tokens

# Summary

Serialize Analysis Type Tokens

## Scope

the serialization of Analysis Type tokens in an Analysis Atom File Carrier filename.

## Claim

an Analysis Atom File Carrier **must** serialize the following Type components within the Atom filename grammar governed by CA-D-283 **and** CA-D-284:

- Rationale: `RATIONALE`.
- External Analysis Report: `EXTERNAL_ANALYSIS_REPORT`.

these mappings govern filename representation; they do **not** rename a Type, admit a new Type, **or** prescribe a YAML Type value.

## Details
