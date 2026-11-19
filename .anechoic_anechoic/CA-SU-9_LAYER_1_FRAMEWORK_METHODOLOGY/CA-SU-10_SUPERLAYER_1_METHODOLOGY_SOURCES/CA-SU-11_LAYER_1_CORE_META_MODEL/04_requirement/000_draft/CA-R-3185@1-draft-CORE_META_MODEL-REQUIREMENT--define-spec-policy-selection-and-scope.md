---
identity:
  atom_id: CA-R-3185
  ref_id: CA-R-3185@1-draft
context:
  container:
    scope_unit: CA-SU-11
  role: requirement
  form: requirement
  topics:
    main_subject: MODEL//ANECHOIC <+ Atom
  tier: 3
state:
  status: draft
  version: 1
  updated_at: '2026-11-18T22:05:04.589666+00:00'
destination:
  file:
    name: CA-R-3185@1-draft-CORE_META_MODEL-REQUIREMENT--define-spec-policy-selection-and-scope.md
    path: .anechoic_anechoic/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-11_LAYER_1_CORE_META_MODEL/04_requirement/000_draft
---
## Summary

Define Spec Policy selection and scope

## Claim

### Prose Claim

A Spec Policy directly affects Specification: it applies to matching Spec Atoms selected by its explicit `affects` property in its own Component and the full descendant Component tree. A filter may use criteria including Lens, Tier, Template, a Concern Path subtree, or logical Component name. `component.name` identifies the Component containing the selected Atom. For a child's Purpose and Manifest that is the parent Component. A parent Policy may constrain `io_allowance` on child Component Manifests it contains. An Atom may be affected by several Policies and Solutions; actors resolve conflicting claims as other Specification conflicts.

## Details

Acceptance: a Policy owned by A can select a matching Atom in descendant C, but not a matching Atom in a sibling outside A's tree. A Policy in parent A selecting `component.name: A` can match its contained Manifest describing child B; selecting B by that criterion does not match that Manifest. Multiple matching Policies remain applicable; selection alone establishes no extra precedence.

Sources: CA-A-1462@1-draft, CA-P-3082@1. Task: CA-P-3082.
