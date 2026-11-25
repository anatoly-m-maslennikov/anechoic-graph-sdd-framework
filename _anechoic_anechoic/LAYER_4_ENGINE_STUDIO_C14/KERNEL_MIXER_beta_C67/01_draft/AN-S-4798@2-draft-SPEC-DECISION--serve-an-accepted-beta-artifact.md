---
atom_family: SPEC
atom_id: AN-S-4798
container:
  component: C67
tier: 1
context:
  template: DECISION
  lens: SPEC
relations:
  IS_SOLUTION_FOR:
  - AN-S-4797@3-draft
state:
  status: draft
  version: 2
  updated_at: '2026-11-25T10:46:01Z'
---
## Summary

Serve an accepted Beta artifact.

## Claim

### Prose Claim

For a successful Model or Structure request, the Database Server checks the
Project instance. The selected Host reads the artifact and generation ID
under the same lock. The Server returns the bytes and generation ID together.

### Formal Claim

```python
component_workflow(
    component='C67',
    action='beta_artifact_read',
    machine={
        'id': 'c67_beta_artifact_read',
        'initial': 'idle',
        'states': {
            'idle': {'on': {
                'artifact_requested': {'target': 'checking_instance', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'trigger'}}},
            }},
            'checking_instance': {'on': {
                'binding_matched': {'target': 'reading', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'effect', 'target': 'project_binding', 'outcome': 'matched'}}},
                'foreign_instance': {'target': 'rejected', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'output', 'outcome': 'foreign_instance'}}},
            }},
            'reading': {'on': {
                'no_generation': {'target': 'rejected', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'output', 'outcome': 'no_generation'}}},
                'structure_from_accepted_rows_read': {'target': 'reading_structure_pair', 'guard': {
                    'type': 'matchesTrace', 'params': {
                        'kind': 'effect', 'target': 'structure', 'outcome': 'rendered_from_accepted_rows',
                        'detail': {'component': 'C71', 'action': 'beta_database_artifact_read',
                                   'output': 'structure_returned'},
                    },
                }},
                'accepted_artifact_read': {'target': 'responding', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'effect', 'target': 'artifact_content_generation', 'outcome': 'paired',
                     'detail': {'component': 'C71', 'action': 'beta_database_artifact_read', 'output': 'succeeded'}}}},
            }},
            'reading_structure_pair': {'on': {
                'accepted_structure_pair_read': {'target': 'responding_structure', 'guard': {
                    'type': 'matchesTrace', 'params': {
                        'kind': 'effect', 'target': 'artifact_content_generation', 'outcome': 'paired',
                        'detail': {'component': 'C71', 'action': 'beta_database_artifact_read',
                                   'output': 'structure_returned'},
                    },
                }},
            }},
            'responding_structure': {'on': {
                'structure_and_generation_paired': {'target': 'reporting_structure', 'guard': {
                    'type': 'matchesTrace', 'params': {
                        'kind': 'effect', 'target': 'artifact_response', 'outcome': 'paired',
                    },
                }},
            }},
            'reporting_structure': {'on': {
                'structure_returned': {'target': 'succeeded', 'guard': {
                    'type': 'matchesTrace', 'params': {'kind': 'output', 'outcome': 'structure_returned'},
                }},
            }},
            'responding': {'on': {
                'artifact_and_generation_paired': {'target': 'reporting', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'effect', 'target': 'artifact_response', 'outcome': 'paired'}}},
            }},
            'reporting': {'on': {
                'artifact_returned': {'target': 'succeeded', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'output', 'outcome': 'succeeded'}}},
            }},
            'succeeded': {'type': 'final'},
            'rejected': {'type': 'final'},
        },
    },
)
```

## Details

The trace models the successful read, foreign-Project rejection, and the
pre-admission result. It leaves the exact identity and byte values, the lock,
and runtime conformance unresolved.


## Source alignment to resolve

AN-S-4797@3-draft retains AN-S-4797@2-draft's Structure reconstruction
from accepted rows. This Solution retains AN-S-4798@1's successful
artifact-read account. The sources do not establish how those accounts
fit together. Resolve that question before activation.

The `structure_returned` case models the existing accepted-row Draft
proposal. Its comparison checks how that proposal fits C71. The source
alignment and read sequence require review before adoption. Admission
atomicity and exact value equality remain outside the checks.
