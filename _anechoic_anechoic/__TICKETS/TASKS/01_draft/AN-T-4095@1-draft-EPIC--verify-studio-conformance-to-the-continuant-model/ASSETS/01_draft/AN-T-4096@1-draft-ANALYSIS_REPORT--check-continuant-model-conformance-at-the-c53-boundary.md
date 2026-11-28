---
atom_family: TKT
atom_id: AN-T-4096
container:
  atom: AN-T-4095
priority: 2
context:
  template: analysis_report
state:
  status: draft
  version: 1
  updated_at: '2026-11-28T08:48:01.247417+00:00'
---

## Summary

Check Continuant Model conformance at the C53 boundary

## Scope

AN-T-4095 pilots Project SPEC Axiom validation. The inputs are the
active Continuant Model, Project Config, and an existing Axiom carrier.
Stage 1 permits Studio changes inside Spec Engine.

## Results

- The compiler validated the source Model and two controlled Project
  Config variants in Lean. The actual Axiom Template is AN-C-3194@5.
  The baseline Model fingerprint is
  `dc0e1f83226a3d5f7ff259d3856d7b72836f262f17616b56c099ad75dbba5c04`.
- Changing the Axiom Tier in a source copy from 0 to 1 changed the Model
  fingerprint. The bound validator and lifecycle preflight then used
  1. The previous generation failed fingerprint validation.
- Removing the declared Tier default exposed a C53 fallback that
  supplied 0. C53 now leaves the default unset. Lifecycle preflight requires an
  explicit Tier for a Template with no Model default. The legacy path still handles older Model data.
- Four Unit and four Functional cases derived their Tier inputs and
  expectations from the two admitted Models. The Functional cases
  called the public bound Model validator. All eight passed.
- Lean compared the emitted Model Header predicate with the translated
  C53 membership check on the same four cases. A wrong value domain
  failed. A source check without Lean detected replacing the Model
  lookup with a hardcoded Tier domain.

## Findings outside Spec Engine

- An unbound Project SPEC lifecycle validator still uses a built-in
  Axiom Tier of 0. The read-only probe found this fallback after the
  admitted Axiom definition changed to Tier 1.
- C30's legacy fallback admits Ticket Status `active`, which is absent
  from the admitted Ticket Status domain.
- The Model supplies the custom `APPLIES` and `IS_APPLIED_BY` Relation
  names. Archive handling still contains four retired citation names.
  Keep archive compatibility under review before changing those
  paths.

## QA placement

Tier domain examples fit focused Unit and Functional checks.
Fingerprint verification fits the existing Static check for generated
Model artifacts. The Lean comparison requires the matching Autoform
and Lean tools, so keep it in the formal verification lane.

## Evidence and limits

Evidence is in this thread's `an-t-4095-stage-1` directory under
`conformance-cases.json`, `lean-comparison.json`,
`post-fix.log` and `outside-scope.json`.

The Lean comparison covers the Tier membership check after type
validation. The sampled source check covers that Model lookup.
Broader Atom axes, Templates, Relations, and Studio entry points
need their own conformance cases.
