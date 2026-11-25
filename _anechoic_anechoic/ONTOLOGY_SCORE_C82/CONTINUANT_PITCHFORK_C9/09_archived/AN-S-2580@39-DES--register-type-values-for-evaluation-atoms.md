---
atom_family: SPEC
atom_id: AN-S-2580
container:
  component: C9
tier: 3
context:
  lens: DES
state:
  status: "archived"
  version: 39
  updated_at: "2026-11-25T22:50:30.275971+00:00"
---
## Summary

Register Type Values for Evaluation Atoms

## Claim

### Prose Claim


internal values of `Atom/(.Header.Role := Evaluation).Header.Form`.


Policy, Eval Case, QA Case, **and** Evaluation Control **must** be registered as internal values of `Atom/(.Header.Role := Evaluation).Header.Form`.

## Details

Eval Case is defined by CA-R-2116@9. QA Case remains registered for existing Atoms pending individually evidenced migration; this registration does not require bulk reclassification. Evaluation Control remains a distinct specific Type.
