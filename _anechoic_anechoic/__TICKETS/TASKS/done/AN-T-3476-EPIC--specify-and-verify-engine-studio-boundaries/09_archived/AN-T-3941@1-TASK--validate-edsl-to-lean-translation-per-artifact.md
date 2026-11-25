---
atom_family: TKT
atom_id: AN-T-3941
container:
  atom: AN-T-3476
priority: 2
context:
  template: task
  label: Task
state:
  status: archived
  version: 1
  updated_at: '2026-11-25T20:36:59+00:00'
---
## Summary

Validate eDSL to Lean translation per artifact

## Work

Check generated Lean against expectations derived from the supported
eDSL input independently of the emitter. Start with a small supported
scope and report gaps.

## Acceptance

A syntactically valid translation that changes a supported meaning
fails validation. Report unsupported input. Implementation conformance
remains in its own Epic.

## Findings

The trace chain validates evaluated Lean JSON declarations before
comparing the pinned Specs. Executable shape and framing projections
remain unresolved in artifact validation.
