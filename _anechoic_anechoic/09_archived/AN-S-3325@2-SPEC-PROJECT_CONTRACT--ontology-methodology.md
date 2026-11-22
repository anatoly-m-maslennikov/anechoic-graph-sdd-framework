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
  status: archived
  version: 2
  updated_at: '2026-11-22T11:00:54.983176+00:00'
relations:
  ADVANCES:
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

Keep ANECHOIC-owned repository files in `.anechoic_*` directories. The
Package Spec Binding sidecar is the sole exception. Place it at the
Package root as `<package folder name>__spec_bind.yaml`.
