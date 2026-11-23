---
atom_family: SPEC
atom_id: AN-S-3408
container:
  component: C9
tier: 1
context:
  lens: DES
state:
  status: archived
  version: 31
  updated_at: 2026-10-29 17:09:47 +0400
---
## Summary

Define Requirement Content Role

## Claim scope

the Requirement Content Role.

## Claim

A Requirement Atom is an Atom with Content Role Requirement. Its Claim specifies a required outcome or runtime behavior, or defines the governed model and its constraints. Common Atom meaning, properties and constraints are inherited.

## Details

- Functional requirements specify required business/domain behavior.
- Non-functional requirements specify required runtime qualities, including speed, performance, delivery guarantees and error-rate limits.
- Model definitions and Entity Definition constraints specify the methodology's own governed model and constraints; they remain Requirements.
- Subject and Content Role are independent. A Requirement can govern a Domain, Engineering or global Graph Subject.
- Architecture and coding choices describe how to achieve a result and belong to Method, even when mandatory.
- an obligation, permission, **or** prohibition does **not** by itself select this Content Role; classification follows the Claim's primary contribution.
