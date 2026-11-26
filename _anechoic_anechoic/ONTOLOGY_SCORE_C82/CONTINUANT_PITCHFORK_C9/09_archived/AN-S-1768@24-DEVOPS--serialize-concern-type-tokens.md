---
atom_family: SPEC
atom_id: AN-S-1768
container:
  component: C9
tier: 3
context:
  lens: DevOps
state:
  status: "archived"
  version: 24
  updated_at: "2026-11-25T19:37:50.083268+00:00"
---
## Summary

Serialize Concern Type Tokens

## Claim

### Prose Claim


the serialization of Concern Type tokens in a Concern Atom File Carrier filename.


a Concern Atom File Carrier **must** serialize the following Type components within the Atom filename grammar governed by CA-D-283 **and** CA-D-284:

- Question: `QUESTION`.
- Problem: `PROBLEM`.
- Risk: `RISK`.
- Opportunity: `OPPORTUNITY`.

these mappings govern filename representation; they do **not** rename a Type, admit a new Type, **or** prescribe a YAML Type value.
