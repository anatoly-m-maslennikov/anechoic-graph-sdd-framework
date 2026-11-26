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

Guide subject tree and compact Spec rewrites

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

```python
component_workflow(
    component='C56',
    action='compact_spec_rewrite',
    machine={
        'id': 'c56_compact_spec_rewrite',
        'initial': 'idle',
        'states': {
            'idle': {'on': {
                'rewrite_requested': {'target': 'source_guidance', 'guard': {'type': 'matchesTrace', 'params': {'kind': 'trigger'}}},
            }},
            'source_guidance': {'on': {
                'current_source_guidance_provided': {'target': 'gate_guidance', 'guard': {'type': 'matchesTrace', 'params': {'kind': 'effect', 'target': 'current_source_guidance', 'outcome': 'provided'}}},
            }},
            'gate_guidance': {'on': {
                'size_gate_guidance_provided': {'target': 'response', 'guard': {'type': 'matchesTrace', 'params': {'kind': 'effect', 'target': 'size_gate_guidance', 'outcome': 'provided'}}},
            }},
            'response': {'on': {
                'draft_returned': {'target': 'done', 'guard': {'type': 'matchesTrace', 'params': {'kind': 'output', 'outcome': 'draft_returned'}}},
                'held_returned': {'target': 'done', 'guard': {'type': 'matchesTrace', 'params': {'kind': 'output', 'outcome': 'held_returned'}}},
            }},
            'done': {'type': 'final'},
        },
    },
)
```


## Details

Process parents first. Rebuild from pinned sources, check the inputs, and compare the sources. If inputs are missing, report them. If comparison is uncertain, record questions and keep the gate open.

Write the Draft, record source-to-Draft mapping, and verify it before reporting it. Report a write or verification failure. An open question permits a provisional Draft; use Current authority for unresolved parent decisions.

## Compact rewrite

Source coverage: `LAYER_4_ENGINE_STUDIO_C14/FEATURE_AGENTIC/FEATURE_PROMPTS/FEATURE_SUBJECT_TREE_ATOM_REWRITE_PROMPT/compact_spec_rewrite.prompt.md`.
The carrier guides the consumer and does not write Drafts or state. The output names the instructed response.

Use only the Current source Atom. Preserve Role and Form, keep the central Claim and essential support, and retain out-of-scope statements in Offtopic. Return a Draft with Summary, Claim, and Details when all size gates pass.

Exclude Offtopic from the gates. Apply the prompt's line-length and Form-specific Claim and Details limits. If a gate fails, remove the least essential in-scope support and recheck, up to five times. If a gate still fails, return Held and name it.
