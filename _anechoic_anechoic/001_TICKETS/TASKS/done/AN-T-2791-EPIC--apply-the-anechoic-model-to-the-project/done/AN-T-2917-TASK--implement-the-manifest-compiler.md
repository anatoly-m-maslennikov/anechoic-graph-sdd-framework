---
atom_family: TKT
atom_id: AN-T-2917
container:
  atom: AN-T-2791
priority: 2
context:
  template: task
state:
  status: done
  version: 1
  updated_at: '2026-11-20T12:10:17.230299+00:00'
---
## Summary

Implement the Manifest Compiler

## Work

Reuse the source watcher and Anechoic Python eDSL parser. Run compilation in a short-lived process. Generate small importable Model modules and validate Structure against that Model. Record the exact source revisions in the output.
