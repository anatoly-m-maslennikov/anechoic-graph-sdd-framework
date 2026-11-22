---
atom_family: SPEC
atom_id: AN-S-165
container:
  component: C14
tier: 5
context:
  lens: QA
state:
  status: draft
  version: 29
  updated_at: '2026-11-14T19:13:28.300269+00:00'
---
## Summary

Evaluate Operator control over the ANECHOIC instance

## Claim

### Prose Claim


the declared Operators collectively retain control over **every** governed part of the ANECHOIC instance **and** can use the instance **to** change the Project within their current authority.

## Applicable conditions

apply **after** a material change **to** the ANECHOIC instance, its authority, **or** the mechanisms through which Operators change the Project.

## Check

enumerate **every** governed part of the current ANECHOIC instance **and** **every** Operator-authorized Project-change operation exposed through it. for **every** part, demonstrate that the declared Operators can collectively inspect **and** direct it under their current authority. Demonstrate at least one exposed Operator-authorized Project-change operation. for **every** operation, demonstrate that **`>=1`** admissible Operator-controlled path can apply the change **to** the Project.

## Acceptance

pass **only** **when** **every** governed instance part is collectively inspectable **and** directable by the declared Operators **and** at least one Operator-authorized Project-change operation is exposed **and** **every** admitted Project-change operation has an admissible Operator-controlled execution path.

## Failure

fail **and** report **every** uncontrolled instance part **or** unavailable Operator-controlled Project-change path. If no authorized operation is exposed, fail and report that no usable Project-change path was demonstrated.
