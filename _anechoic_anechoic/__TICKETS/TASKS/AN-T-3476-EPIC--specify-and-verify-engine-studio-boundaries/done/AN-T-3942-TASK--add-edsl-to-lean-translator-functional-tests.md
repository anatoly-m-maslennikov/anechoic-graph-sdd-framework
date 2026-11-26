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
  status: done
  version: 2
  updated_at: '2026-11-25T22:10:56+00:00'
---
## Summary

Add eDSL to Lean translator functional tests

## Work

Use a dedicated test package under Lean Translator. Keep hand-written
Lean expectations for each supported construct. Generate individual
constructs and combinations. Compare their meaning against the
independent expectations.

Include a typed guard in an ordering rule and a numeric bound on a
branch with an alternate exit. Target changed lowering rules. Keep
each minimized counterexample as a reproducible regression.

## Research

[PROGnosticator](https://futures.cs.utah.edu/papers/26FSE-a.pdf) ·
[OptiMuzz](https://kihongheo.kaist.ac.kr/publications/pldi25.pdf)

## Acceptance

The suite checks actual Lean output and catches a semantic mutation
that still compiles. The selected suite fails explicitly when Lean
is unavailable.

## Findings

The Lean Translator and Translation Validator functional packages
passed all six focused checks using Lean 4.31.0.
