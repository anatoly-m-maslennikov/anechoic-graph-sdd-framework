---
atom_family: SPEC
atom_id: AN-S-3373
container:
  component: C48
tier: 1
context:
  template: DECISION
  lens: DES
relations:
  IS_SOLUTION_FOR:
  - AN-S-3307@3-draft
state:
  status: draft
  version: 3
  updated_at: '2026-11-25T12:00:00Z'
---

## Summary

Read a Workbench MCP App resource

## Claim

### Prose Claim

A resource request selects the bundled compatibility or Workbench HTML and
returns it with the MCP App MIME type.

### Formal Claim

```python
component_workflow(
    component='C48',
    action='codex_extension_read_resource',
    machine={
        'id': 'c48_codex_extension_read_resource',
        'initial': 'idle',
        'states': {
            'idle': {'on': {
                'resource_read_requested': {'target': 'reading', 'guard': {
                    'type': 'matchesTrace', 'params': {
                        'kind': 'trigger',
                    },
                }},
            }},
            'reading': {'on': {
                'html_loaded': {'target': 'responding', 'guard': {
                    'type': 'matchesTrace', 'params': {
                        'kind': 'effect', 'target': 'C48.selected_bundle', 'outcome': 'loaded',
                    },
                }},
                'unknown_or_unavailable_resource': {'target': 'failed_response', 'guard': {
                    'type': 'matchesTrace', 'params': {
                        'kind': 'effect', 'target': 'C48.resource_error', 'outcome': 'unknown_ui_resource',
                        'detail': {
                            'code': -32002,
                            'message': 'Unknown UI resource',
                        },
                    },
                }},
            }},
            'responding': {'on': {
                'resource_returned': {'target': 'succeeded_response', 'guard': {
                    'type': 'matchesTrace', 'params': {
                        'kind': 'effect', 'target': 'C48.resource_html', 'outcome': 'returned',
                        'detail': {
                            'mime': 'text/html;profile=mcp-app',
                        },
                    },
                }},
            }},
            'succeeded': {'type': 'final'},
            'failed': {'type': 'final'},
            'succeeded_response': {'on': {
                'resource_succeeded': {'target': 'succeeded', 'guard': {
                    'type': 'matchesTrace', 'params': {
                        'kind': 'output', 'outcome': 'succeeded',
                    },
                }},
            }},
            'failed_response': {'on': {
                'resource_failed': {'target': 'failed', 'guard': {
                    'type': 'matchesTrace', 'params': {
                        'kind': 'output', 'outcome': 'failed',
                    },
                }},
            }},
        },
    },
)
```

## Details

This Solution defines the expected event sequence for the selected workflow.
Trace conformance requires recorded evidence.
