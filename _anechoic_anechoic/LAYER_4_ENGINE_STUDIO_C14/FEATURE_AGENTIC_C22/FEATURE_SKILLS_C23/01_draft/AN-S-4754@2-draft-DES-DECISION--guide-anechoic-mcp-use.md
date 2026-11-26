---
atom_family: SPEC
atom_id: AN-S-4754
container:
  component: C23
tier: 1
context:
  template: decision
  lens: DES
relations:
  IS_SOLUTION_FOR:
  - AN-S-4753@2-draft
state:
  status: draft
  version: 2
  updated_at: '2026-11-25T10:52:38+00:00'
---

## Summary

Guide anechoic mcp use

## Claim

### Prose Claim

The ane skill supplies instructions for MCP use. The modeled sequence records guidance effects, not agent compliance or tool operations. The carrier does not perform MCP operations.

### Formal Claim

```python
component_workflow(
    component='C23',
    action='guided_anechoic_mcp_use',
    machine={
        'id': 'guided_anechoic_mcp_use',
        'initial': 'idle',
        'states': {
            'idle': {'on': {'guidance_requested': {'target': 'step_0', 'guard': {'type': 'matchesTrace', 'params': {'kind': 'trigger'}}}}},
            'step_0': {'on': {'guidance_0': {'target': 'step_1', 'guard': {'type': 'matchesTrace', 'params': {'kind': 'effect', 'target': 'guidance.tools', 'outcome': 'discovery_required'}}}}},
            'step_1': {'on': {'guidance_1': {'target': 'step_2', 'guard': {'type': 'matchesTrace', 'params': {'kind': 'effect', 'target': 'guidance.tool_help', 'outcome': 'reading_required'}}}}},
            'step_2': {'on': {'guidance_2': {'target': 'step_3', 'guard': {'type': 'matchesTrace', 'params': {'kind': 'effect', 'target': 'guidance.project_binding', 'outcome': 'preservation_required'}}}}},
            'step_3': {'on': {'guidance_3': {'target': 'step_4', 'guard': {'type': 'matchesTrace', 'params': {'kind': 'effect', 'target': 'guidance.mcp_operation', 'outcome': 'use_required'}}}}},
            'step_4': {'on': {'guidance_4': {'target': 'step_5', 'guard': {'type': 'matchesTrace', 'params': {'kind': 'effect', 'target': 'guidance.result', 'outcome': 'verification_required'}}}}},
            'step_5': {'on': {'guidance_5': {'target': 'reporting', 'guard': {'type': 'matchesTrace', 'params': {'kind': 'effect', 'target': 'guidance.blockers', 'outcome': 'reporting_required'}}}}},
            'reporting': {'on': {'guidance_provided': {'target': 'done', 'guard': {'type': 'matchesTrace', 'params': {'kind': 'output', 'outcome': 'guidance_provided'}}}}},
            'done': {'type': 'final'},
        },
    },
)
```

## Details

Source coverage: `.agents/skills/ane/SKILL.md`. The skill instructs the agent to discover and select live MCP tools, read each tool's help before first use, trust results and reuse selections, pass the explicit Project root unchanged wherever accepted and reuse returned context, verify the returned result, and report unavailable MCP, tools, or Project binding. These are operator instructions, not claims of execution.
