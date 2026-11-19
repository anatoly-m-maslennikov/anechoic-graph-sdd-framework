---
identity:
  atom_id: CA-E-830
  ref_id: CA-E-830
context:
  role: evaluation
  form: Eval Case
  container:
    scope_unit: CA-SU-45
  tier: 5
  topics:
    main_subject: PROJECT STRUCTURE//ANECHOIC <+ Aspects <+ Engineering <+ Quality
      <+ Traceability
relations:
  evaluation_for:
  - CA-M-1015
state:
  version: 1
  status: active
  updated_at: '2026-11-13T18:17:34.949828+00:00'
destination:
  file:
    name: CA-E-830-WORKBENCH_BACKEND-EVAL_CASE--verify-workbench-spec-trace-indexing-and-lookup.md
    path: .anechoic_anechoic/CA-SU-14_LAYER_2_FRAMEWORK_ENGINE/CA-SU-15_FEATURE_PROGRAMMATIC/CA-SU-20_FEATURE_APPS/CA-SU-43_APP_WORKBENCH/CA-SU-45_FEATURE_WORKBENCH_BACKEND/06_evaluation
---
## Summary

Verify Workbench spec trace indexing and lookup

## Claim scope

The Workbench pilot and its public read-only query interface.

## Claim

### Prose Claim

Use a disposable Project to verify that Workbench publishes exact spec-trace pins and returns the expected owners for each lookup.

- At startup, query both trace tables. Check Package and Module paths and their immediate containers, including objects with zero pins and a same-named Package and Module. Verify a pin to an Archived revision remains visible with the Archive body unloaded.
- Create, edit, move, rename, and delete traced files and owners through the watcher. Verify a Package trace edit updates only that Package’s pins. A malformed trace removes all of its pins and reports the path and error. A full reread restores the same rows as a clean startup.
- Query in both directions, from an exact Atom ID and Version to its owners and from an owner to its pins. Check direct and subtree coverage separately. A Package with only Applies pins has zero implementation coverage.
- For one target Atom, look up owners by its Scope Unit, exact main Subject, and direct Atom dependencies. Use a fixture with a match from each search, an owner found by two searches, and a versioned dependency whose other revision has a different owner. Return each owner once with every matching reason. List applicable standards separately. Treat an unloaded Archive pin as unverified and report a Scope Unit with no mapped owners.