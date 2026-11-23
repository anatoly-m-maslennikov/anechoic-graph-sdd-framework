---
atom_family: SPEC
atom_id: AN-S-1654
container:
  component: C9
tier: 1
context:
  lens: DES
state:
  status: archived
  version: 21
  updated_at: 2026-10-03 02:15:29 +0400
---
## Summary

Admit Atoms only where a role has an atomic unit

# Summary

Admit Atoms only where a role has an atomic unit

## Scope

Content Role Type admission.

## Claim

a Content Role admits a Type value for an Atom **only** **when** that role has an independently governed atomic unit that benefits from stable identity, admission, **and** whole-unit lifecycle; ANECHOIC **must not** create a placeholder Type value merely **to** fill a semantic coordinate.

## Details

an Atom with Content Role Requirement, Method, **or** Delivery has a role-qualified Type **only** **when** a separately governed specialized Type applies. an ordinary Atom in these roles has no role-qualified Type; its Content Role already identifies its contribution. a specialized Atom retains **`=1`** admitted Type under its Content Role.
