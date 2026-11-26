---
atom_family: SPEC
atom_id: AN-S-2313
container:
  component: C9
tier: 4
context:
  lens: QA
state:
  status: "archived"
  version: 2
  updated_at: "2026-11-25T20:57:09.420793+00:00"
---
## Summary

Validate Atom Claims and derived Projections

## Claim

### Prose Claim


active and draft Atom Claims, their Summaries, and requested Translation and terminology Projections.


**every** active **or** draft Atom **contains** **`=1`** human-readable Claim that expresses one precise contribution and follows the applicable ASD-STE100-aligned Atom prose profile **and** a source-faithful Summary. requested Translation **and** terminology Projections preserve their source meaning; their absence **when** **not** requested is **not** an Atom defect.

## Details

### Test case

create valid active **and** draft Atom Claims for **every** admitted Content Role. include fixtures with no requested Translation **or** terminology Projection **and** fixtures with requested Projections. derive a candidate Summary during Atom creation, **then** retain it for checks of subsequent Revisions under AN-S-1604. derive requested Translation **and** terminology Projections twice **without** regenerating the existing Atom's Summary. **then** introduce ambiguity, an unstated participant, two independent Claims, an added Projection meaning, an independent vocabulary entry, **and** a confidence result below the effective Confidence Threshold resolved according **to** CA-M-271-CORE_META_MODEL-IMPLEMENTATION_METHOD--resolve-confidence-thresholds-by-source-precedence.

### Acceptance criteria

**every** valid fixture has **`=1`** precise interpretation, a source-faithful Summary, **and** reproducible Projections **when** requested. no fixture fails merely because an optional Projection was **not** requested. **every** invalid fixture fails. a confidence result below the effective Confidence Threshold leaves the Atom unchanged **and** requests Operator disposition. changing the applicable Operator input, Plan override, enclosing Hub override, **or** Framework Instance Settings default changes the checked threshold according **to** CA-M-271-CORE_META_MODEL-IMPLEMENTATION_METHOD--resolve-confidence-thresholds-by-source-precedence **without** retaining a fixed percentage gate.

### Failure disposition

record a Concern naming the affected Claim **or** Projection.
