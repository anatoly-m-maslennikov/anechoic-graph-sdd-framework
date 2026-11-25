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
  status: done
  version: 2
  updated_at: '2026-11-25T22:10:56+00:00'
---
## Summary

Validate eDSL to Lean translation per artifact

## Work

Check the actual Lean artifact against expectations derived from the
admitted source independently of the emitter. Account for every
semantic clause in scope. Check declaration and trace artifacts.

Report omissions, unsupported constructs, and timeouts as unverified.
State bounds in the result and retain failing cases.

## Research

[Translation Validation](https://weizmann.elsevierpure.com/en/publications/translation-validation-2/) ·
[Alive2](https://pldi21.sigplan.org/details/pldi-2021-papers/5/Alive2-Bounded-Translation-Validation-for-LLVM) ·
[Crellvm](https://sf.snu.ac.kr/crellvm/) ·
[Trivet preprint](https://arxiv.org/abs/2609.19583)

## Acceptance

A syntactically valid translation that changes a supported meaning
fails validation. Report unsupported input. Implementation conformance
remains in its own Epic.

## Findings

The trace and shape chains validate evaluated Lean JSON declarations
before comparing pinned Specs. Shape validation checks Lean structure
metadata and projection types. Framing uses bounded witnesses and
reports unbounded equivalence as unverified.
