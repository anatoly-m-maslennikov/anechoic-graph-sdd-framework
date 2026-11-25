---
atom_family: TKT
atom_id: AN-T-3943
container:
  atom: AN-T-3476
priority: 2
context:
  template: task
  label: Task
state:
  status: done
  version: 1
  updated_at: '2026-11-25T22:10:56+00:00'
---
## Summary

Define typed source and target semantics

## Work

Define a small typed workflow representation and source and target
semantics. Cover guards, effect ordering, and observable outcomes
first. State the admitted AST boundary and the observable traces that
a translation must preserve.

## Acceptance

Expected semantics come from the admitted source independently of
the translator. The model distinguishes stale and current replies,
typed guard values, ordered effects, and alternate exits.

## Research

[CompCert](https://compcert.org/man/manual001.html) ·
[Vélus](https://velus.inria.fr/compiler.html) ·
[Lean-MLIR](https://arxiv.org/abs/2407.03685)
