---
atom_family: SPEC
atom_id: AN-S-1770
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

Serialize Method Type Tokens

# Summary

Serialize Method Type Tokens

## Scope

Method Atom File Carriers.

## Claim

a Method Atom File Carrier **must** serialize the following Type components within the Atom filename grammar governed by CA-D-283-CORE_META_MODEL-CORE-DELIVERY--serialize-project-owned-markdown-atom-filenames **and** CA-D-284-CORE_META_MODEL-CORE-DELIVERY--serialize-filename-token-case:

- Implementation Method: `IMPLEMENTATION_METHOD`.
- Implementation Decision: `IMPLEMENTATION_DECISION`.
- External Implementation Method: `EXTERNAL_IMPLEMENTATION_METHOD`.
- Method Binding: `METHOD_BINDING`.

## Details

these mappings govern filename representation; they do **not** rename a Type, admit a new Type, **or** prescribe a YAML Type value.
