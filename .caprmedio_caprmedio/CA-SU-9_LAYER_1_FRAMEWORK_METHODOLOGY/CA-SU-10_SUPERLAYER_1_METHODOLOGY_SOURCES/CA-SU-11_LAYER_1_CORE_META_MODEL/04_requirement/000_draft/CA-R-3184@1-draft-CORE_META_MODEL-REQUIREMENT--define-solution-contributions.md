---
identity:
  atom_id: CA-R-3184
  ref_id: CA-R-3184@1-draft
context:
  container:
    scope_unit: CA-SU-11
  role: requirement
  form: requirement
  topics:
    main_subject: MODEL//CAPRMEDIO <+ Atom
  tier: 3
state:
  status: draft
  version: 1
  updated_at: '2026-11-18T22:05:01.702443+00:00'
destination:
  file:
    name: CA-R-3184@1-draft-CORE_META_MODEL-REQUIREMENT--define-solution-contributions.md
    path: .caprmedio_caprmedio/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-11_LAYER_1_CORE_META_MODEL/04_requirement/000_draft
---
## Summary

Define Solution contributions

## Claim

### Prose Claim

A Solution affects Specification and may begin with no supporting Atoms. A Solution, Decision, Standard, or Policy may declare `CONTRIBUTES_TO` a supported Solution; one Atom may support multiple Solutions and support may cross Component boundaries. Each explicit Atom-to-Atom relation has a derived reverse endpoint for the same direct pair. Validate the authored Solution-to-Solution support graph as acyclic using the directed dependency acyclicity check. A View may show transitive support.

## Details

Acceptance: Decision D in one Component can contribute to Solutions A and B in another; each Solution exposes D in its direct reverse endpoint. If S contributes to A and A contributes to B, B's direct inverse includes A, while a View may show S's transitive support. Accept an unsupported Solution; reject A contributes to B and B contributes to A.

Sources: CA-A-1462@1-draft, CA-P-3082@1. Task: CA-P-3082.
