---
atom_family: SPEC
atom_id: AN-S-2896
container:
  component: C9
tier: 1
context:
  lens: DES
state:
  status: "archived"
  version: 1
  updated_at: 2026-10-29 00:13:17 +0400
---
# Summary

Define Asset File

## Claim

An Asset File is a file-level, non-executable Implementation item needed by runtime or tests and contained in one Package. Descriptive Documentation, rather than required runtime/test input, is a separate Package part.

### Formal claim

```text
Package > Asset File
```

## Semantics

The item and its Carrier are distinct. An executable permission bit or file extension alone does not decide the item's role. Runtime or test necessity distinguishes this kind from Documentation; it does not automatically classify every non-executable repository file as an Asset File.

## Details

CA-A-1266 narrows the previous broad Asset File proposal. CA-A-1267 confirms runtime and test Assets. Resources member classification remains separate work, rather than an unanswered runtime-versus-tests decision. Numeric identity, Current adoption and any Delivery mapping remain pending. No new primitive Format or runtime implementation is introduced.

## Superseded — do not promote

CA-A-1271 restores Asset as the logical kind because files are Carriers. The promotion candidate is define-implementation-asset.md. This Asset File naming Draft is retained for historical references only, not as another kind or alias.
