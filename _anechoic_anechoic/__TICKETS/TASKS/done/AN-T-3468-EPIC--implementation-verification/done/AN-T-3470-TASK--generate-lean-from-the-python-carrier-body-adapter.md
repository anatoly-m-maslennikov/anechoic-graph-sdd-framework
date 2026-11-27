---
atom_family: TKT
atom_id: AN-T-3470
container:
  atom: AN-T-3468
priority: 2
context:
  template: task
  label: Task
state:
  status: done
  version: 1
  updated_at: '2026-11-26T16:39:58.756193+00:00'
---
## Summary

Generate Lean from the Python carrier body Adapter

## Work

After AN-T-3469, pin the real C30 `carrier_body__pub.py` source, exact symbols,
and source revision. Generate a separate Lean model for `frontmatter_bounds`
and `source_body` using pinned Python with Code Analysis facts and the Lean
harness. Keep implementation-side source and analysis separate from the exact
formal-side inputs: Adapter Manifest, Adapter Contract, and Adapter Solution
formal blocks only. Record generated facts and unsupported behavior.

## Acceptance

The generated model checks in Lean, identifies its source revision and input
locations, and marks behavior the generator cannot cover.
