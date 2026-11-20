---
identity:
  atom_id: AN-S-2580
context:
  container:
    component: C9
  tier: 3
  lens: DES
state:
  status: active
  version: 39
  updated_at: 2026-11-02 19:44:26 +0400
---
## Summary

Register Type Values for Evaluation Atoms

## Claim

### Prose Claim


internal values of `Atom/(.Header.Role := Evaluation).Header.Form`.


Policy, Eval Case, QA Case, **and** Evaluation Control **must** be registered as internal values of `Atom/(.Header.Role := Evaluation).Header.Form`.

## Details

Eval Case is defined by CA-R-2116@9. QA Case remains registered for existing Atoms pending individually evidenced migration; this registration does not require bulk reclassification. Evaluation Control remains a distinct specific Type.
