---
atom_family: SPEC
atom_id: AN-S-3409
container:
  component: C9
tier: 1
context:
  lens: DES
state:
  status: archived
  version: 32
  updated_at: 2026-10-29 17:09:48 +0400
---
## Summary

Define Delivery Content Role

## Claim scope

the Delivery Content Role.

## Claim

A Delivery Atom is an Atom with Content Role Delivery. Its Claim specifies how an Entity is represented, serialized, stored or placed in a Carrier. Common Atom meaning, properties and constraints are inherited.

## Details

Delivery governs representation formats, contents, addresses, placement, Entity/Carrier bindings and constraints on changes to those representations. Requirement defines the Entities, their dependent properties and their classification, including Carrier kinds. A statement defining what a Carrier or property is remains a Requirement; a statement specifying how its representation is encoded or placed is Delivery. A property stored in YAML or a Markdown section does not require its own Carrier entity or separately registered binding.
