---
atom_family: TKT
atom_id: AN-T-3945
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

Check Markdown extraction and eDSL parsing

## Work

Check the path from a pinned Markdown carrier to the admitted AST.
Use independent expectations for recognized declaration fences,
malformed inputs, and clauses that could be omitted during parsing.

## Acceptance

Extraction and parsing checks detect dropped declarations or
clauses. Reports state where the lowering guarantee begins and link
each failure to its source.

## Research

[Verified parser validation](https://gallium.inria.fr/~fpottier/publis/jourdan-leroy-pottier-validating-parsers.pdf)
