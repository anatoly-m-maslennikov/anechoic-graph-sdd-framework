---
atom_family: SPEC
atom_id: AN-S-3080
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

Declare QUEUE_ACTIONS

## Purpose

Pause dispatch through the direct queue-control path. This path is not queued on a paused queue. Pausing does not cancel running work.

This is a Draft proposal based on AN-S-2816@1-draft.

## Formal manifest

```python
from anechoic.formal_claims import declare_entity
from anechoic.model import ComponentManifest

declare_entity(
    entity_name='Component Manifest',
    instance=ComponentManifest(
        component_id='C40', name='QUEUE_ACTIONS', lens_whitelist=['DES'],
        boundaries={'io': {'server': {'pause_queue_dispatch': {'outcomes': {
            'dispatch_paused': {'must_effect': [('dispatch', 'paused')], 'forbid_effect': ['running_work_cancellation']},
        }}}}},
    ),
)
```
