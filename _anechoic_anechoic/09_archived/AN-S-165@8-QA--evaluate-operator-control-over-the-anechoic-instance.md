---
atom_family: SPEC
atom_id: AN-S-165
container:
  component: C00
tier: 4
context:
  lens: QA
state:
  status: archived
  version: 8
  updated_at: 2026-10-23 03:17:34 +0400
---
## Summary

Evaluate Operator control over the ANECHOIC instance

# Evaluate Operator control over the ANECHOIC instance

## Claim checked

the declared Operators collectively retain control over **every** governed part of the ANECHOIC instance **and** can use the instance **to** change the Project within their current authority.

## Applicable conditions

apply **after** a material change **to** the ANECHOIC instance, its authority, **or** the mechanisms through which Operators change the Project.

## Check

enumerate **every** governed part of the current ANECHOIC instance **and** **every** Operator-authorized Project-change operation exposed through it. for **every** part, demonstrate that the declared Operators can collectively inspect **and** direct it under their current authority. for **every** operation, demonstrate that **`>=1`** admissible Operator-controlled path can apply the change **to** the Project.

## Acceptance

pass **only** **when** **every** governed instance part is collectively inspectable **and** directable by the declared Operators **and** **every** admitted Project-change operation has an admissible Operator-controlled execution path.

## Failure

fail **and** report **every** uncontrolled instance part **or** unavailable Operator-controlled Project-change path.
