---
identity:
  atom_id: AN-T-1149
context:
  container:
    component: C00
  tier: 3
  template: Spec Proposal
state:
  status: active
  version: 2
  updated_at: 2026-11-02 15:49:28 +0400
---
# Summary

Refine Code Units, Packages and file-level Modules

## Decisions

Use Code Unit, not bare Unit, to distinguish it from Scope Unit. Class and Function are narrower kinds of Code Unit: Code Unit/Class and Code Unit/Function. They are not replaced by Scope Unit or discarded merely because the old Code branch changed.

Package contains nested Packages and Modules. Since both kinds already have declarations, use Package >@(Package) and Package >@(Module) for reuse. A Module is a file-level Code component represented by one File Carrier. This is the model's granularity convention, not a claim that every language uses the word Module in exactly the same way. Earlier permission for Module to exist outside Package remains: a direct Code > Module declaration is retained.

Folders that form logical collections of Modules/Packages can represent Packages through Directory Carriers. Directory Carrier and Package remain distinct. A folder's mere existence does not automatically establish a logical Package. The Directory binding is prepared as a Delivery Draft, not applied to the filesystem.

## Remaining choice

Whether every Code Unit must belong to a Module, or may also exist directly under Code, is the pending Operator question. Do not infer it from file placement. The partial Code Unit Draft records the decided name and subtypes while leaving that binding explicit for later refinement. Tool's disposition remains unresolved.

## State

This updates review Drafts only. No Current source, implementation file, Carrier, Tool or runtime is moved. Formal Claims remain R-only; M/E/D describe their contracts in prose.
