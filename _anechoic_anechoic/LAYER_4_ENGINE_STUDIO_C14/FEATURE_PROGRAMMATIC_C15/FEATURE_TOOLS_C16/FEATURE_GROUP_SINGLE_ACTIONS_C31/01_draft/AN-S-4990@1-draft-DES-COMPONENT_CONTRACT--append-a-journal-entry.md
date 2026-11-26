---
atom_family: SPEC
atom_id: AN-S-4990
container:
  component: C38
tier: 0
context:
  template: component_contract
  lens: DES
relations:
  ANSWERS:
  - AN-S-3077
state:
  status: draft
  version: 1
  updated_at: '2026-11-26T00:00:00+00:00'
---

## Summary

Append a journal entry.

## Guarantee

The successful Append reports the entry as appended. The input shape, selection rules, failure behavior and underlying I/O effects remain open.

This Draft proposes only this successful outcome under AN-S-2816@1-draft; it does not establish runtime behavior.

## Claim

### Formal Claim

```python trace
declare_trace_contract(
    action='append_journal_entry', output='entry_appended',
    must_effect=(('journal_entry', 'appended'),),
)
```
