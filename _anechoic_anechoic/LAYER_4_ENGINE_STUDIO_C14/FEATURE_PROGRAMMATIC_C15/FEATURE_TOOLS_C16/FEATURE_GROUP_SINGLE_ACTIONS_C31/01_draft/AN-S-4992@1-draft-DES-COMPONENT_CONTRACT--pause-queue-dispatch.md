---
atom_family: SPEC
atom_id: AN-S-4992
container:
  component: C40
tier: 0
context:
  template: component_contract
  lens: DES
relations:
  ANSWERS:
  - AN-S-3080
state:
  status: draft
  version: 1
  updated_at: '2026-11-26T00:00:00+00:00'
---

## Summary

Pause queue dispatch.

## Guarantee

The successful pause reports dispatch as paused and does not cancel running work. Queue selection, inputs, failure behavior and other effects remain open.

This Draft proposes only this successful outcome under AN-S-2816@1-draft; it does not establish runtime behavior.

## Claim

### Formal Claim

```python trace
declare_trace_contract(
    action='pause_queue_dispatch', output='dispatch_paused',
    must_effect=(('dispatch', 'paused'),),
    forbid_effect=('running_work_cancellation',),
)
```
