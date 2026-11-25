---
atom_family: SPEC
atom_id: AN-S-3077
container:
  component: C31
tier: 4
context:
  template: component_manifest
  lens: SPEC
state:
  status: draft
  version: 3
  updated_at: '2026-11-26T00:00:00+00:00'
---

## Summary

Declare JOURNAL_ACTIONS

## Purpose

Append one supplied entry to a Journal. C30 owns Journal I/O. Find and Fetch remain outside this narrow claim.

This is a Draft proposal based on AN-S-2816@1-draft.

## Formal manifest

```python
from anechoic.formal_claims import declare_entity
from anechoic.model import ComponentManifest

declare_entity(
    entity_name='Component Manifest',
    instance=ComponentManifest(
        component_id='C38', name='JOURNAL_ACTIONS', lens_whitelist=['DES'],
        boundaries={'io': {'server': {'append_journal_entry': {'outcomes': {
            'entry_appended': {'must_effect': [('journal_entry', 'appended')]},
        }}}}},
    ),
)
```
