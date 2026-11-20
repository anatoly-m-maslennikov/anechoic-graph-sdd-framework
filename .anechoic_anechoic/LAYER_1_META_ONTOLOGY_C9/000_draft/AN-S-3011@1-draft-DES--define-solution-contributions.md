---
identity:
  atom_id: AN-S-3011
context:
  container:
    component: C9
  tier: 3
  lens: DES
state:
  status: draft
  version: 1
  updated_at: '2026-11-18T22:05:01.702443+00:00'
---
## Summary

Define Solution contributions

## Claim

### Prose Claim

A Solution affects Specification and may begin with no supporting Atoms. A Solution, Decision, Standard, or Policy may declare `CONTRIBUTES_TO` a supported Solution; one Atom may support multiple Solutions and support may cross Component boundaries. Each explicit Atom-to-Atom relation has a derived reverse endpoint for the same direct pair. Validate the authored Solution-to-Solution support graph as acyclic using the directed dependency acyclicity check. A View may show transitive support.

## Details

Acceptance: Decision D in one Component can contribute to Solutions A and B in another; each Solution exposes D in its direct reverse endpoint. If S contributes to A and A contributes to B, B's direct inverse includes A, while a View may show S's transitive support. Accept an unsupported Solution; reject A contributes to B and B contributes to A.

Sources: CA-A-1462@1-draft, CA-P-3082@1. Task: CA-P-3082.
