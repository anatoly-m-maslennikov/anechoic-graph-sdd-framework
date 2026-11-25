---
atom_family: SPEC
atom_id: AN-S-4752
container:
  component: C56
tier: 1
context:
  template: decision
  lens: DES
relations:
  IS_SOLUTION_FOR:
  - AN-S-4751@2-draft
state:
  status: draft
  version: 2
  updated_at: '2026-11-25T10:52:49+00:00'
---

## Summary

Guide subject tree rewrite

## Claim

### Prose Claim

The prompt calls for parent-first processing, quark classification, source comparison, and source-to-Draft mapping. It instructs MCP Draft writes and verification, without itself performing them.

### Formal Claim

Source coverage: `LAYER_4_ENGINE_STUDIO_C14/FEATURE_AGENTIC/FEATURE_PROMPTS/FEATURE_SUBJECT_TREE_ATOM_REWRITE_PROMPT/subject_tree_atom_rewrite.prompt.md`.
The effects model guidance in the carrier. The output names the instructed operator report; it does not establish that a Draft was created, verified, or reported.

```python
component_workflow(
    component='C56',
    action='subject_tree_atom_rewrite',
    machine={
        'id': 'c56_subject_tree_atom_rewrite',
        'initial': 'idle',
        'states': {
            'idle': {'on': {
                'rewrite_requested': {'target': 'rebuild_guidance', 'guard': {'type': 'matchesTrace', 'params': {'kind': 'trigger'}}},
            }},
            'rebuild_guidance': {'on': {
                'rebuild_guidance_provided': {'target': 'traceability_guidance', 'guard': {'type': 'matchesTrace', 'params': {'kind': 'effect', 'target': 'rebuild_guidance', 'outcome': 'provided'}}},
            }},
            'traceability_guidance': {'on': {
                'traceability_guidance_provided': {'target': 'reporting', 'guard': {'type': 'matchesTrace', 'params': {'kind': 'effect', 'target': 'traceability_guidance', 'outcome': 'provided'}}},
            }},
            'reporting': {'on': {
                'verified_draft_reported': {'target': 'done', 'guard': {'type': 'matchesTrace', 'params': {'kind': 'output', 'outcome': 'verified_draft_reported'}}},
            }},
            'done': {'type': 'final'},
        },
    },
)
```

## Details

Process parents first. Rebuild from pinned sources, check the inputs, and compare the sources. If inputs are missing, report them. If comparison is uncertain, record questions and keep the gate open.

Write the Draft, record source-to-Draft mapping, and verify it before reporting it. Report a write or verification failure. An open question permits a provisional Draft; use Current authority for unresolved parent decisions.
