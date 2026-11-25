---
atom_family: TKT
atom_id: AN-T-3942
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

Add eDSL to Lean translator functional tests

## Work

Add a dedicated test package under Lean Translator. Run emitted Lean
against independent expectations for representative declarations,
literal values, and a deliberately incorrect translation.

## Acceptance

The suite checks actual Lean output and catches a semantic mutation
that still compiles. The selected suite fails explicitly when Lean
is unavailable.

## Findings

The Lean Translator and Translation Validator functional packages
passed all six focused checks using Lean 4.31.0.
