---
atom_family: SPEC
atom_id: AN-S-4952
container:
  component: C90
tier: 0
context:
  template: component_contract
  lens: DES
relations:
  ANSWERS:
  - AN-S-4937
state:
  status: draft
  version: 1
  updated_at: '2026-11-26T00:00:00Z'
---

## Summary

Form a source-linked diagnostic.

## Guarantee

Form a diagnostic from the source, field, and message of a finding.

## Claim

### Formal Claim

```python trace
declare_trace_contract(
    action='finding',
    output='reported',
    must_effect=(('C90.source_diagnostic', 'formed'),),
)
```
