---
atom_family: TKT
atom_id: AN-T-2987
container:
  atom: AN-T-2973
priority: 2
context:
  template: task
  label: Task
state:
  status: "done"
  version: 2
  updated_at: "2026-11-22T17:33:20.398873+00:00"
relations:
  IS_REFERENCE:
  - AN-T-1157@2
---

## Summary

Add Code Units and calls to the Realization Graph

## Work

- Add Classes, Functions, and Methods under their existing Module nodes.
- Publish statically resolved calls in Python, JavaScript, and TypeScript.
- Reuse the existing source capture, import resolution, and graph rebuild.

## Acceptance

Query Module membership and call sites in Beta. Check direct calls and
known imported aliases. Omit edges when a target is ambiguous.
