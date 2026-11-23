---
atom_family: SPEC
atom_id: AN-S-1769
container:
  component: C9
tier: 3
context:
  lens: DevOps
state:
  status: archived
  version: 12
  updated_at: 2026-10-20 15:51:07 +0400
---
## Summary

Serialize Delivery Type Tokens

# Summary

Serialize Delivery Type Tokens

## Scope

the serialization of Delivery Type tokens in a Delivery Atom File Carrier filename.

## Claim

a Delivery Atom File Carrier **must** serialize the following Type components within the Atom filename grammar governed by CA-D-283-CORE_META_MODEL-DELIVERY--serialize-project-owned-markdown-atom-filenames **and** CA-D-284-CORE_META_MODEL-DELIVERY--serialize-filename-token-case:

- Release Definition: `RELEASE_DEFINITION`.
- Environment Definition: `ENVIRONMENT_DEFINITION`.

these mappings govern filename representation; they do **not** rename a Type, admit a new Type, **or** prescribe a YAML Type value.

## Details
