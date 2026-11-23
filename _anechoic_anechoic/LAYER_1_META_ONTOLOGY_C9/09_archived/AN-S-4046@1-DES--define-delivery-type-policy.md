---
atom_family: SPEC
atom_id: AN-S-4046
container:
  component: C9
tier: 1
context:
  lens: DES
state:
  status: archived
  version: 1
  updated_at: 2026-10-29 09:34:45 +0400
---
## Summary

Define Delivery Type Policy

## Claim
Policy **means** a Delivery Type whose rule automatically applies to every child Scope Unit of its Local Scope Unit, subject only to genuine topic or environment conditions.

## Details

A Scope Unit can locally own an Policy only when it has at least one actual, currently declared child. A leaf can inherit ancestor Policies but cannot locally own one. Do not create artificial children or count hypothetical future children to retain a Policy label.

A Policy can select a named technology. Actual-child ownership and automatic application to every child distinguish it from Decision; abstract wording or a technology name alone does not classify it.

If the owner loses its last child, review and relocate or reclassify its local Policies; do not infer an automatic runtime conversion.

This Type does not constrain an Atom to a particular Tier. The PROGRAMMATIC-only allowed-Type restriction belongs to Project Configuration, not this reusable definition.
