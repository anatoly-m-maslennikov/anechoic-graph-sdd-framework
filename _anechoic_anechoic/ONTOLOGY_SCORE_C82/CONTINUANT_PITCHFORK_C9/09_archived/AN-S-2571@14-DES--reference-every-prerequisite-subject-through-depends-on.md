---
atom_family: SPEC
atom_id: AN-S-2571
container:
  component: C9
tier: 1
context:
  lens: DES
state:
  status: archived
  version: 14
  updated_at: 2026-09-25 22:01:55 +0000
---
## Summary

Reference Every Prerequisite Subject through DEPENDS_ON

# Summary

Reference Every Prerequisite Subject through DEPENDS_ON

## Scope

coverage of canonical Entity mentions by an Atom's Subjects.

## Claim

**every** Atom's Subject targets **must** be exactly the distinct canonical Entities mentioned **in** its Markdown Main Content: **`=1`** GOVERNS target for the Entity governed by its Claim, **and** DEPENDS_ON targets for **every** other mentioned Entity.

## Details

coverage includes Summary **and** **all** other body sections, nested headings, tables, examples, **and** reference labels. a mention outside Claim is **not** optional coverage. do **not** repeat GOVERNS **in** DEPENDS_ON **or** include an Entity absent from Main Content. a qualified Subject Path identifies its complete target; its component Terms **and** implicit bearer prefixes are **not** additional Entity mentions **unless** independently referenced. Subjects remain Relations rather than their Entity targets. unresolved Entity mentions require resolution **before** coverage can pass.
