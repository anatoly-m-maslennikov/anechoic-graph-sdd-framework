---
atom_family: SPEC
atom_id: AN-S-4994
container:
  component: C41
tier: 0
context:
  template: component_contract
  lens: DES
relations:
  ANSWERS:
  - AN-S-3074
state:
  status: draft
  version: 1
  updated_at: '2026-11-26T00:00:00+00:00'
---

## Summary

Submit and aggregate a batch.

## Guarantee

The successful outcome reports aggregated batch results after job submission. Scheduling is asynchronous and independent of the caller. Input shape, aggregation rules, failure behavior and other effects remain open.

This Draft proposes only this successful outcome under AN-S-2814@1-draft; it does not establish runtime behavior.

## Claim

### Formal Claim

```python trace
declare_trace_contract(
    action='submit_and_aggregate_batch', output='batch_aggregated',
    must_effect=(('batch_jobs', 'submitted'), ('batch_results', 'aggregated')),
    must_precede=((('batch_jobs', 'submitted'), ('batch_results', 'aggregated')),),
)
```
