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
  - AN-S-3293@8-draft
state:
  status: draft
  version: 5
  updated_at: '2026-11-25T00:00:00+00:00'
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
                'public_release_requested': {'target': 'validating', 'guard': {'type': 'matchesTrace', 'params': {
                    'kind': 'trigger', 'target': 'public_release', 'detail': {
                        'transport': 'cli', 'runner': 'uv', 'command': 'public',
                        'path': 'LAYER_3_DEVOPS_C80/LAYER_2_RELEASE_C27/release.py',
                    },
                }}},
            }},
            'validating': {'on': {
                'interrupted': {'target': 'interrupted', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'output', 'outcome': 'interrupted', 'detail': {'exit_code': 130}}}},
                'invalid_usage_reported': {'target': 'invalid_usage', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'output', 'outcome': 'invalid_usage', 'detail': {'exit_code': 2}}}},
                'arguments_admitted': {'target': 'comparing', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'effect', 'target': 'C64', 'outcome': 'succeeded'}}},
            }},
            'comparing': {'on': {
                'interrupted': {'target': 'interrupted', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'output', 'outcome': 'interrupted', 'detail': {'exit_code': 130}}}},
                'git_refs_and_version_resolved': {'target': 'selecting', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'effect', 'target': 'git_base_head', 'outcome': 'resolved'}}},
                'comparison_failed': {'target': 'failed', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'output', 'outcome': 'failed', 'detail': {'exit_code': 1}}}},
            }},
            'selecting': {'on': {
                'interrupted': {'target': 'interrupted', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'output', 'outcome': 'interrupted', 'detail': {'exit_code': 130}}}},
                'pinned_ticket_evidence_read': {'target': 'reporting', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'effect', 'target': 'C64'}}},
                'content_draft_pins_matched': {'target': 'rendering_drafts', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'effect', 'target': 'content_draft_commit_pins', 'outcome': 'matched'}}},
                'content_draft_invalid': {'target': 'failed', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'output', 'outcome': 'failed', 'detail': {'exit_code': 1}}}},
            }},
            'rendering_drafts': {'on': {
                'drafts_rendered': {'target': 'rendering_description', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'effect', 'target': 'release_drafts', 'outcome': 'rendered'}}},
                'rendering_failed': {'target': 'failed', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'output', 'outcome': 'failed', 'detail': {'exit_code': 1}}}},
                'interrupted': {'target': 'interrupted', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'output', 'outcome': 'interrupted', 'detail': {'exit_code': 130}}}},
            }},
            'rendering_description': {'on': {
                'description_returned': {'target': 'rendering_history', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'effect', 'target': 'pull_request_description', 'outcome': 'returned'}}},
                'rendering_failed': {'target': 'failed', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'output', 'outcome': 'failed', 'detail': {'exit_code': 1}}}},
                'interrupted': {'target': 'interrupted', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'output', 'outcome': 'interrupted', 'detail': {'exit_code': 130}}}},
            }},
            'rendering_history': {'on': {
                'history_returned': {'target': 'returning_drafts', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'effect', 'target': 'version_history', 'outcome': 'returned'}}},
                'rendering_failed': {'target': 'failed', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'output', 'outcome': 'failed', 'detail': {'exit_code': 1}}}},
                'interrupted': {'target': 'interrupted', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'output', 'outcome': 'interrupted', 'detail': {'exit_code': 130}}}},
            }},
            'returning_drafts': {'on': {
                'markdown_drafts_returned': {'target': 'completed', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'output', 'outcome': 'completed', 'detail': {'exit_code': 0}}}},
            }},
            'reporting': {'on': {
                'interrupted': {'target': 'interrupted', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'output', 'outcome': 'interrupted', 'detail': {'exit_code': 130}}}},
                'evidence_handoff_returned': {'target': 'input_required', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'output', 'outcome': 'input_required', 'detail': {'exit_code': 1}}}},
            }},
            'input_required': {'type': 'final'},
            'completed': {'type': 'final'},
            'failed': {'type': 'final'},
            'invalid_usage': {'type': 'final'},
            'interrupted': {'type': 'final'},
        },
    },
)
```
