---
atom_family: SPEC
atom_id: AN-S-1770
container:
  component: C9
tier: 3
context:
  lens: DevOps
state:
  status: "archived"
  version: 30
  updated_at: "2026-11-25T19:35:30.291238+00:00"
---

## Summary

Serialize Method Type Tokens

## Claim

### Prose Claim

A Method Atom File Carrier must serialize its effective Label within the Atom filename grammar governed by CA-D-283 and CA-D-284. Use the explicit Label when present and the Form name when Label is absent. Normalize the effective Label as an uppercase structured token.

## Details

The filename token is the effective-Label carrier encoding; it does not rename or admit a Form or prescribe a YAML Form value. The YAML `form` field carries the Atom Form under CA-D-657. An explicit `label` field takes precedence; when absent, CA-R-2705 supplies the Form name as the effective Label. Do not infer the Atom Form from a filename token; derive the filename token from the effective Label.

Form admission is governed by the applicable Form declarations and Scope Delegation permissions.
