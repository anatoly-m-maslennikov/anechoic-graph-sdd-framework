---
atom_family: SPEC
atom_id: AN-S-1767
structure:
  container:
    component: C9
  tier: 3
context:
  lens: DevOps
state:
  status: active
  version: 25
  updated_at: 2026-11-02 00:18:22 +0400
---
## Summary

Serialize Evaluation Type Tokens

## Claim

### Prose Claim


the serialization of Evaluation Type tokens in an Evaluation Atom File Carrier filename.


an Evaluation Atom File Carrier **must** serialize its effective Label within the Atom filename grammar governed by CA-D-283 and CA-D-284, using the explicit Label when present and the Type name when Label is absent. The effective Label is normalized as an uppercase structured token; an unlabeled Eval Case, Evaluation Control and Evaluation Approach therefore use `EVAL_CASE`, `EVALUATION_CONTROL` and `EVALUATION_APPROACH`. This generic rule covers every admitted Evaluation Type and does not rename a Type, admit a new Type, or prescribe a YAML Type value.
