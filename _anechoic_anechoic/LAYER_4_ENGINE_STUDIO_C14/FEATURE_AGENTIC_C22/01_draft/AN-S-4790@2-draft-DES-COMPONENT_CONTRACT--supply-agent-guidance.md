---
atom_family: SPEC
atom_id: AN-S-4790
container:
  component: C22
tier: 0
context:
  template: component_contract
  lens: DES
relations:
  ANSWERS:
  - AN-S-3043
state:
  status: draft
  version: 2
  updated_at: '2026-11-25T11:02:11.485674+00:00'
---

## Summary

Supply agent guidance

## Guarantee

Supply prompt and skill guidance for agent work. The guidance is consumed by an agent and does not itself execute an operation.

## Claim

### Prose Claim

A conceptual consumer handoff records that guidance is available before the agent receives it. The handoff itself must not execute an operation. It models neither agent compliance nor an execution interface.

### Formal Claim

```python trace
declare_trace_contract(
    action='consume_agent_guidance',
    output='guidance_received',
    must_effect=(('guidance', 'available'),),
    forbid_effect=('operation_execution',),
)
```

## Details

The Manifest delegates prompt guidance to C24 and skill guidance to C23. This abstract handoff does not assert a runtime, discovery mechanism, or actual agent behavior. The forbidden effect concerns the guidance handoff itself, not operations an agent may later perform.
