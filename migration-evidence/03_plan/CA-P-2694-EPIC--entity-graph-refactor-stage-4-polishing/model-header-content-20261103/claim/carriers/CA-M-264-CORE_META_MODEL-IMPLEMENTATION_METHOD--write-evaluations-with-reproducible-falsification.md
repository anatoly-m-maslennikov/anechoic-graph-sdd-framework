---
subjects:
  active: ANECHOIC_MODEL <+ Atom/(.Header.Role := Evaluation)
  passive:
  - ANECHOIC_MODEL <+ Atom/(.Header.Role := Evaluation)
  - ANECHOIC_MODEL <+ Atom/(.Header.Role := Method)
  - ANECHOIC_MODEL <+ Atom.Content.Claim.Prose Claim
  - ANECHOIC_MODEL <+ Atom.Header.Tier
  - ANECHOIC_MODEL <+ CFEL > Relation//evaluation_for
version: 28
updated_at: 2026-11-02 00:18:22 +0400
relations: {}
atom_id: CA-M-264
current_scope_unit: CORE_META_MODEL
claim_target_scope_unit: CORE_META_MODEL
status: Draft
tier: 3
role: Method
form: Implementation Method
---
## Summary

Write evaluations with reproducible falsification

## Claim

### Prose Claim

Applicability: authoring or maintaining an Evaluation.

**to** write **or** maintain an Evaluation, identify its checked authority **and** Scope, select a suitable test technique, specify recoverable inputs, procedure, **and** observable falsifying conditions, **and** preserve the distinction between foundational evaluation authority, independent shared evaluation criteria **where** they are independently governed, **and** concrete evaluation criteria; keep writing techniques, test frameworks, **and** authoring conventions **in** Method authority rather than treating them as test results.

