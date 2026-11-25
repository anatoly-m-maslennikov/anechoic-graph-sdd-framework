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
  version: 15
  updated_at: 2026-09-27 16:46:44 +0400
---
## Summary

Reference Every Prerequisite Subject through DEPENDS_ON

# Summary

Reference Every Prerequisite Subject through DEPENDS_ON

## Scope

coverage of canonical Entity mentions by an Atom's Subjects.

## Claim

**every** Atom's Subject targets **must** be exactly the distinct canonical Entities independently mentioned **in** its Markdown Main Content, **not** an Atom citation label rendered under `CA-M-301 — Make Atom Claims easy to understand` as **`=1`** exact Atom ID **and** its source-faithful Summary: **`=1`** GOVERNS target for the Entity governed by its Claim, **and** DEPENDS_ON targets for **every** other mentioned Entity.

## Details

coverage includes Summary **and** **all** other body sections, nested headings, tables, examples, **and** reference labels. an Atom citation label is readable authority evidence, **not** an Entity mention **or** Subject target. this exclusion holds **when** the label occurs **in** the same sentence as Entity language; inventory that Entity **only** **when** the surrounding prose independently uses it. a mention outside Claim is **not** otherwise optional coverage. do **not** repeat GOVERNS **in** DEPENDS_ON **or** include an Entity absent from Main Content. a qualified Subject Path identifies its complete target; its component Terms **and** implicit bearer prefixes are **not** additional Entity mentions **unless** independently referenced. Subjects remain Relations rather than their Entity targets. unresolved Entity mentions require resolution **before** coverage can pass.
