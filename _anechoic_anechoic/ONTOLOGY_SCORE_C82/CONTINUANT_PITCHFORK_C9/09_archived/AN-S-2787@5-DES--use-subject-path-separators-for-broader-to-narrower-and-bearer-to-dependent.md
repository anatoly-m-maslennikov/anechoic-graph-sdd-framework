---
atom_family: SPEC
atom_id: AN-S-2787
container:
  component: C9
tier: 3
context:
  lens: DES
state:
  status: archived
  version: 5
  updated_at: 2026-10-24 01:18:03 +0400
---
## Summary

Use Subject Path Separators for Broader-to-Narrower and Bearer-to-Dependent

# Summary

Use Subject Path Separators for Broader-to-Narrower and Bearer-to-Dependent

## Scope

a Subject Path.

## Claim

**in** a Subject Path, `/` **must** separate a broader component from its following narrower component; `//`, recognized as one separator token and **not** two `/` tokens, **must** separate an Entity kind component from the following named instance component; `.` **must** separate a bearer component from its following dependent component; `:` **must** separate a Property component from its following allowed-value component; **and** `@` is **not** Subject syntax. the complete Subject Path still resolves **to** **`=1`** existing canonical target **and** does **not** create target identities. `//` denotes the existing kind-to-named-instance connection, distinct from the Atom's outer Subject Relation. The intended EntityGraph fact is named instance INSTANCE_OF kind, but a projection may assert that fact only under separately authored Core authority; syntax alone does **not** admit it. the mechanical native fact for `.` is Dependent IS_BORNE_BY Bearer; for `:` it is AllowedValue IS_ALLOWED_VALUE_OF Property. `/` admits **no** native Subject **or** Entity relation; any later Terms-Graph binding to NARROWER_THAN remains separately governed.

## Details
