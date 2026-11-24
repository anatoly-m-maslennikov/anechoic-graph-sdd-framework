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
  - AN-S-4747@1
state:
  status: active
  version: 1
  updated_at: '2026-11-24T00:00:00+00:00'
---

## Summary

Guide autonomous atom rewrite

## Claim

### Prose Claim

The prompt requires exact source and model reads, bidirectional comparison, correction and recheck. Unresolved uncertainty is flagged and must not be reported as conforming.

### Formal Claim

Source coverage: `LAYER_4_ENGINE_STUDIO_C14/FEATURE_AGENTIC/FEATURE_PROMPTS/FEATURE_AUTONOMOUS_ATOM_REWRITE_PROMPT/autonomous_atom_rewrite.prompt.md`.
The authored rule models only the named condition. It does not prove that
an agent complied or that a tool call occurred.

```lean
namespace AgenticC55Rule

def admitted (gatePassed draftCall : Bool) : Bool := gatePassed && draftCall

theorem admitted_requires_condition (gatePassed draftCall : Bool)
    (h : admitted gatePassed draftCall = true) : gatePassed = true := by
  cases gatePassed <;> simp_all [admitted]

end AgenticC55Rule
```
