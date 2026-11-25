---
atom_family: SPEC
atom_id: AN-S-1766
container:
  component: C9
tier: 3
context:
  lens: DevOps
state:
  status: "archived"
  version: 25
  updated_at: "2026-11-25T19:35:29.595485+00:00"
---
## Summary

Serialize Requirement Type Tokens

## Claim

### Prose Claim


the serialization of Requirement Type tokens in a Requirement Atom File Carrier filename.


a Requirement Atom File Carrier **must** serialize its effective Label within the Atom filename grammar governed by CA-D-283 and CA-D-284, using the explicit Label when present and the Type name when Label is absent. The effective Label is normalized as an uppercase structured token; an unlabeled Constraint and Boundary therefore use `CONSTRAINT` and `BOUNDARY`. This generic rule covers every admitted Requirement Type and does not rename a Type, admit a new Type, or prescribe a YAML Type value.
