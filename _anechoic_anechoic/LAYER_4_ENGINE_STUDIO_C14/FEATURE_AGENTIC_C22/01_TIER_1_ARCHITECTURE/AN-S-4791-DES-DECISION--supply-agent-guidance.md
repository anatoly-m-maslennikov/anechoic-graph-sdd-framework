---
atom_family: SPEC
atom_id: AN-S-4791
container:
  component: C22
tier: 1
context:
  template: decision
  lens: DES
relations:
  IS_SOLUTION_FOR:
  - AN-S-4790@1
state:
  status: active
  version: 1
  updated_at: '2026-11-24T00:00:00+00:00'
---

## Summary

Supply agent guidance

## Claim

### Prose Claim

Agentic guidance consists of the prompt and skill carriers in the realization tree. Their consumers select and interpret them. The carriers do not prove a tool call or result.

### Formal Claim

Source coverage: `LAYER_4_ENGINE_STUDIO_C14/FEATURE_AGENTIC/FEATURE_PROMPTS and FEATURE_AGENTIC/FEATURE_SKILLS`.
The authored rule models only the named condition. It does not prove that
an agent complied or that a tool call occurred.

```lean
namespace AgenticC22Rule

def admitted (hasCarrier guidance : Bool) : Bool := hasCarrier && guidance

theorem admitted_requires_condition (hasCarrier guidance : Bool)
    (h : admitted hasCarrier guidance = true) : hasCarrier = true := by
  cases hasCarrier <;> simp_all [admitted]

end AgenticC22Rule
```
