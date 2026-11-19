---
identity:
  atom_id: CA-R-3188
  ref_id: CA-R-3188@1-draft
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
  updated_at: '2026-11-18T22:05:13.637753+00:00'
destination:
  file:
    name: CA-R-3188@1-draft-CORE_META_MODEL-REQUIREMENT--define-package-visibility-and-consumer-rules.md
    path: .caprmedio_caprmedio/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-11_LAYER_1_CORE_META_MODEL/04_requirement/000_draft
---
## Summary

Define package visibility and consumer rules

## Claim

### Prose Claim

Component Packages and ordinary Packages can declare access boundaries. Omitted visibility defaults to internal for Component Packages, specified ordinary Packages, and ordinary Packages without a Spec, including explicit SPEC exports. Internal permits immediate parent and siblings; `internal: [parent]` permits only the immediate parent, and `internal: [siblings]` only immediate siblings. Public permits any caller. An explicit allowlist selects consumers for that entry; both visibility modes accept allowlists, and a Component ID selects its Component Package. Resolve parent and siblings in the package tree.

A caller may restrict dependencies using import allowlists or denylists. A Component’s rules apply to its own modules and ordinary Packages at every depth and are inherited throughout the child Component tree. Each import must pass the provider’s visibility and every applicable caller rule. An allowed external caller may directly access a child Package entry.

## Details

Acceptance: an unconfigured package permits an immediate sibling and rejects an unrelated package; `internal: [parent]` rejects a sibling; `public` permits an unrelated caller unless an applicable caller rule denies the import; `public: [C43]` permits C43 and rejects another caller. A parent Component denylist applies to nested ordinary Packages and a child Component even if their provider permits access.

Sources: CA-A-1463@1-draft. Task: CA-P-3084.
