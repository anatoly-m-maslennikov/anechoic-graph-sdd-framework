---
atom_family: SPEC
atom_id: AN-S-372
container:
  component: C9
tier: 1
context:
  lens: DES
state:
  status: archived
  version: 18
  updated_at: 2026-10-24 01:37:42 +0400
---
## Summary

Distinguish enacted release and runtime facts from Operations authority

# Summary

Distinguish enacted release and runtime facts from Operations authority

## Scope

enacted release and runtime facts.

## Claim

successful **and** failed release **or** deployment events, deployed environment state, runtime health, **and** incidents **must** be treated as operational facts whose execution evidence **and** state changes are carried by Journal Records. these facts **and** Records are distinct from reusable Operations definitions **and** **must not** themselves establish **or** silently change Plan, Requirement, Method, Evaluation, Delivery, **or** Operations authority.

## Details
