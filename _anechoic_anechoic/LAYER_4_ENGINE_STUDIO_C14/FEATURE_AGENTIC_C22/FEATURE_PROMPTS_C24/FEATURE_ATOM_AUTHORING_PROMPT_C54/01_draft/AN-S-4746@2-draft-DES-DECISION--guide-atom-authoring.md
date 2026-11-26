---
atom_family: SPEC
atom_id: AN-S-4746
container:
  component: C54
tier: 1
context:
  template: decision
  lens: DES
relations:
  IS_SOLUTION_FOR:
  - AN-S-4745@2-draft
state:
  status: draft
  version: 2
  updated_at: '2026-11-25T10:52:38+00:00'
---

## Summary

Guide atom authoring

## Claim

### Prose Claim

The prompt instructs the agent to preserve meaning and applicability, derive Summary last, use the lifecycle result, and report unresolved uncertainty. Missing necessary input for a new Atom is a question to the Actor.

The modeled sequence covers one successful guided path. It describes the instructions, not actual execution or user or agent compliance.

### Formal Claim

```python
component_workflow(
    component='C54',
    action='guided_atom_update',
    machine={'id': 'guided_atom_update',
 'initial': 'idle',
 'states': {'idle': {'on': {'guidance_requested': {'target': 'source', 'guard': {'type': 'matchesTrace', 'params': {'kind': 'trigger'}}}}},
            'source': {'on': {'review_guidance': {'target': 'gate', 'guard': {'type': 'matchesTrace', 'params': {'kind': 'effect', 'target': 'source_model_guidance', 'outcome': 'provided'}}}}},
            'gate': {'on': {'gate_guidance': {'target': 'reporting', 'guard': {'type': 'matchesTrace', 'params': {'kind': 'effect', 'target': 'gate_guidance', 'outcome': 'required_before_draft_lifecycle'}}}}},
            'reporting': {'on': {'draft_outcome_reported': {'target': 'done', 'guard': {'type': 'matchesTrace', 'params': {'kind': 'output', 'outcome': 'draft_outcome_reported'}}}}},
            'done': {'type': 'final'}}},
)
```

## Details

Source coverage: `LAYER_4_ENGINE_STUDIO_C14/FEATURE_AGENTIC/FEATURE_PROMPTS/FEATURE_ATOM_AUTHORING_PROMPT/atom_authoring.prompt.md`. This models an update with complete input and a resolved gate. Review of the lifecycle result means following that result; the prompt does not require an independent read-back. New-Atom missing input, uncertainty, replacement identity, batching, and detailed semantic preservation remain outside this trace.
