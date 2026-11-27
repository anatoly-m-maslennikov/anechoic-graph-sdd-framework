---
atom_family: SPEC
atom_id: AN-S-3381
container:
  component: C64
tier: 1
context:
  template: DECISION
  lens: DevOps
relations:
  IS_SOLUTION_FOR:
  - AN-S-3293@7
state:
  status: "active"
  version: 4
  updated_at: "2026-11-26T16:43:14.701559+00:00"
---

## Summary

Prepare public release evidence or render drafts from reviewed content.

## Claim

### Prose Claim

Public Release pins the Git comparison and either returns completed ticket
evidence for review or renders PR and Version History drafts from a
matching content draft.

### Formal Claim

```python
component_workflow(
    component='C64',
    action='prepare_public_release',
    machine={
        'id': 'c64_prepare_public_release',
        'initial': 'idle',
        'states': {
            'idle': {'on': {
                'public_release_requested': {'target': 'comparing', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'trigger'}}},
            }},
            'comparing': {'on': {
                'git_refs_and_version_resolved': {'target': 'selecting', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'effect', 'target': 'C64'}}},
                'comparison_failed': {'target': 'failed', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'output', 'outcome': 'failed'}}},
            }},
            'selecting': {'on': {
                'pinned_ticket_evidence_read': {'target': 'reporting', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'effect', 'target': 'C64'}}},
                'markdown_drafts_returned': {'target': 'completed', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'output', 'outcome': 'completed'}}},
                'content_draft_invalid': {'target': 'failed', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'output', 'outcome': 'failed'}}},
            }},
            'reporting': {'on': {
                'evidence_handoff_returned': {'target': 'input_required', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'output', 'outcome': 'input_required'}}},
            }},
            'input_required': {'type': 'final'},
            'completed': {'type': 'final'},
            'failed': {'type': 'final'},
        },
    },
)
```

## Details

This Solution defines the expected event sequence for the selected workflow.
Trace conformance requires recorded evidence.
