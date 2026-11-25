---
atom_family: SPEC
atom_id: AN-S-4745
container:
  component: C54
tier: 0
context:
  template: component_contract
  lens: DES
relations:
  ANSWERS:
  - AN-S-3061
state:
  status: draft
  version: 2
  updated_at: '2026-11-25T10:52:38+00:00'
---

## Summary

Guide atom authoring

## Guarantee

Guide creation or update of an Atom from Actor input, with source and model review and an internal gate before a Draft lifecycle call.

## Claim

### Prose Claim

For the modeled successful guidance path, the trace records guidance on source and model review, and the required internal gate before a Draft lifecycle call. The carrier does not read Actor input, call a lifecycle tool, write a Draft, or change carrier state.

### Formal Claim

```python trace
declare_trace_contract(
    action='guided_atom_update',
    output='draft_outcome_reported',
    must_effect=(('source_model_guidance', 'provided'), ('gate_guidance', 'required_before_draft_lifecycle')),
    forbid_effect=('actor_input', 'draft_lifecycle', 'draft_write', 'carrier_state'),
)
```

## Details

Source coverage: `LAYER_4_ENGINE_STUDIO_C14/FEATURE_AGENTIC/FEATURE_PROMPTS/FEATURE_ATOM_AUTHORING_PROMPT/atom_authoring.prompt.md`. This models an update with complete input and a resolved gate. Review of the lifecycle result means following that result; the prompt does not require an independent read-back. New-Atom missing input, uncertainty, replacement identity, batching, and detailed semantic preservation remain outside this trace.
