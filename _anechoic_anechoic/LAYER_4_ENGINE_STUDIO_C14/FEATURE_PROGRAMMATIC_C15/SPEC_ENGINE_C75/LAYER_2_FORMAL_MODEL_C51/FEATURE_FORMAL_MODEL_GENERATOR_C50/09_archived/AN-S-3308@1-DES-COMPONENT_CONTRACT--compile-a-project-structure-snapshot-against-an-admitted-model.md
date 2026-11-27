---
atom_family: SPEC
atom_id: AN-S-3308
container:
  component: C50
tier: 1
context:
  template: component_contract
  lens: DES
state:
  status: archived
  version: 1
  updated_at: "2026-11-22T10:12:24.050397+00:00"
---
## Summary

Compile a Project Structure snapshot against an admitted Model

## Guarantee

Given a selected Project Manifest and an admitted Model, return a
serializable Structure snapshot. Include the Project Manifest reference
and digest, the Component ownership and source pins, and each admitted
Component Seed's owner and Manifest reference.

Reject invalid Component identity or containment, duplicate Component
paths, and inputs that change during compilation.

For image staging, admit a supplied previous image only after its Model
Claim selection matches the staged Claims. Reject an unavailable previous
image or changes to the staged source inventory.

## References

AN-S-3065, AN-S-3089, and AN-T-2947.
