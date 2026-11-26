---
atom_family: SPEC
atom_id: AN-S-4748
container:
  component: C55
tier: 1
context:
  template: decision
  lens: DES
relations:
  IS_SOLUTION_FOR:
  - AN-S-4747@2-draft
state:
  status: draft
  version: 2
  updated_at: '2026-11-25T10:52:49+00:00'
---

## Summary

Guide autonomous atom rewrite

## Claim

### Prose Claim

The prompt requires exact source and model reads, bidirectional comparison, correction and recheck. Unresolved uncertainty is flagged and must not be reported as conforming.

### Formal Claim

Source coverage: `LAYER_4_ENGINE_STUDIO_C14/FEATURE_AGENTIC/FEATURE_PROMPTS/FEATURE_AUTONOMOUS_ATOM_REWRITE_PROMPT/autonomous_atom_rewrite.prompt.md`.
The trace models guidance provided by the prompt, not agent compliance, a tool call, or a Draft outcome. `draft_reported` names the guidance outcome; it does not assert that a Draft was reported.

```python
component_workflow(
    component='C55',
    action='autonomous_atom_rewrite',
    machine={
        'id': 'c55_autonomous_atom_rewrite',
        'initial': 'idle',
        'states': {
            'idle': {'on': {
                'rewrite_requested': {'target': 'source_guidance', 'guard': {'type': 'matchesTrace', 'params': {'kind': 'trigger'}}},
            }},
            'source_guidance': {'on': {
                'source_meaning_guided': {'target': 'uncertainty_guidance', 'guard': {'type': 'matchesTrace', 'params': {'kind': 'effect', 'target': 'source_meaning_guidance', 'outcome': 'provided'}}},
            }},
            'uncertainty_guidance': {'on': {
                'uncertainty_guided': {'target': 'report_guidance', 'guard': {'type': 'matchesTrace', 'params': {'kind': 'effect', 'target': 'uncertainty_guidance', 'outcome': 'required'}}},
            }},
            'report_guidance': {'on': {
                'draft_reported': {'target': 'done', 'guard': {'type': 'matchesTrace', 'params': {'kind': 'output', 'outcome': 'draft_reported'}}},
            }},
            'done': {'type': 'final'},
        },
    },
)
```

## Details

The prompt instructs the agent to read the complete input, exact source Atom and applicable model, including Role and Form requirements. It instructs the agent to preserve source meaning and applicability, including actors, conditions, exceptions, limits, sequences, references and formal or executable content, except for input-authorized changes.

Derive the Summary last and align the Main Subject. Before a Draft lifecycle call, compare candidate and source in both directions, correct issues and recheck. Follow the lifecycle result, preserve a required replacement relationship, and report each Draft and outcome.

For unresolved uncertainty, restore the smallest affected original passage and flag the passage and question to the Actor outside Atom prose. A preserved-content Draft may be created, but unresolved work must not be reported as conforming. Continue independent Atoms.

Group similar Main Subjects when useful, with distinct sources and scopes. Size batches to fit context. When a subagent nears its context limit, save completed results and assign unfinished Atoms with pinned sources and instructions to a fresh subagent.
