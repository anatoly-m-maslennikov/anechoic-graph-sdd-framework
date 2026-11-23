---
atom_family: TKT
atom_id: AN-T-116
container:
  component: C00
priority: 2
context:
  template: spec_proposal
state:
  status: archived
  version: 2
  updated_at: 2026-10-29 21:51:04 +0400
---
## Summary

Use Scope Units and Packages without a Tool kind

# Summary

Use Scope Units and Packages without a Tool kind

## Decision

Tool is not needed as a separate primary kind. Specific Tools are organized as Scope Unit instances; their implementation uses Packages and the existing Module, Code Unit, Prompt and Asset kinds. Do not add a universal Tool Type or Tool property to all Scope Units.

R2197 is a retirement candidate for the adoption pass, not an active source deletion. R2205 machine-readable Self Description meaning is preserved by the new Engineering API Self Documentation Definition. R2204 Effect Result still needs a precise destination and remains explicitly unresolved; removing Tool from the model does not authorize dropping useful result-contract meaning.

## State

Model/Definition preparation only. Current methodology, Engine code and runtime are unchanged.
