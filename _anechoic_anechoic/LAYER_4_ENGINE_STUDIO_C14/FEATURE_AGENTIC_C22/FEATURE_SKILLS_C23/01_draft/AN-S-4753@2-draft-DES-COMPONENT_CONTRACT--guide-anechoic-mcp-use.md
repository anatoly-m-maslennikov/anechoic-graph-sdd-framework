---
atom_family: SPEC
atom_id: AN-S-4753
container:
  component: C23
tier: 0
context:
  template: component_contract
  lens: DES
relations:
  ANSWERS:
  - AN-S-3050
state:
  status: draft
  version: 2
  updated_at: '2026-11-25T10:52:38+00:00'
---

## Summary

Guide anechoic mcp use

## Guarantee

Guide an agent to use the host-configured ANECHOIC MCP with the explicit Project root and verify the result.

## Claim

### Prose Claim

The trace records the guidance supplied by the skill. It does not claim that an agent follows the guidance or performs an MCP operation. The carrier must not perform an MCP operation. The Contract does not express the order among guidance effects.

### Formal Claim

```python trace
declare_trace_contract(
    action='guided_anechoic_mcp_use',
    output='guidance_provided',
    must_effect=(('guidance.tools', 'discovery_required'), ('guidance.tool_help', 'reading_required'), ('guidance.project_binding', 'preservation_required'), ('guidance.mcp_operation', 'use_required'), ('guidance.result', 'verification_required'), ('guidance.blockers', 'reporting_required')),
    forbid_effect=('mcp_operation',),
)
```

## Details

Source coverage: `.agents/skills/ane/SKILL.md`. The skill instructs the agent to discover and select live MCP tools, read each tool's help before first use, trust results and reuse selections, pass the explicit Project root unchanged wherever accepted and reuse returned context, verify the returned result, and report unavailable MCP, tools, or Project binding. These are operator instructions, not claims of execution.
