---
atom_family: TKT
atom_id: AN-T-1479
container:
  atom: AN-T-1482
priority: 2
context:
  template: task
state:
  status: canceled
  version: 1
  updated_at: '2026-11-20T20:06:18.300250+00:00'
---
## Summary

Align implementation Workflow with Current Steps

## Objective

Align the implementation Workflow’s prompt bindings and implementation with its Current methodology. The Operator deferred this repair to the Engine Epic; it is outside the Scope Unit source cutover.

## Details

The implementation source roster still names archived Steps CA-O-091, CA-O-092, CA-O-093 and CA-O-095. The Current CA-O-016 Workflow uses CA-O-231, CA-O-232, CA-O-233 and CA-O-234 instead. These replacements also change shared-context behavior, so do not treat them as filename aliases.

Review the Current Step Claims, update the prompt and runtime bindings accordingly, and test that behavior. Use Current authoritative sources, not applied/projection copies or frozen old bindings. Do not restore the retired Steps or add business rules not declared in Current methodology.
