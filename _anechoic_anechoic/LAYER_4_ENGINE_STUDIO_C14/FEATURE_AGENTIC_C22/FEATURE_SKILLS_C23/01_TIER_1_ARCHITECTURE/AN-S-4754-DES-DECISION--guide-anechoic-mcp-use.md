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
  - AN-S-4753@1
state:
  status: active
  version: 1
  updated_at: '2026-11-24T00:00:00+00:00'
---

## Summary

Guide anechoic mcp use

## Claim

### Prose Claim

The ane skill instructs discovery, per-tool help, reuse of MCP selections, unchanged Project binding, and reporting unavailable tools or binding. It is guidance to the agent, not an MCP dispatcher.

### Formal Claim

Source coverage: `LAYER_4_ENGINE_STUDIO_C14/FEATURE_AGENTIC/FEATURE_SKILLS/ane/SKILL.md`.
The authored rule models only the named condition. It does not prove that
an agent complied or that a tool call occurred.

```lean
namespace AgenticC23Rule

def admitted (hasProjectRoot mcpUse : Bool) : Bool := hasProjectRoot && mcpUse

theorem admitted_requires_condition (hasProjectRoot mcpUse : Bool)
    (h : admitted hasProjectRoot mcpUse = true) : hasProjectRoot = true := by
  cases hasProjectRoot <;> simp_all [admitted]

end AgenticC23Rule
```
