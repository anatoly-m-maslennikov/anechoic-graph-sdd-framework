---
atom_family: SPEC
atom_id: AN-S-1769
container:
  component: C9
tier: 3
context:
  lens: DevOps
state:
  status: active
  version: 29
  updated_at: 2026-11-07 15:18:44 +0400
---

## Summary

Serialize Delivery Type Tokens

## Claim

### Prose Claim

A Delivery Atom File Carrier must serialize its effective Label within the Atom filename grammar governed by CA-D-283 and CA-D-284. Use the explicit Label when present and the Form name when Label is absent. Normalize the effective Label as an uppercase structured token.

## Details

The filename token is the effective-Label carrier encoding; it does not rename or admit a Form or prescribe a YAML Form value. The YAML `form` field carries the Atom Form under CA-D-657. An explicit `label` field takes precedence; when absent, CA-R-2705 supplies the Form name as the effective Label. Do not infer the Atom Form from a filename token; derive the filename token from the effective Label.

Release Definition and Environment Definition remain subject to their applicable admission authority, including CA-R-1665.
