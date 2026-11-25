---
atom_family: SPEC
atom_id: AN-S-3648
container:
  component: C9
tier: 2
context:
  lens: DES
state:
  status: archived
  version: 19
  updated_at: 2026-10-29 07:45:27 +0400
---
## Summary

Establish Scope Units through Project Structure declarations

## Claim scope

non-Project Scope Unit declarations in their owning Project Structure.

## Claim

**every** non-Project Scope Unit **must** have **`=1`** declaration **in** its owning Project Structure that supplies its unique Name, direct parent, Type, Label, applicable Local Order, navigation number, **and** authority/Implementation Folder bindings. the declaration establishes the unit independently of Goal coverage **and** Carrier materialization; these remain separately evaluated conditions. Project Settings establishes the root identity, **and** Project Structure **must not** redeclare it as a child. Name/Order Atoms **and** concrete binding Atoms **must not** coexist as independent authorities for the same declared values.

## Details
