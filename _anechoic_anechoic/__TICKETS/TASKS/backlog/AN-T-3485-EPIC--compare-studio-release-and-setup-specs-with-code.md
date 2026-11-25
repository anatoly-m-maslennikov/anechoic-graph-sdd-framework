---
atom_family: TKT
atom_id: AN-T-3485
container:
  component: C14
priority: 2
context:
  template: task
  label: Epic
state:
  status: backlog
  version: 2
  updated_at: '2026-11-25T12:56:51+00:00'
---
## Summary

Compare Studio, Release, and Setup Specs with code

## Work

Start after AN-T-3476 completes formal validation. Use those exact
Manifest, Contract, and Solution pins. Generate Lean from the Studio,
Release, and Setup implementation and compare it with the Specs.
Record reproducible mismatches and unresolved code coverage.

## Earlier pilot evidence

Reviewed 51 manifests and 6 seeds. Found 35 current Contract and formal Solution pairs. Fourteen Lean blocks compile and 21 workflow declarations compile. Sixteen records lack executable evidence, including historical definitions.

The C910647071 throughput fixture is absent from the image workspace but present in the mounted Project. C30 has 8 normal and 110 prior cases. C76 has 14 actual source cases. C68 has 2 matched explicit failure traces.

The Studio scan covered 582 source files. It covered 4411 units, 5164 resolved calls, and 3995 unresolved effect cases. It found 1 permitted ambient read and output. The capture excludes tests, assets, and prompt Markdown.

A Lean 4.19 compatibility shim works in scratch. Full conformance remains unsupported.
