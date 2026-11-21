---
atom_family: SPEC
atom_id: AN-S-3183
structure:
  container:
    component: C14
  tier: 3
context:
  lens: QA
state:
  status: active
  version: 1
  updated_at: '2026-11-21T15:23:48+00:00'
---
## Summary

Keep Engine source free of prose comments

## Claim

### Prose Claim

Engine source and tests must contain no prose comments. Keep comment syntax only when the interpreter, build tools, or static analyzers use it. Examples include shebangs, encoding declarations, type annotations, and lint suppressions that apply to the code.

The full test suite must report ordinary comments by file and line and fail without changing source. An explicit purge must preserve code behavior, string literals, docstrings, and required directives.
