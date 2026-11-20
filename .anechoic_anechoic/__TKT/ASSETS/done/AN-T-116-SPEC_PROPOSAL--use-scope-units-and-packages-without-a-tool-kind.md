---
identity:
  atom_id: AN-T-116
context:
  container:
    component: C00
  tier: 3
  template: Spec Proposal
state:
  status: done
  version: 3
  updated_at: 2026-11-02 15:49:28 +0400
---
# Summary

Use Scope Units and Packages without a Tool kind

## Decision

Tool is not needed as a separate primary kind. Specific Tools are organized as Scope Unit instances; their implementation uses Packages and the existing Module, Code Unit, Prompt and Asset kinds. Do not add a universal Tool Type or Tool property to all Scope Units.

R2197 is a retirement candidate for the adoption pass, not an active source deletion. R2205 machine-readable Self Description meaning is preserved by the new Engineering API Self Documentation Definition. R2204 Effect Result still needs a precise destination and remains explicitly unresolved; removing Tool from the model does not authorize dropping useful result-contract meaning.

## State

Model/Definition preparation only. Current methodology, Engine code and runtime are unchanged.
