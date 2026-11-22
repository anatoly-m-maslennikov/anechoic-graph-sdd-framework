---
atom_family: SPEC
atom_id: AN-S-3325
container:
  component: C00
tier: 0
context:
  template: project_contract
  lens: SPEC
state:
  status: active
  version: 4
  updated_at: '2026-11-22T11:59:13.546148+00:00'
relations:
  SERVES:
  - AN-S-1233
---
## Summary

Ontology + Methodology

## Inputs

The Operator supplies Project concepts, goals, existing Specification and
Realization, and a proposed change or task. The Operator selects one or
more repository roots.

## Guarantee

Represent Project information in versioned Specification Atoms and typed
relations. Return guidance for making and checking changes. Return
actionable findings for records that the Operator asks ANECHOIC to
validate. Resolve exact Specification revisions from implementation or
test evidence with trace bindings.

Read across each selected repository, including files outside
`.anechoic_*`. State which sources an analysis covered. Report exclusions,
unsupported inputs, and read failures that affect its result.

Place the Current Project Manifest and Project Goal at the repository
root for new Projects. Existing Projects can keep them in their
ANECHOIC control directory. Place each Package Spec Binding sidecar at
its Package root as `<package folder name>__spec_bind.yaml`. Keep all
other ANECHOIC-owned repository files in `.anechoic_*` directories.
