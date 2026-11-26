---
atom_family: TKT
atom_id: AN-T-3973
container:
  atom: AN-T-3476
priority: 2
context:
  template: task
  label: Task
state:
  status: done
  version: 2
  updated_at: '2026-11-25T13:10:19+00:00'
---
## Summary

Translate formal boundary declarations to Lean

## Work

Translate Manifest, Contract, and Solution declarations from the Spec Engine eDSL into traceable Lean from one common model. Reject or report each unsupported declaration explicitly.

## Acceptance

Each Lean result traces to its source declaration and model; unsupported input cannot silently disappear or pass as a complete translation.

## Findings

Generated and evaluated Lean for 48 exact source chains. The output
includes each declaration's path, version, and digest. The report
identifies unsupported declarations and Components with missing
boundary authority.
