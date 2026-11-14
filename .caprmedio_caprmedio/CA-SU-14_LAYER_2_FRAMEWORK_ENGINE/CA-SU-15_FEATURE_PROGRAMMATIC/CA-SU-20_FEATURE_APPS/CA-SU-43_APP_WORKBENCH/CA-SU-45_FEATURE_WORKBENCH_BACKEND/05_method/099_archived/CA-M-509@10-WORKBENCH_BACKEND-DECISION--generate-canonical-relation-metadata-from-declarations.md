---
identity:
  ref_id: CA-M-509@10
  id: CA-M-509
context:
  container:
    scope_unit: CA-SU-45
  role: Method
  form: decision
  topics:
    main_subject: PROJECT STRUCTURE//CAPRMEDIO <+ Aspects <+ Engineering <+ Operation
      <+ Data Handling <+ Schema
    dependencies:
    - MODEL//CAPRMEDIO <+ CFEL <+ Relation
  tier: 3
state:
  status: archived
  version: 10
  updated_at: '2026-11-13T21:05:59.817802+00:00'
destination:
  file:
    name: CA-M-509@10-WORKBENCH_BACKEND-DECISION--generate-canonical-relation-metadata-from-declarations.md
    path: .caprmedio_caprmedio/CA-SU-14_LAYER_2_FRAMEWORK_ENGINE/CA-SU-15_FEATURE_PROGRAMMATIC/CA-SU-20_FEATURE_APPS/CA-SU-43_APP_WORKBENCH/CA-SU-45_FEATURE_WORKBENCH_BACKEND/05_method/099_archived
author: Anatoly Maslennikov
relations:
  method_for:
  - CA-R-2724
  IS_REPLACEMENT_FOR:
  - CA-D-705
  - CA-M-509
---
## Summary

Generate canonical relation metadata from declarations

## Claim

### Prose Claim

Build one Workbench relation registry from the Formal Claims of Current Requirement Relation Declarations. Record canonical names, inverse aliases, unqualified inverse bindings, and source Atom IDs and Versions. An inverse alias needs no separate Declaration.

#### Build and load

- In refresh mode, select inputs under CA-M-1011, including its first-refresh bootstrap. Generate deterministic JSON before fingerprinting the image and assembling its build context. Exclude changing timestamps from the registry fingerprint.
- In existing mode, use the checkout registry as is.
- Reject the image or package if the registry is missing or invalid, or if refresh fails.
- Load the registry at startup. Apply Declaration changes by refreshing the registry and rebuilding the image. Keep MCP tool discovery separate.

#### Read declarations

- Read only code blocks in `Content.Claim.Formal Claim` that the build-time compiler accepts. Ignore comments outside strings.
- Use source identity, lifecycle and provenance to select and bind inputs. Exclude Prose Claim, Semantics, Details, examples, Header Topics and qualified derivation rules from runtime relation facts.

#### Apply the registry

- Use exact model addresses. For carrier keys, accept a canonical name, a declared inverse alias or a unique case-folded spelling. Warn and omit ambiguous, unsupported or case-colliding links and bindings.
- Swap endpoints once for an explicit inverse. Resolve an unambiguous legacy inverse through its declared counterpart. Build each inverse view once.
- Read containment from effective `Header.Container`, including its Context layout. Resolve the Project root as `uppercase(Project prefix)-SU-00`.
- Keep references typed. When a supporting source changes, refresh only affected direct and derived facts, rows and hashes. Preserve source bytes and Versions.
